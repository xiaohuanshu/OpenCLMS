# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.conf import settings
from wechat.client import wechat_client
from school.models import Student, Teacher
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        userlist = wechat_client.user.list(1, True)
        deletecount = 0
        updatecount = 0
        existcount = 0
        createcount = 0

        def getinfomation(id):
            for user in userlist:
                # print json.dumps(user, encoding='utf-8', ensure_ascii=False)
                if user['extattr']['attrs'][0]['name'] == u"学工号":
                    thisuserworkid = user['extattr']['attrs'][0]['value']
                else:
                    thisuserworkid = user['extattr']['attrs'][1]['value']
                if thisuserworkid == id:
                    return user
            return None

        def getidnumber(user):
            if user['extattr']['attrs'][0]['name'] == u"身份证号":
                return user['extattr']['attrs'][0]['value']
            else:
                return user['extattr']['attrs'][1]['value']

        # print json.dumps(userlist, encoding='utf-8', ensure_ascii=False)

        # for student
        students = Student.objects.select_related('classid').filter(available=True).all()
        for s in students:
            userinfo = getinfomation(s.studentid)
            if userinfo:
                existcount += 1
                if userinfo['department'][0] != s.classid.wechatdepartmentid or getidnumber(userinfo) != s.idnumber[
                                                                                                         -6:]:
                    logger.debug("%s update" % s.studentid)
                    updatecount += 1
                    wechat_client.user.update(userinfo['userid'], department=[s.classid.wechatdepartmentid], extattr={
                        "attrs": [{"name": u"学工号", "value": s.studentid}, {"name": u"身份证号", "value": s.idnumber[-6:]}]})
                else:
                    logger.debug("%s exist" % s.studentid)
                userlist.remove(userinfo)
            else:
                logger.debug("%s create" % s.studentid)
                createcount += 1
                wechat_client.user.create('S%s' % s.studentid, s.name, s.classid.wechatdepartmentid, u'学生',
                                          gender=s.sex,
                                          email='%s@%s' % (s.studentid, settings.SCHOOLEMAIL),
                                          extattr={"attrs": [{"name": u"学工号", "value": s.studentid},
                                                             {"name": u"身份证号", "value": s.idnumber[-6:]}]})

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
                    wechat_client.user.update(userinfo['userid'], department=tdeps,
                                              extattr={"attrs": [{"name": u"学工号", "value": t.teacherid},
                                                                 {"name": u"身份证号", "value": t.idnumber[-6:]}]})
                else:
                    logger.debug("%s exist" % t.teacherid)
                userlist.remove(userinfo)
            else:
                logger.debug("%s create" % t.teacherid)
                createcount += 1
                wechat_client.user.create('T%s' % t.teacherid, t.name, tdeps, u'教师',
                                          gender=t.sex,
                                          email='%s@gengdan.edu.cn' % t.teacherid,
                                          extattr={"attrs": [{"name": u"学工号", "value": t.teacherid},
                                                             {"name": u"身份证号", "value": t.idnumber[-6:]}]})

        # delete
        for user in userlist:
            logger.debug("%s delete" % user['userid'])
            deletecount += 1
            wechat_client.user.delete(user['userid'])
        logger.info("[updateuser] Successful exist:%d update:%d create:%d delete:%d" % (
            existcount, updatecount, createcount, deletecount))
