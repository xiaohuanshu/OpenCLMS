from __future__ import unicode_literals

from django.db import models
from constant import *


# Create your models here.


class Checkin(models.Model):
    lesson = models.ForeignKey('course.Lesson', models.DO_NOTHING, db_column='lessonid', blank=True, null=True)
    student = models.ForeignKey('school.Student', models.DO_NOTHING, db_column='studentid', blank=True, null=True)
    seat = models.IntegerField(blank=True, null=True, db_column='seatid')
    status = models.SmallIntegerField(blank=True, null=True)
    laststatus = models.SmallIntegerField(blank=True, null=True)
    time = models.DateTimeField(blank=True, null=True)
    positionaccuracy = models.FloatField(blank=True, null=True)
    positionlatitude = models.FloatField(blank=True, null=True)
    positionlongitude = models.FloatField(blank=True, null=True)
    method = models.SmallIntegerField(blank=True, null=True)
    abnormal = models.SmallIntegerField(blank=True, null=True)

    def __unicode__(self):
        return "%d %d" % (self.id, self.lesson.id)

    class Meta:
        db_table = 'Checkin'
        unique_together = ["lesson", "student"]


class Checkinrecord(models.Model):
    lesson = models.ForeignKey('course.Lesson', models.DO_NOTHING, db_column='lessonid', blank=True, null=True)
    starttime = models.DateTimeField(blank=True, null=True)
    endtime = models.DateTimeField(blank=True, null=True)
    shouldnumber = models.SmallIntegerField(blank=True, null=True)
    actuallynumber = models.SmallIntegerField(blank=True, null=True)
    newnumber = models.SmallIntegerField(blank=True, null=True)
    leavenumber = models.SmallIntegerField(blank=True, null=True)
    status = models.SmallIntegerField(blank=True, null=True)
    time = models.SmallIntegerField(blank=True, null=True)

    def __unicode__(self):
        return "%d %d" % (self.id, self.lesson.id)

    class Meta:
        db_table = 'CheckinRecord'


class Ask(models.Model):
    schoolterm = models.CharField(max_length=20, blank=True, null=True)
    starttime = models.DateTimeField(blank=True, null=True)
    endtime = models.DateTimeField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    reason = models.CharField(max_length=100, blank=True, null=True)
    student = models.ForeignKey('school.Student', models.DO_NOTHING, db_column='studentid', blank=True, null=True)
    operater = models.ForeignKey('user.User', models.DO_NOTHING, db_column='operater', blank=True, null=True)
    type = models.IntegerField(blank=True, null=True)
    student = models.ManyToManyField('school.Student', through='Asktostudent',
                                     through_fields=('ask', 'student'))

    class Meta:
        db_table = 'Ask'


class Asktostudent(models.Model):
    student = models.ForeignKey('school.Student', models.DO_NOTHING, db_column='studentid', blank=True, null=True)
    ask = models.ForeignKey(Ask, models.DO_NOTHING, db_column='askid', blank=True, null=True)

    class Meta:
        db_table = 'AsktoStudent'
        unique_together = ["student", "ask"]


class Scoreregulation(models.Model):
    course = models.ForeignKey('course.Course', models.DO_NOTHING, db_column='courseid', blank=True, null=True)
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
