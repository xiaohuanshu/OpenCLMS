from __future__ import unicode_literals

from django.db import models
from constant import *


# Create your models here.


class Checkin(models.Model):
    lesson = models.ForeignKey('course.Lesson', models.CASCADE, db_column='lessonid')
    student = models.ForeignKey('school.Student', models.CASCADE, db_column='studentid')
    seat = models.IntegerField(blank=True, null=True, db_column='seatid')
    status = models.SmallIntegerField(default=CHECKIN_STATUS_NORMAL)
    laststatus = models.SmallIntegerField(null=True)
    time = models.DateTimeField(null=True)
    positionaccuracy = models.FloatField(null=True)
    positionlatitude = models.FloatField(null=True)
    positionlongitude = models.FloatField(null=True)
    method = models.SmallIntegerField(null=True)
    abnormal = models.SmallIntegerField(null=True)

    def __unicode__(self):
        return "%d %d" % (self.id, self.lesson.id)

    class Meta:
        db_table = 'Checkin'
        unique_together = ["lesson", "student"]


class Checkinrecord(models.Model):
    lesson = models.ForeignKey('course.Lesson', models.CASCADE, db_column='lessonid')
    starttime = models.DateTimeField(null=True)
    endtime = models.DateTimeField(null=True)
    shouldnumber = models.SmallIntegerField(null=True)
    actuallynumber = models.SmallIntegerField(null=True)
    newnumber = models.SmallIntegerField(null=True)
    leavenumber = models.SmallIntegerField(null=True)
    status = models.SmallIntegerField(null=True)
    time = models.SmallIntegerField()

    def __unicode__(self):
        return "%d %d" % (self.id, self.lesson.id)

    class Meta:
        db_table = 'CheckinRecord'


class Ask(models.Model):
    schoolterm = models.CharField(max_length=20)
    starttime = models.DateTimeField(null=True)
    endtime = models.DateTimeField(null=True)
    status = models.IntegerField(default=ASK_STATUS_WAITING)
    reason = models.CharField(max_length=100, blank=True, null=True)
    operater = models.ForeignKey('user.User', models.SET_NULL, db_column='operater', null=True)
    type = models.IntegerField(null=True)
    student = models.ManyToManyField('school.Student', through='Asktostudent', through_fields=('ask', 'student'))

    class Meta:
        db_table = 'Ask'


class Asktostudent(models.Model):
    student = models.ForeignKey('school.Student', models.CASCADE, db_column='studentid')
    ask = models.ForeignKey(Ask, models.CASCADE, db_column='askid')

    class Meta:
        db_table = 'AsktoStudent'
        unique_together = ["student", "ask"]


class Scoreregulation(models.Model):
    course = models.ForeignKey('course.Course', models.CASCADE, db_column='courseid')
    normal = models.IntegerField(default=0)
    success = models.IntegerField(default=100)
    early = models.IntegerField(default=30)
    lateearly = models.IntegerField(default=0)
    late = models.IntegerField(default=70)
    private_ask = models.IntegerField(default=70)
    public_ask = models.IntegerField(default=95)

    def getscore(self, status):
        if status == CHECKIN_STATUS_NORMAL:
            return self.normal
        elif status == CHECKIN_STATUS_SUCCESS:
            return self.success
        elif status == CHECKIN_STATUS_EARLY:
            return self.early
        elif status == CHECKIN_STATUS_LATEEARLY:
            return self.lateearly
        elif status == CHECKIN_STATUS_LATE:
            return self.late
        elif status == CHECKIN_STATUS_PRIVATE_ASK:
            return self.private_ask
        elif status == CHECKIN_STATUS_PUBLIC_ASK:
            return self.public_ask
        else:
            return 0

    class Meta:
        db_table = 'ScoreRegulation'
