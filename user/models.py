# -*- coding: utf-8 -*-
from django.db import models
from center.functional import classmethod_cache


# Create your models here.


class Role(models.Model):
    name = models.CharField(max_length=20, blank=True, null=True)
    resourcejurisdiction = models.ManyToManyField('rbac.Resourcejurisdiction',
                                                  through='rbac.Roletoresourcejurisdiction',
                                                  through_fields=('role', 'resourcejurisdiction'))

    def __unicode__(self):
        return u"%s" % (self.name)

    class Meta:
        managed = False
        db_table = 'Role'


class User(models.Model):
    username = models.CharField(max_length=20, blank=True, null=True)
    openid = models.CharField(max_length=28, blank=True, null=True)
    password = models.CharField(max_length=32, blank=True, null=True)
    sex = models.IntegerField(blank=True, null=True)
    ip = models.TextField(blank=True, null=True)  # This field type is a guess.
    registertime = models.DateTimeField(blank=True, null=True)
    lastlogintime = models.DateTimeField(blank=True, null=True)
    email = models.CharField(max_length=40, blank=True, null=True)
    verify = models.NullBooleanField()
    role = models.ManyToManyField(Role, through='Usertorole', through_fields=('user', 'role'))

    @classmethod_cache
    def isteacher(self):
        return self.role.filter(name='教师').exists()

    @classmethod_cache
    def isstudent(self):
        return self.role.filter(name='学生').exists()

    def hasresourcejurisdiction(self, jurisdiction):
        from rbac.auth import is_user_has_resourcejurisdiction
        return is_user_has_resourcejurisdiction(self, jurisdiction)

    def __unicode__(self):
        return u"%s" % (self.username)

    class Meta:
        managed = False
        db_table = 'User'


class Usertorole(models.Model):
    user = models.ForeignKey(User, models.DO_NOTHING, db_column='userid', blank=True, null=True)
    role = models.ForeignKey(Role, models.DO_NOTHING, db_column='roleid', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'UsertoRole'
