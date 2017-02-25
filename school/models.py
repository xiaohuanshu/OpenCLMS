# Create your models here.
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from center.functional import classmethod_cache


class Administration(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    wechattagtid = models.SmallIntegerField(blank=True, null=True)

    def __unicode__(self):
        return u"%s" % (self.name)

    def teachernumber(self):
        return self.teacher_set.count()

    class Meta:
        db_table = 'Administration'


class Class(models.Model):
    department = models.ForeignKey('Department', models.DO_NOTHING, db_column='departmentid', blank=True, null=True)
    schoolyear = models.SmallIntegerField(blank=True, null=True)
    major = models.ForeignKey('Major', models.DO_NOTHING, db_column='majorid', blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    wechatdepartmentid = models.SmallIntegerField(blank=True, null=True)

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


class Classroom(models.Model):
    location = models.CharField(max_length=50, blank=True, null=True)
    seattype = models.ForeignKey('Seat', models.DO_NOTHING, db_column='seattype', blank=True, null=True)

    def __unicode__(self):
        return u"%s" % (self.location)

    class Meta:
        db_table = 'Classroom'


class Department(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    wechatdepartmentid = models.SmallIntegerField(blank=True, null=True)

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
    department = models.ForeignKey(Department, models.DO_NOTHING, db_column='departmentid', blank=True, null=True)
    name = models.CharField(max_length=50, blank=True, null=True)
    wechattagid = models.SmallIntegerField(blank=True, null=True)

    def __unicode__(self):
        return u"%s" % (self.name)

    @classmethod_cache
    def studentnumber(self):
        return self.student_set.count()

    @classmethod_cache
    def classamount(self):
        return self.class_set.count()

    class Meta:
        db_table = 'Major'


class Schoolterm(models.Model):
    schoolyear = models.IntegerField(blank=True, null=True)
    description = models.CharField(max_length=20, blank=True, null=True)
    now = models.NullBooleanField()
    startdate = models.DateField(blank=True, null=True)
    enddate = models.DateField(blank=True, null=True)

    def __unicode__(self):
        return u"%s" % (self.description)

    class Meta:
        db_table = 'SchoolTerm'


class Seat(models.Model):
    seattype = models.AutoField(primary_key=True)
    maxnumber = models.SmallIntegerField(blank=True, null=True)
    mapid = models.IntegerField(blank=True, null=True)

    def __unicode__(self):
        return "%d" % (self.seattype)

    class Meta:
        db_table = 'Seat'


class Student(models.Model):
    studentid = models.CharField(primary_key=True, max_length=11)
    idnumber = models.CharField(max_length=18, blank=True, null=True)
    name = models.CharField(max_length=20, blank=True, null=True)
    sex = models.SmallIntegerField(blank=True, null=True)

    classid = models.ForeignKey(Class, models.DO_NOTHING, db_column='classid', blank=True,
                                null=True)  # can't name to class

    department = models.ForeignKey(Department, models.DO_NOTHING, db_column='departmentid', blank=True, null=True)
    major = models.ForeignKey(Major, models.DO_NOTHING, db_column='majorid', blank=True, null=True)
    user = models.ForeignKey('user.User', models.DO_NOTHING, db_column='userid', blank=True, null=True)
    available = models.BooleanField(default=True)

    def __unicode__(self):
        return u"%s" % (self.name)

    class Meta:
        db_table = 'Student'


class Teacher(models.Model):
    teacherid = models.CharField(primary_key=True, max_length=8)
    name = models.CharField(max_length=20, blank=True, null=True)
    sex = models.SmallIntegerField(blank=True, null=True)
    idnumber = models.CharField(max_length=18, blank=True, null=True)
    user = models.ForeignKey('user.User', models.DO_NOTHING, db_column='userid', blank=True, null=True)
    administration = models.ManyToManyField(Administration, through='Teachertoadministration',
                                            through_fields=('teacher', 'administration'))
    department = models.ManyToManyField(Department, through='Teachertodepartment',
                                        through_fields=('teacher', 'department'))
    available = models.BooleanField(default=True)

    def __unicode__(self):
        return u"%s" % (self.name)

    class Meta:
        db_table = 'Teacher'


class Teachertoadministration(models.Model):
    teacher = models.ForeignKey(Teacher, models.DO_NOTHING, db_column='teacherid', blank=True, null=True)
    administration = models.ForeignKey(Administration, models.DO_NOTHING, db_column='administrationid', blank=True,
                                       null=True)

    class Meta:
        db_table = 'TeachertoAdministration'
        index_together = ["teacher", "administration"]


class Teachertodepartment(models.Model):
    teacher = models.ForeignKey(Teacher, models.DO_NOTHING, db_column='teacherid', blank=True, null=True)
    department = models.ForeignKey(Department, models.DO_NOTHING, db_column='departmentid', blank=True, null=True)

    class Meta:
        db_table = 'TeachertoDepartment'
        index_together = ["teacher", "department"]


@receiver(post_save, sender=Schoolterm)
def schoolterm_pre_save(sender, **kwargs):
    cache.delete_many(['currentschoolyearterm', 'termdata', 'schoolyeardata'])


@receiver(post_save, sender=Classtime)
def classtime_pre_save(sender, **kwargs):
    cache.delete('classtimedata')
