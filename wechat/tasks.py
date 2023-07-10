# -*- coding: utf-8 -*-
# Create your tasks here
from celery import shared_task
from django.conf import settings
from wechat.client import wechat_client
from user_system.models import User
from school.models import Student, Class, Department, Teacher, Major, Administration
from wechat.contact import contact_helper
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.db.models import Q
from urllib import request
import logging
import datetime

logger = logging.getLogger(__name__)


@shared_task(name='update_avatar_from_wechat')
def update_avatar_from_wechat():
    counter = 0
    student_avaliable = Student.objects.filter(available=True).values_list('user', flat=True)
    teacher_avaliable = Student.objects.filter(available=True).values_list('user', flat=True)
    users = User.objects.filter(Q(id__in=student_avaliable) | Q(id__in=teacher_avaliable)).exclude(openid=None).all()
    for u in users:
        counter += 1
        try:
            userinfo = wechat_client.user.get(u.openid)
        except:
            continue
        if 'avatar' not in userinfo:
            continue
        avatar_url = userinfo['avatar']
        if not avatar_url:
            continue
        img_temp = NamedTemporaryFile(delete=True)
        try:
            img_temp.write(request.urlopen(avatar_url).read())
        except:
            logger.exception("download %s avatar error" % avatar_url)
        img_temp.flush()
        if u.avatar != 'avatar/default.png':
            u.avatar.delete()
        u.avatar.save('%s.jpeg' % u.openid, File(img_temp))
    logger.info("[update_avatar_from_wechat]successful update %d avatar" % counter)
    return counter


@shared_task(name='send_birthday_blessing')
def send_birthday_blessing():
    counter = 0
    todate = datetime.datetime.now().strftime('%m%d')
    students = Student.objects.select_related('user').exclude(user__openid=None) \
        .extra(where=['substring("idnumber",11,4) = \'%s\'' % (todate)]).all()
    for s in students:
        counter += 1
        message = u"%s同学，生日快乐哦！祝你有美好的一天~" % s.name
        wechat_client.message.send_text(agent_id=settings.AGENTID, user_ids=[s.user.openid], content=message)
    logger.info("[send_birthday_blessing]successful send %d students" % counter)
    return counter


@shared_task(name='sync_wechat')
def sync_wechat(continuous=None):
    """
    同步过程：部门->用户(学生->教师)->标签->标签用户
    """

    # 部门
    departmentlist = contact_helper.department.get()

    for dep in Department.objects.filter(wechatdepartmentid=None).all():
        exist = False
        for d in departmentlist:
            if dep.name == d['name']:
                exist = True
                break
        if not exist:
            depid = contact_helper.department.create(dep.name, 1)['id']
            dep.wechatdepartmentid = depid
            dep.save()
            logger.info("[sync_wechat] add department %s" % dep.name)
    departmentlist = contact_helper.department.get()
    for dep in departmentlist:
        if dep['parentid'] == 1:
            thisdepartmentid = dep['id']
            thisdepartment = Department.objects.get(name=dep['name'])
            cls = Class.objects.filter(department=thisdepartment).all()
            for c in cls:
                exist = False
                for d in departmentlist:
                    if c.name == d['name']:
                        exist = True
                        break
                if not exist:
                    depid = contact_helper.department.create(c.name, thisdepartmentid)['id']
                    c.wechatdepartmentid = depid
                    c.save()
                    logger.info("[sync_wechat] add department %s" % c.name)

    # (用户)学生-教师
    userlist = contact_helper.user.list(1, True)
    deletecount = 0
    updatecount = 0
    existcount = 0
    createcount = 0

    def getinfomation(id):
        for user in userlist:
            for item in user['extattr']['attrs']:
                if item['name'] == u"学工号":
                    thisuserworkid = item['value']
                    break
            if thisuserworkid == id:
                return user
        return None

    def getverifycode(user):
        for item in user['extattr']['attrs']:
            if item['name'] == u"验证码":
                return item['value']

    create_list = []

    # for student
    students = Student.objects.select_related('classid').filter(available=True).all()
    for s in students:
        userinfo = getinfomation(s.studentid)
        if s.classid:
            s_depid = s.classid.wechatdepartmentid
        else:
            s_depid = 1
        email = s.user.email or '%s@%s' % (s.studentid, settings.SCHOOLEMAIL)
        mobile = s.user.phone or ''
        if userinfo:
            existcount += 1
            if userinfo['department'][0] != s_depid or getverifycode(userinfo) != s.idnumber[-6:] or userinfo[
                'email'] != email or (mobile != '' and userinfo['mobile'] != mobile):
                logger.debug("%s update" % s.studentid)
                updatecount += 1
                contact_helper.user.update(userinfo['userid'], department=[s_depid], email=email, mobile=mobile,
                                           extattr={
                                               "attrs": [{"name": u"学工号", "value": s.studentid},
                                                         {"name": u"验证码", "value": s.idnumber[-6:]}]})
            else:
                logger.debug("%s exist" % s.studentid)
            userlist.remove(userinfo)
        else:
            create_list.append(dict(user_id='S%s' % s.studentid, name=s.name,
                                    department=s_depid, position=u'学生',
                                    gender=s.sex,
                                    email=email,
                                    mobile=mobile,
                                    extattr={"attrs": [{"name": u"学工号", "value": s.studentid},
                                                       {"name": u"验证码", "value": s.idnumber[-6:]}]}))

    # for teacher
    teachers = Teacher.objects.filter(available=True).exclude(name__regex='.*\d+.*').all()
    for t in teachers:
        userinfo = getinfomation(t.teacherid)
        tdeps = [de.wechatdepartmentid for de in t.department.all()]
        email = t.user.email or '%s@%s' % (t.teacherid, settings.SCHOOLEMAIL)
        mobile = t.user.phone or ''

        if userinfo:
            existcount += 1
            if sorted(userinfo['department']) != sorted(tdeps) or getverifycode(userinfo) != t.idnumber[-6:] or \
                    userinfo['email'] != email or (mobile != '' and userinfo['mobile'] != mobile):
                logger.debug("%s update" % t.teacherid)
                updatecount += 1
                contact_helper.user.update(userinfo['userid'], department=tdeps, email=email, mobile=mobile,
                                           extattr={"attrs": [{"name": u"学工号", "value": t.teacherid},
                                                              {"name": u"验证码", "value": t.idnumber[-6:]}]})
            else:
                logger.debug("%s exist" % t.teacherid)
            userlist.remove(userinfo)
        else:
            create_list.append(dict(user_id='T%s' % t.teacherid, name=t.name, department=tdeps, position=u'教师',
                                    gender=t.sex,
                                    email=email,
                                    mobile=mobile,
                                    extattr={"attrs": [{"name": u"学工号", "value": t.teacherid},
                                                       {"name": u"验证码", "value": t.idnumber[-6:]}]}))

    # delete
    for user in userlist:
        if user['userid'][0] not in ('T', 'S'):
            continue  # T和S开头的不要删除
        logger.debug("%s delete" % user['userid'])
        deletecount += 1
        contact_helper.user.delete(user['userid'])

    # create
    for c in create_list:
        logger.debug("%s create" % c['user_id'])
        createcount += 1
        contact_helper.user.create(**c)
    logger.info("[sync_wechat]User Finished exist:%d update:%d create:%d delete:%d" % (
        existcount, updatecount, createcount, deletecount))

    # 标签

    taglist = contact_helper.tag.list()
    taglist = [t['tagname'] for t in taglist]
    if u'学生' not in taglist:
        contact_helper.tag.create(u'学生')
    if u'教师' not in taglist:
        contact_helper.tag.create(u'教师')
    # for schoolyear
    schoolyears = Class.objects.distinct('schoolyear').only('schoolyear')
    for s in schoolyears:
        if str(s.schoolyear) not in taglist:
            contact_helper.tag.create(s.schoolyear)
    # for major
    majors = Major.objects.all()
    for m in majors:
        if m.name not in taglist:
            contact_helper.tag.create(m.name)

    # for administration
    administrations = Administration.objects.all()
    for a in administrations:
        if a.name not in taglist:
            contact_helper.tag.create(a.name)

    logger.info("[sync_wechat] Update tag Finished")

    # 标签用户
    userlist = contact_helper.user.list(1, True)

    # 等分list
    def splist(l, s):
        return [l[i:i + s] for i in range(len(l)) if i % s == 0]

    def tag_update(tagid, newuserlist):
        oldlist = [user['userid'] for user in contact_helper.tag.get_users(tagid)['userlist']]
        deletelist = list(set(oldlist).difference(set(newuserlist)))
        newlist = list(set(newuserlist).difference(set(oldlist)))
        if len(deletelist) > 0:
            contact_helper.tag.delete_users(tagid, deletelist)
        for new in splist(newlist, 100):
            contact_helper.tag.add_users(tagid, new)

    taglist = contact_helper.tag.list()
    tagname_to_id = {}
    for t in taglist:
        tagname_to_id[t['tagname']] = t['tagid']

    # for student
    students = Student.objects.filter(available=True).only('studentid').all()
    taguserlist = []
    for s in students:
        userinfo = getinfomation(s.studentid)
        if userinfo:
            thiswechatuserid = userinfo['userid']
        else:
            thiswechatuserid = 'S%s' % s.studentid
        taguserlist.append(thiswechatuserid)
    tag_update(tagname_to_id[u'学生'], taguserlist)
    logger.info("[sync_wechat] Finished Tag user for student")
    # for teacher
    teachers = Teacher.objects.filter(available=True).exclude(name__regex='.*\d+.*').only('teacherid').all()
    taguserlist = []
    for t in teachers:
        userinfo = getinfomation(t.teacherid)
        if userinfo:
            thiswechatuserid = userinfo['userid']

        else:
            thiswechatuserid = 'T%s' % t.teacherid
        taguserlist.append(thiswechatuserid)
    tag_update(tagname_to_id[u'教师'], taguserlist)
    logger.info("[sync_wechat] Finished Tag user for teacher")
    # for major
    majors = Major.objects.all()
    for m in majors:
        students = Student.objects.filter(available=True, major=m).only('studentid').all()
        taguserlist = []
        for s in students:
            userinfo = getinfomation(s.studentid)
            if userinfo:
                thiswechatuserid = userinfo['userid']
            else:
                thiswechatuserid = 'S%s' % s.studentid
            taguserlist.append(thiswechatuserid)
        tag_update(tagname_to_id[m.name], taguserlist)
    logger.info("[sync_wechat] Finished Tag user for major")
    # for administration
    administrations = Administration.objects.all()
    for a in administrations:
        teachers = Teacher.objects.filter(available=True, administration=a).exclude(name__regex='.*\d+.*').only(
            'teacherid').all()
        taguserlist = []
        for t in teachers:
            userinfo = getinfomation(t.teacherid)
            if userinfo:
                thiswechatuserid = userinfo['userid']

            else:
                thiswechatuserid = 'T%s' % t.teacherid
            taguserlist.append(thiswechatuserid)
        tag_update(tagname_to_id[a.name], taguserlist)
    logger.info("[sync_wechat] Finished Tag user for administration")
    # for school year
    schoolyears = Class.objects.distinct('schoolyear').only('schoolyear')
    schoolyears = [cl.schoolyear for cl in schoolyears]
    for sy in schoolyears:
        students = Student.objects.filter(available=True, classid__schoolyear=sy).only('studentid').all()
        taguserlist = []
        for s in students:
            userinfo = getinfomation(s.studentid)
            if userinfo:
                thiswechatuserid = userinfo['userid']
            else:
                thiswechatuserid = 'S%s' % s.studentid
            taguserlist.append(thiswechatuserid)
        tag_update(tagname_to_id[str(sy)], taguserlist)
    logger.info("[sync_wechat] Finished Tag user for schoolyear")

    logger.info("[sync_wechat] All Finished")


@shared_task(name='sync_wechat_user')
def sync_wechat_user(user_id):
    """
    用户修改信息(Email、Phone)后，立刻异步向微信更新
    """

    user = User.objects.get(id=user_id)
    if user.openid:
        openid = user.openid
    elif user.isstudent:
        openid = 'S%s' % user.academiccode
    elif user.isteacher:
        openid = 'T%s' % user.academiccode

    contact_helper.user.update(openid, email=user.email, mobile=user.phone)

    logger.info("[sync_wechat_user] %s Finished" % openid)
