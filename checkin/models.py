from __future__ import unicode_literals

from django.db import models


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

    def __unicode__(self):
        return "%d %d" % (self.id, self.lesson.id)

    class Meta:
        db_table = 'Checkin'


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