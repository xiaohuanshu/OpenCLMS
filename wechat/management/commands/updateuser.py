# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.conf import settings
from wechat.contact import contact_helper
from school.models import Student, Teacher
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
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

        def getidnumber(user):
            for item in user['extattr']['attrs']:
                if item['name'] == u"验证码":
                    return item['value']

        # print json.dumps(userlist, encoding='utf-8', ensure_ascii=False)

        create_list = []

        # for student
        students = Student.objects.select_related('classid').filter(available=True).all()
        for s in students:
            userinfo = getinfomation(s.studentid)
            if s.classid:
                s_depid = s.classid.wechatdepartmentid
            else:
                s_depid = 1
            if userinfo:
                existcount += 1
                if userinfo['department'][0] != s_depid or getidnumber(userinfo) != s.idnumber[-6:]:
                    logger.debug("%s update" % s.studentid)
                    updatecount += 1
                    contact_helper.user.update(userinfo['userid'], department=[s_depid], extattr={
                        "attrs": [{"name": u"学工号", "value": s.studentid}, {"name": u"验证码", "value": s.idnumber[-6:]}]})
                else:
                    logger.debug("%s exist" % s.studentid)
                userlist.remove(userinfo)
            else:
                create_list.append(dict(user_id='S%s' % s.studentid, name=s.name,
                                        department=s_depid, position=u'学生',
                                        gender=s.sex,
                                        email='%s@%s' % (s.studentid, settings.SCHOOLEMAIL),
                                        extattr={"attrs": [{"name": u"学工号", "value": s.studentid},
                                                           {"name": u"验证码", "value": s.idnumber[-6:]}]}))

        # for teacher
        teachers = Teacher.objects.filter(available=True).exclude(name__regex='.*\d+.*').all()
        for t in teachers:
            userinfo = getinfomation(t.teacherid)
            tdeps = [de.wechatdepartmentid for de in t.department.all()]

            if userinfo:
                existcount += 1
                if sorted(userinfo['department']) != sorted(tdeps) or getidnumber(userinfo) != t.idnumber[-6:]:
                    logger.debug("%s update" % t.teacherid)
                    updatecount += 1
                    contact_helper.user.update(userinfo['userid'], department=tdeps,
                                               extattr={"attrs": [{"name": u"学工号", "value": t.teacherid},
                                                                  {"name": u"验证码", "value": t.idnumber[-6:]}]})
                else:
                    logger.debug("%s exist" % t.teacherid)
                userlist.remove(userinfo)
            else:
                create_list.append(dict(user_id='T%s' % t.teacherid, name=t.name, department=tdeps, position=u'教师',
                                        gender=t.sex,
                                        email='%s@gengdan.edu.cn' % t.teacherid,
                                        extattr={"attrs": [{"name": u"学工号", "value": t.teacherid},
                                                           {"name": u"验证码", "value": t.idnumber[-6:]}]}))

        # delete
        for user in userlist:
            logger.debug("%s delete" % user['userid'])
            deletecount += 1
            contact_helper.user.delete(user['userid'])

        # create
        for c in create_list:
            logger.debug("%s create" % c['user_id'])
            createcount += 1
            contact_helper.user.create(**c)
        logger.info("[updateuser] Successful exist:%d update:%d create:%d delete:%d" % (
            existcount, updatecount, createcount, deletecount))
