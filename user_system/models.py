# -*- coding: utf-8 -*-
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.core.cache import cache
from django.utils.functional import cached_property
from django.dispatch import receiver
from django.db.models.signals import post_save


# Create your models here.

class Role(models.Model):
    name = models.CharField(max_length=20)
    permission = ArrayField(models.CharField(max_length=50), blank=True, default=[])

    def __unicode__(self):
        return u"%s" % (self.name)

    class Meta:
        db_table = 'Role'


class User(models.Model):
    username = models.CharField(max_length=20, null=True, unique=True)
    academiccode = models.CharField(max_length=20, null=True, unique=True)
    openid = models.CharField(max_length=28, null=True, unique=True)
    wechatdeviceid = models.CharField(max_length=32, null=True)
    password = models.CharField(max_length=32)
    sex = models.IntegerField(blank=True, null=True, default=1)
    ip = models.GenericIPAddressField(protocol='ipv4', null=True)
    lastlogintime = models.DateTimeField(null=True)
    email = models.CharField(max_length=40, null=True, unique=True)
    phone = models.CharField(max_length=20, null=True, unique=True)
    role = models.ManyToManyField(Role, through='Usertorole', through_fields=('user', 'role'))
    avatar = models.ImageField(upload_to='avatar', default='avatar/default.png')
    checkinaccountabnormal = models.BooleanField(default=False)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    accuracy = models.FloatField(null=True)
    lastpositiontime = models.DateTimeField(null=True)
    mainrole = models.CharField(max_length=40, null=True)

    @cached_property
    def isteacher(self):
        return self.mainrole == u'教师'

    @cached_property
    def isstudent(self):
        return self.mainrole == u'学生'

    def has_perm(self, permission):
        # permbool = Role.objects.filter(user=self,permission__contains=[permission]).exists()
        perm_cache = cache.get('perm_%d_cache' % self.id)
        if not perm_cache:
            perm_cache = []
            perms = list(Role.objects.filter(user=self).values_list('permission', flat=True))
            for p in perms:
                perm_cache = list(set(perm_cache).union(set(p)))
            cache.set('perm_%d_cache' % self.id, perm_cache, 86400)
        if type(permission) == list:
            for p in permission:
                if p in perm_cache:
                    return True
            return False
        else:
            if permission in perm_cache:
                return True
            else:
                return False

    def __unicode__(self):
        return u"%s" % (self.username)

    class Meta:
        db_table = 'User'


class Usertorole(models.Model):
    user = models.ForeignKey(User, models.CASCADE, db_column='userid')
    role = models.ForeignKey(Role, models.CASCADE, db_column='roleid')

    class Meta:
        db_table = 'UsertoRole'
        unique_together = ["user", "role"]


@receiver(post_save, sender=Role)
def role_post_save(sender, **kwargs):
    for user in kwargs['instance'].usertorole_set.values('user'):
        cache.delete('perm_%d_cache' % user['user'])


@receiver(post_save, sender=Usertorole)
def usertorole_post_save(sender, **kwargs):
    cache.delete('perm_%d_cache' % kwargs['instance'].user.id)
