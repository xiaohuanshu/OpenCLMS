# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.conf import settings
from wechat.client import wechat_client
from school.models import Student, Teacher
import json


class Command(BaseCommand):
    def handle(self, *args, **options):
        userlist = wechat_client.user.list(1, True)

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
        students = Student.objects.select_related('classid').all()
        for s in students:
            print s.studentid,
            userinfo = getinfomation(s.studentid)
            if userinfo:
                print 'exist'
                if userinfo['department'][0] != s.classid.wechatdepartmentid or getidnumber(userinfo)[
                                                                                -6:] != s.idnumber:
                    wechat_client.user.update(userinfo['userid'], department=[s.classid.wechatdepartmentid], extattr={
                        "attrs": [{"name": u"学工号", "value": s.studentid}, {"name": u"身份证号", "value": s.idnumber[-6:]}]})
            else:
                print 'create'
                wechat_client.user.create('S%s' % s.studentid, s.name, s.classid.wechatdepartmentid, u'学生',
                                          gender=s.sex,
                                          email='%s@gengdan.edu.cn' % s.studentid, extattr={
                        "attrs": [{"name": u"学工号", "value": s.studentid}, {"name": u"身份证号", "value": s.idnumber[-6:]}]})

        # for teacher
        teachers = Teacher.objects.all()
        for t in teachers:
            print t.teacherid,
            userinfo = getinfomation(t.teacherid)
            tdeps = [de.wechatdepartmentid for de in t.department.all()]

            if userinfo:
                print 'exist'
                if sorted(userinfo['department']) != sorted(tdeps) or getidnumber(userinfo)[
                                                                      -6:] != t.idnumber:
                    wechat_client.user.update(userinfo['userid'], department=tdeps, extattr={
                        "attrs": [{"name": u"学工号", "value": t.teacherid}, {"name": u"身份证号", "value": t.idnumber[-6:]}]})
            else:
                print 'create'
                wechat_client.user.create('T%s' % t.teacherid, t.name, tdeps, u'教师',
                                          gender=t.sex,
                                          email='%s@gengdan.edu.cn' % t.teacherid, extattr={
                        "attrs": [{"name": u"学工号", "value": t.teacherid}, {"name": u"身份证号", "value": t.idnumber[-6:]}]})
        print 'Successful!'
