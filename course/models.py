# -*- coding: utf-8 -*-
from django.db import models
import datetime
from school.function import getTermDate, getClassTime
from school.models import Classroom
from constant import *
from django.db.models import ObjectDoesNotExist, Q, F
import time
from function import getweek, gettime, getday, t, splitlesson, simplifytime
from center.functional import classmethod_cache


# Create your models here.


class Course(models.Model):
    serialnumber = models.CharField(max_length=50, blank=True, null=True)
    number = models.SmallIntegerField(blank=True, null=True)
    title = models.CharField(max_length=100, blank=True, null=True)
    teacher = models.ForeignKey('school.Teacher', models.DO_NOTHING, db_column='teacherid', blank=True, null=True)
    time = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    schoolterm = models.CharField(max_length=20, blank=True, null=True)
    major = models.ForeignKey('school.Major', models.DO_NOTHING, db_column='majorid', blank=True, null=True)
    department = models.ForeignKey('school.Department', models.DO_NOTHING, db_column='departmentid', blank=True,
                                   null=True)

    @classmethod_cache
    def lastlessontime(self):
        lessondata = Lesson.objects.filter(course=self).order_by('-starttime').all()[:1]
        if lessondata[0].starttime:
            return lessondata[0].starttime
        else:
            return None

    @classmethod_cache
    def status(self):
        try:
            lessondata = Lesson.objects.filter(course=self, status=LESSON_STATUS_NOW).get()
        except ObjectDoesNotExist:
            return 0
        return 1

    @classmethod_cache
    def progress(self):
        lessoncount = Lesson.objects.filter(course=self).count()
        lessonallreadycount = Lesson.objects.filter(course=self, status=LESSON_STATUS_END).count()
        return "%d" % ((lessonallreadycount / (lessoncount * 1.0)) * 100)

    def simplifytime(self):
        self.time, self.location = simplifytime(self.time, self.location)
        self.save()

    def generatelesson(self):
        count = 0
        Lesson.objects.filter(course=self, status=LESSON_STATUS_AWAIT).delete()
        time = self.time
        location = self.location
        term = self.schoolterm
        for ele in splitlesson(time, location):
            try:
                locationid = Classroom.objects.get(location=ele['location'])
            except ObjectDoesNotExist:
                return -1
            if not Lesson.objects.filter(course=self.id, time=ele['time'], term=term,
                                         week=ele['week'], day=ele['day'], length=ele['length'],
                                         classroom=locationid.id).exists():
                p = Lesson()
                p.course = self
                p.classroom = locationid
                p.length = ele['length']
                p.status = LESSON_STATUS_AWAIT
                p.term = term
                p.week = ele['week']
                p.time = ele['time']
                p.day = ele['day']
                p.save()
                count = count + 1
        return count

    def __unicode__(self):
        return u"%s" % (self.title)

    class Meta:
        db_table = 'Course'


class Lesson(models.Model):
    course = models.ForeignKey(Course, models.DO_NOTHING, db_column='courseid', blank=True, null=True)
    classroom = models.ForeignKey('school.Classroom', models.DO_NOTHING, db_column='classroomid', blank=True, null=True)
    length = models.SmallIntegerField(blank=True, null=True)
    status = models.SmallIntegerField(blank=True, null=True)
    year = models.SmallIntegerField(blank=True, null=True)
    term = models.CharField(max_length=20, blank=True, null=True)
    week = models.SmallIntegerField(blank=True, null=True)
    time = models.SmallIntegerField(blank=True, null=True)
    day = models.SmallIntegerField(blank=True, null=True)
    starttime = models.DateTimeField(blank=True, null=True)
    endtime = models.DateTimeField(blank=True, null=True)
    checkincount = models.SmallIntegerField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)

    @classmethod_cache
    def getTime(self):
        # allowcheckinbeforetime = 10
        classtime = getClassTime()
        termtime = getTermDate(self.term)
        thistermtime = datetime.datetime.strptime(str(termtime[0]), '%Y-%m-%d')
        dayplus = (self.week - 1) * 7 + self.day
        thistermtime = thistermtime + datetime.timedelta(days=dayplus)
        coursestarttime = datetime.datetime.strptime(str(classtime[self.time][0]), '%H:%M:%S')
        courseendtime = datetime.datetime.strptime(str(classtime[self.time + self.length - 1][1]), '%H:%M:%S')
        starttime = thistermtime + datetime.timedelta(hours=coursestarttime.hour, minutes=coursestarttime.minute,
                                                      seconds=coursestarttime.second)
        endtime = thistermtime + datetime.timedelta(hours=courseendtime.hour, minutes=courseendtime.minute,
                                                    seconds=courseendtime.second)
        # allowstarttime = starttime - datetime.timedelta(minutes=allowcheckinbeforetime)
        return [starttime.timetuple(), endtime.timetuple()]

    @classmethod_cache
    def shouldnumber(self):
        from checkin.models import Checkin
        shouldnumber = Studentcourse.objects.filter(course=self.course).count()
        leavenumber = Checkin.objects.filter(lesson=self, status__gt=10).count()
        # TODO leavenumver counter
        return shouldnumber - leavenumber

    @classmethod_cache
    def actuallynumber(self):
        from checkin.models import Checkin
        from checkin.constant import CHECKIN_STATUS_EARLY, CHECKIN_STATUS_SUCCESS, CHECKIN_STATUS_LATE, \
            CHECKIN_STATUS_LATEEARLY
        checkindata = Checkin.objects.filter(lesson=self)
        realnumber = checkindata.filter(
            Q(status=CHECKIN_STATUS_EARLY) | Q(status=CHECKIN_STATUS_SUCCESS) | Q(status=CHECKIN_STATUS_LATE) | Q(
                status=CHECKIN_STATUS_LATEEARLY)).count()
        return realnumber

    @classmethod_cache
    def asknumber(self):
        from checkin.models import Checkin
        checkindata = Checkin.objects.filter(lesson=self)
        asknumber = checkindata.filter(status__gt=10).count()
        return asknumber

    @classmethod_cache
    def notreachnumber(self):
        from checkin.models import Checkin
        from checkin.constant import CHECKIN_STATUS_NORMAL
        checkindata = Checkin.objects.filter(lesson=self)
        notreach = checkindata.filter(status=CHECKIN_STATUS_NORMAL).count()
        return notreach

    def startlesson(self):
        if self.course.status() != 0:
            return {'error': 101, 'message': u'课程时间冲突'}
        if self.status != LESSON_STATUS_AWAIT:
            return {'error': 101, 'message': u'课程不能开启'}
        nowtime = time.localtime()
        self.starttime = time.strftime('%Y-%m-%d %H:%M:%S', nowtime)
        self.status = LESSON_STATUS_NOW
        self.save()

        # for checkin
        from checkin.models import Checkin, Ask
        from checkin.constant import CHECKIN_STATUS_NORMAL, ASK_STATUS_APPROVE, CHECKIN_STATUS_PRIVATE_ASK, \
            CHECKIN_STATUS_PUBLIC_ASK
        nowstudent = Checkin.objects.filter(lesson=self).values_list('student', flat=True)
        studentcourse = Studentcourse.objects.filter(course=self.course).exclude(student__in=nowstudent).all()
        newstudent = []
        for s in studentcourse:
            newstudent.append(
                Checkin(lesson=self, status=CHECKIN_STATUS_NORMAL, student=s.student))
        Checkin.objects.bulk_create(newstudent)
        students = Checkin.objects.filter(lesson=self).values_list('student', flat=True)
        starttime, endtime = self.getTime()
        starttime = time.strftime('%Y-%m-%d %H:%M:%S', starttime)
        endtime = time.strftime('%Y-%m-%d %H:%M:%S', endtime)
        askstudents_private = Ask.objects.filter(student__in=students, status=ASK_STATUS_APPROVE,
                                                 type=CHECKIN_STATUS_PRIVATE_ASK).filter(
            Q(starttime__lte=starttime, endtime__gte=starttime) | Q(starttime__lte=endtime, endtime__gte=endtime) | Q(
                starttime__gte=starttime, endtime__lte=endtime)).values_list('student', flat=True)
        askstudents_public = Ask.objects.filter(student__in=students, status=ASK_STATUS_APPROVE,
                                                type=CHECKIN_STATUS_PUBLIC_ASK).filter(
            Q(starttime__lte=starttime, endtime__gte=starttime) | Q(starttime__lte=endtime, endtime__gte=endtime) | Q(
                starttime__gte=starttime, endtime__lte=endtime)).values_list('student', flat=True)
        Checkin.objects.filter(lesson=self, student__in=askstudents_private).update(laststatus=F('status'),
                                                                                    status=CHECKIN_STATUS_PRIVATE_ASK)
        Checkin.objects.filter(lesson=self, student__in=askstudents_public).update(laststatus=F('status'),
                                                                                   status=CHECKIN_STATUS_PUBLIC_ASK)
        return {'error': 0, 'message': u'课程成功开启', 'newstatus': self.status,
                'starttime': time.strftime('%Y-%m-%d %H:%M:%S', nowtime)}

    def stoplesson(self):
        if self.status != LESSON_STATUS_NOW:
            return {'error': 101, 'message': u'现在不能结束'}
        nowtime = time.localtime()
        self.endtime = time.strftime('%Y-%m-%d %H:%M:%S', nowtime)
        self.status = LESSON_STATUS_END
        self.save()
        return {'error': 0, 'message': u'课程已结束', 'newstatus': self.status,
                'endtime': time.strftime('%Y-%m-%d %H:%M:%S', nowtime)}

    def cleardata(self):
        self.status = LESSON_STATUS_AWAIT
        self.starttime = None
        self.endtime = None
        self.save()
        return {'error': 0, 'message': u'成功清除', 'newstatus': self.status,
                'endtime': u'没有数据'}

    @classmethod_cache
    def isnow(self):
        if self.status == LESSON_STATUS_NOW or self.status == LESSON_STATUS_CHECKIN or self.status == LESSON_STATUS_CHECKIN_ADD or self.status == LESSON_STATUS_CHECKIN_AGAIN:
            return True
        else:
            return False

    def isend(self):
        if self.status == LESSON_STATUS_CANCLE or self.status == LESSON_STATUS_END or self.status == LESSON_STATUS_END_EARLY:
            return True
        else:
            return False

    @classmethod_cache
    def ischeckinnow(self):
        if self.status == LESSON_STATUS_CHECKIN or self.status == LESSON_STATUS_CHECKIN_ADD or self.status == LESSON_STATUS_CHECKIN_AGAIN:
            return True
        else:
            return False

    def __unicode__(self):
        return "%d %s-%d-%d-%d-%d" % (self.id, self.term, self.year, self.week, self.day, self.time)

    class Meta:
        db_table = 'Lesson'


class Studentcourse(models.Model):
    student = models.ForeignKey('school.Student', models.DO_NOTHING, db_column='studentid', blank=True, null=True)
    course = models.ForeignKey(Course, models.DO_NOTHING, db_column='courseid', blank=True, null=True,
                               related_name='courses')

    class Meta:
        db_table = 'StudentCourse'
