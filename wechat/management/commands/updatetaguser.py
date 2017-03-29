# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.conf import settings
from wechat.client import wechat_client
from school.models import Student, Teacher, Class, Major, Administration
import logging

logger = logging.getLogger(__name__)


# 等分list
def splist(l, s):
    return [l[i:i + s] for i in range(len(l)) if i % s == 0]


class Command(BaseCommand):
    def handle(self, *args, **options):
        userlist = wechat_client.user.list(1, True)

        def getinfomation(id):
            for user in userlist:
                if user['extattr']['attrs'][0]['name'] == u"学工号":
                    thisuserworkid = user['extattr']['attrs'][0]['value']
                else:
                    thisuserworkid = user['extattr']['attrs'][1]['value']
                if thisuserworkid == id:
                    return user
            return None

        def update(tagid, newuserlist):
            oldlist = [user['userid'] for user in wechat_client.tag.get_users(tagid)['userlist']]
            deletelist = list(set(oldlist).difference(set(newuserlist)))
            newlist = list(set(newuserlist).difference(set(oldlist)))
            if len(deletelist) > 0:
                wechat_client.tag.delete_users(tagid, deletelist)
            for new in splist(newlist, 100):
                wechat_client.tag.add_users(tagid, new)

        taglist = wechat_client.tag.list()
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
        update(tagname_to_id[u'学生'], taguserlist)
        logger.info("[updatetaguser] Successful update tag user for student")
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
        update(tagname_to_id[u'教师'], taguserlist)
        logger.info("[updatetaguser] Successful update tag user for teacher")
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
            update(m.wechattagid, taguserlist)
        logger.info("[updatetaguser] Successful update tag user for major")
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
            update(a.wechattagtid, taguserlist)
        logger.info("[updatetaguser] Successful update tag user for administration")
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
            update(tagname_to_id[str(sy)], taguserlist)
        logger.info("[updatetaguser] Successful update tag user for major")
