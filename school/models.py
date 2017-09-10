# -*- coding: utf-8 -*-
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.cache import cache
from django.utils.functional import cached_property
import hashlib


class Administration(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return u"%s" % (self.name)

    def teachernumber(self):
        return self.teacher_set.count()

    class Meta:
        db_table = 'Administration'


class Class(models.Model):
    department = models.ForeignKey('Department', models.SET_NULL, db_column='departmentid', null=True)
    schoolyear = models.SmallIntegerField(null=True)
    major = models.ForeignKey('Major', models.SET_NULL, db_column='majorid', null=True)
    name = models.CharField(max_length=255)
    wechatdepartmentid = models.SmallIntegerField(null=True)

    def __unicode__(self):
        return u"%s" % (self.name)

    class Meta:
        db_table = 'Class'


class Classtime(models.Model):
    id = models.IntegerField(primary_key=True)
    starttime = models.TimeField(blank=True, null=True)
    endtime = models.TimeField(blank=True, null=True)

    class Meta:
        db_table = 'ClassTime'


@receiver(post_save, sender=Classtime)
def classtime_post_save(sender, **kwargs):
    cache.delete('classtimedata')


class Classroom(models.Model):
    location = models.CharField(max_length=50)
    seattype = models.ForeignKey('Seat', models.SET_NULL, db_column='seattype', null=True)

    def __unicode__(self):
        return u"%s" % (self.location)

    class Meta:
        db_table = 'Classroom'


class Department(models.Model):
    name = models.CharField(max_length=50)
    wechatdepartmentid = models.SmallIntegerField(null=True)

    def majoramount(self):
        return self.major_set.count()

    def studentnumber(self):
        return self.student_set.count()

    def teachernumber(self):
        return self.teacher_set.count()

    def __unicode__(self):
        return u"%s" % (self.name)

    class Meta:
        db_table = 'Department'


class Major(models.Model):
    department = models.ForeignKey(Department, models.SET_NULL, db_column='departmentid', null=True)
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return u"%s" % (self.name)

    @cached_property
    def studentnumber(self):
        return self.student_set.count()

    @cached_property
    def classamount(self):
        return self.class_set.count()

    class Meta:
        db_table = 'Major'


class Schoolterm(models.Model):
    schoolyear = models.IntegerField()
    description = models.CharField(max_length=20)
    now = models.NullBooleanField()
    startdate = models.DateField()
    enddate = models.DateField()

    def __unicode__(self):
        return u"%s" % (self.description)

    class Meta:
        db_table = 'SchoolTerm'


@receiver(post_save, sender=Schoolterm)
def schoolterm_post_save(sender, **kwargs):
    cache.delete_many(['currentschoolyearterm', 'termdata', 'schoolyeardata'])


class Seat(models.Model):
    seattype = models.AutoField(primary_key=True)
    maxnumber = models.SmallIntegerField(null=True)
    mapid = models.IntegerField(null=True)

    def __unicode__(self):
        return "%d" % self.seattype

    class Meta:
        db_table = 'Seat'


class Student(models.Model):
    studentid = models.CharField(primary_key=True, max_length=11)
    idnumber = models.CharField(max_length=18, null=True)
    name = models.CharField(max_length=20)
    sex = models.SmallIntegerField(null=True)

    classid = models.ForeignKey(Class, models.SET_NULL, db_column='classid', null=True)  # can't name to class

    department = models.ForeignKey(Department, models.SET_NULL, db_column='departmentid', null=True)
    major = models.ForeignKey(Major, models.SET_NULL, db_column='majorid', null=True)
    user = models.ForeignKey('user.User', models.PROTECT, db_column='userid', null=True)
    available = models.BooleanField(default=True)

    def generateuser(self, save=True):
        if self.user is None and self.idnumber is not None:
            from user.models import User, Role, Usertorole
            studentrole = Role.objects.get(name=u'学生')
            m = hashlib.md5()
            m.update(self.idnumber)
            password = m.hexdigest()
            self.user = User.objects.create(academiccode=self.studentid, password=password, sex=self.sex,
                                            mainrole=u'学生')
            Usertorole.objects.create(user=self.user, role=studentrole)
            if save:
                self.save()
        return self.user

    def __unicode__(self):
        return u"%s" % (self.name)

    class Meta:
        db_table = 'Student'


@receiver(pre_save, sender=Student)
def student_pre_save(sender, instance, **kwargs):
    instance.generateuser(save=False)


class Teacher(models.Model):
    teacherid = models.CharField(primary_key=True, max_length=8)
    name = models.CharField(max_length=20)
    sex = models.SmallIntegerField(null=True)
    idnumber = models.CharField(max_length=18, null=True)
    user = models.ForeignKey('user.User', models.PROTECT, db_column='userid', null=True)
    administration = models.ManyToManyField(Administration, through='Teachertoadministration',
                                            through_fields=('teacher', 'administration'))
    department = models.ManyToManyField(Department, through='Teachertodepartment',
                                        through_fields=('teacher', 'department'))
    available = models.BooleanField(default=True)

    def generateuser(self, save=True):
        if self.user is None and self.idnumber is not None:
            from user.models import User, Role, Usertorole
            teacherrole = Role.objects.get(name=u'教师')
            m = hashlib.md5()
            m.update(self.idnumber)
            password = m.hexdigest()
            self.user = User.objects.create(academiccode=self.teacherid, password=password, sex=self.sex,
                                            mainrole=u'教师')
            Usertorole.objects.create(user=self.user, role=teacherrole)
            if save:
                self.save()
        return self.user

    def __unicode__(self):
        return u"%s" % (self.name)

    class Meta:
        db_table = 'Teacher'


@receiver(pre_save, sender=Teacher)
def teacher_pre_save(sender, instance, **kwargs):
    instance.generateuser(save=False)


class Teachertoadministration(models.Model):
    teacher = models.ForeignKey(Teacher, models.CASCADE, db_column='teacherid')
    administration = models.ForeignKey(Administration, models.CASCADE, db_column='administrationid')

    class Meta:
        db_table = 'TeachertoAdministration'
        index_together = ["teacher", "administration"]


class Teachertodepartment(models.Model):
    teacher = models.ForeignKey(Teacher, models.CASCADE, db_column='teacherid')
    department = models.ForeignKey(Department, models.CASCADE, db_column='departmentid')

    class Meta:
        db_table = 'TeachertoDepartment'
        unique_together = ["teacher", "department"]
