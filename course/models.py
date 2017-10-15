# -*- coding: utf-8 -*-
from django.db import models
import datetime
from school.function import getTermDate, getClassTime
from school.models import Classroom
from constant import *
from checkin.constant import *
from checkin.models import Checkin, Asktostudent, Ask
from django.db.models import ObjectDoesNotExist, Q, F
import time
from function import getweek, gettime, getday, t, splitlesson, simplifytime
from django.utils.functional import cached_property
from django.conf import settings
import os.path
from django.utils.http import urlquote
from center.models import Filemodel, Dealbase64imgmodel
import logging

logger = logging.getLogger(__name__)


# Create your models here.


class Course(models.Model):
    serialnumber = models.CharField(max_length=50, unique=True)
    number = models.SmallIntegerField(blank=True, null=True)
    title = models.CharField(max_length=100, blank=True, null=True)
    teachers = models.ManyToManyField('school.Teacher')
    time = models.CharField(max_length=400, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    schoolterm = models.CharField(max_length=20)
    major = models.ForeignKey('school.Major', models.SET_NULL, db_column='majorid', null=True)
    department = models.ForeignKey('school.Department', models.SET_NULL, db_column='departmentid', null=True)
    teachclass = models.ForeignKey('school.Class', models.SET_NULL, db_column='teachclassid', null=True)
    disable_sync = models.BooleanField(default=False)
    exempt_students = models.ManyToManyField('school.Student')

    def gettitlewithclass(self):
        if self.teachclass:
            return "%s(%s)" % (self.title, self.teachclass.name)
        else:
            return self.title

    @cached_property
    def lastlessontime(self):
        lessondata = Lesson.objects.filter(course=self).order_by('-starttime').all()[:1]
        if len(lessondata) == 0:
            return None
        if lessondata[0].starttime:
            return lessondata[0].starttime
        else:
            return None

    @cached_property
    def status(self):
        return Lesson.objects.filter(course=self,
                                     status__in=[LESSON_STATUS_NOW, LESSON_STATUS_CHECKIN, LESSON_STATUS_CHECKIN_ADD,
                                                 LESSON_STATUS_CHECKIN_AGAIN]).exists()

    @cached_property
    def progress(self):
        lessoncount = Lesson.objects.filter(course=self).count()
        if lessoncount == 0:
            return "0"
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
    course = models.ForeignKey(Course, models.CASCADE, db_column='courseid')
    classroom = models.ForeignKey('school.Classroom', models.SET_NULL, db_column='classroomid', blank=True, null=True)
    length = models.SmallIntegerField()
    status = models.SmallIntegerField(default=LESSON_STATUS_AWAIT)
    term = models.CharField(max_length=20)
    week = models.SmallIntegerField()
    time = models.SmallIntegerField()
    day = models.SmallIntegerField()
    starttime = models.DateTimeField(null=True)
    endtime = models.DateTimeField(null=True)
    checkincount = models.SmallIntegerField(null=True)

    @cached_property
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

    @cached_property
    def shouldnumber(self):
        shouldnumber = Studentcourse.objects.filter(course=self.course).count()
        leavenumber = self.asknumber
        return shouldnumber - leavenumber

    @cached_property
    def actuallynumber(self):
        checkindata = Checkin.objects.filter(lesson=self)
        realnumber = checkindata.filter(
            Q(status=CHECKIN_STATUS_EARLY) | Q(status=CHECKIN_STATUS_SUCCESS) | Q(status=CHECKIN_STATUS_LATE) | Q(
                status=CHECKIN_STATUS_LATEEARLY)).count()
        return realnumber

    @cached_property
    def asknumber(self):
        if self.isnow() or self.isend():
            checkindata = Checkin.objects.filter(lesson=self)
            asknumber = checkindata.filter(status__gt=10).count()
        else:
            starttime, endtime = self.getTime()
            starttime = time.strftime('%Y-%m-%d %H:%M:%S', starttime)
            endtime = time.strftime('%Y-%m-%d %H:%M:%S', endtime)
            students = Studentcourse.objects.filter(course=self.course).values_list('student', flat=True)
            asks = Ask.objects.filter(student__in=students, status=ASK_STATUS_APPROVE).filter(
                Q(starttime__lte=starttime, endtime__gte=starttime) | Q(starttime__lte=endtime,
                                                                        endtime__gte=endtime) | Q(
                    starttime__gte=starttime, endtime__lte=endtime))
            asknumber = Asktostudent.objects.filter(ask__in=asks).count()
        return asknumber

    @cached_property
    def notreachnumber(self):
        from checkin.models import Checkin
        checkindata = Checkin.objects.filter(lesson=self)
        notreach = checkindata.filter(status=CHECKIN_STATUS_NORMAL).count()
        return notreach

    def startlesson(self):
        if self.course.status != 0:
            return {'error': 101, 'message': u'课程时间冲突'}
        if self.status not in (LESSON_STATUS_AWAIT, LESSON_STATUS_NEW_AWAIT):
            return {'error': 101, 'message': u'课程不能开启'}
        nowtime = time.localtime()
        self.starttime = time.strftime('%Y-%m-%d %H:%M:%S', nowtime)
        self.status = LESSON_STATUS_NOW
        self.save()

        # for checkin
        nowstudent = Checkin.objects.filter(lesson=self).values_list('student', flat=True)
        studentcourse = Studentcourse.objects.filter(course=self.course).exclude(student__in=nowstudent).all()
        newstudent = []
        for s in studentcourse:
            newstudent.append(
                Checkin(lesson=self, status=CHECKIN_STATUS_SUCCESS, student=s.student))
        Checkin.objects.bulk_create(newstudent)
        students = Checkin.objects.filter(lesson=self).values_list('student', flat=True)
        starttime, endtime = self.getTime
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
        logger.info('lesson %d start' % self.id)
        return {'error': 0, 'message': u'课程成功开启', 'newstatus': self.status,
                'starttime': time.strftime('%Y-%m-%d %H:%M:%S', nowtime)}

    def stoplesson(self):
        if self.status != LESSON_STATUS_NOW:
            return {'error': 101, 'message': u'现在不能结束'}
        nowtime = time.localtime()
        self.endtime = time.strftime('%Y-%m-%d %H:%M:%S', nowtime)
        self.status = LESSON_STATUS_END
        self.save()
        logger.info('lesson %d stoped' % self.id)
        return {'error': 0, 'message': u'课程已结束', 'newstatus': self.status,
                'endtime': time.strftime('%Y-%m-%d %H:%M:%S', nowtime)}

    def transfertime(self, time):  # time is dict {week,day,time}
        if self.status == LESSON_STATUS_TRANSFERRED:
            return {'error': 101, 'message': u'该课程已被转移'}
        if self.isnow() or self.isend():
            return {'error': 101, 'message': u'已开启课程不能转移'}
        if Lesson.objects.filter(course=self.course, **time).exclude(status=LESSON_STATUS_TRANSFERRED).exists():
            return {'error': 101, 'message': u'该课程在该时间段有课'}
        newlesson = None
        if self.status == LESSON_STATUS_AWAIT:
            newlesson = Lesson.objects.create(course=self.course, classroom=self.classroom, length=self.length,
                                              term=self.term, status=LESSON_STATUS_NEW_AWAIT, **time)
            self.status = LESSON_STATUS_TRANSFERRED
            self.save()
        elif self.status == LESSON_STATUS_NEW_AWAIT:
            self.time = time['time']
            self.week = time['week']
            self.day = time['day']
            self.save()
            newlesson = self

        return {'error': 0, 'message': u'时间已转移', 'newlessonid': newlesson.id}

    def cleardata(self):
        self.status = LESSON_STATUS_AWAIT
        self.starttime = None
        self.endtime = None
        self.checkinrecord_set.all().delete()
        self.checkin_set.all().delete()
        self.checkincount = 0
        self.save()
        logger.info('lesson %d cleared' % self.id)
        return {'error': 0, 'message': u'成功清除', 'newstatus': self.status,
                'endtime': u'没有数据'}

    def isnow(self):  # include checkin
        if self.status in (LESSON_STATUS_NOW, LESSON_STATUS_CHECKIN,
                           LESSON_STATUS_CHECKIN_ADD, LESSON_STATUS_CHECKIN_AGAIN):
            return True
        else:
            return False

    def isend(self):
        if self.status == LESSON_STATUS_END or self.status == LESSON_STATUS_END_EARLY:
            return True
        else:
            return False

    def ischeckinnow(self):
        if self.status in (LESSON_STATUS_CHECKIN, LESSON_STATUS_CHECKIN_ADD, LESSON_STATUS_CHECKIN_AGAIN):
            return True
        else:
            return False

    def __unicode__(self):
        return "Lesson:%d" % self.id

    class Meta:
        db_table = 'Lesson'


class Studentcourse(models.Model):
    student = models.ForeignKey('school.Student', models.CASCADE, db_column='studentid')
    course = models.ForeignKey(Course, models.CASCADE, db_column='courseid', related_name='courses')

    class Meta:
        db_table = 'StudentCourse'
        unique_together = ["student", "course"]


def get_courseresource_path(instance, filename):
    return 'courseresource/%d/%s' % (instance.course.id, filename)


class Courseresource(Filemodel):
    course = models.ForeignKey(Course, models.CASCADE, db_column='courseid')
    title = models.CharField(max_length=100, blank=True, null=True)
    uploadtime = models.DateTimeField(auto_now=True)
    # downloadcount = models.SmallIntegerField(default=0)
    file = models.FileField(upload_to=get_courseresource_path)

    class Meta:
        db_table = 'CourseResource'


class Homeworkfile(Filemodel):
    title = models.CharField(max_length=100, blank=True, null=True)
    file = models.FileField(upload_to='homeworkfile')

    class Meta:
        db_table = 'HomeworkFile'


class Coursehomework(Dealbase64imgmodel):
    course = models.ForeignKey(Course, models.CASCADE, db_column='courseid')
    title = models.CharField(max_length=100, blank=True, null=True)
    instruction = models.TextField(blank=True, null=True)
    type = models.SmallIntegerField(blank=True)
    deadline = models.DateTimeField(blank=True, null=True)
    weight = models.SmallIntegerField(blank=True)
    attachment = models.ManyToManyField(Homeworkfile)

    base64img_contained_fields = ('instruction',)

    def commitnumber(self):
        return Homeworkcommit.objects.filter(coursehomework=self).count()

    def commitprogress(self):
        coursenumber = Studentcourse.objects.filter(course=self.course).count()
        return 100.0 * self.commitnumber() / coursenumber

    def isend(self):
        return self.deadline < datetime.datetime.now()

    class Meta:
        db_table = 'CourseHomework'


class Homeworkcommit(Dealbase64imgmodel):
    coursehomework = models.ForeignKey(Coursehomework, models.CASCADE, db_column='coursehomeworkid')
    student = models.ForeignKey('school.Student', models.CASCADE, db_column='studentid')
    submittime = models.DateTimeField(auto_now=True)
    text = models.TextField(blank=True, null=True)
    attachment = models.ManyToManyField(Homeworkfile)
    score = models.SmallIntegerField(blank=True, null=True)

    base64img_contained_fields = ('text',)

    class Meta:
        unique_together = ["coursehomework", "student"]
        db_table = 'HomeworkCommit'
