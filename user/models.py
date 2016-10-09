# -*- coding: utf-8 -*-
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.core.cache import cache
from center.functional import classmethod_cache
from django.dispatch import receiver
from django.db.models.signals import post_save


# Create your models here.


class Role(models.Model):
    name = models.CharField(max_length=20, blank=True, null=True)
    permission = ArrayField(models.CharField(max_length=50), blank=True, default=[])

    def __unicode__(self):
        return u"%s" % (self.name)

    class Meta:
        db_table = 'Role'


class User(models.Model):
    username = models.CharField(max_length=20, blank=True, null=True)
    openid = models.CharField(max_length=28, blank=True, null=True)
    password = models.CharField(max_length=32, blank=True, null=True)
    sex = models.IntegerField(blank=True, null=True, default=1)
    ip = models.GenericIPAddressField(protocol='IPv4', blank=True, null=True)
    registertime = models.DateTimeField(blank=True, null=True)
    lastlogintime = models.DateTimeField(blank=True, null=True)
    email = models.CharField(max_length=40, blank=True, null=True)
    verify = models.NullBooleanField()
    role = models.ManyToManyField(Role, through='Usertorole', through_fields=('user', 'role'))
    avatar = models.ImageField(upload_to='avatar', default='avatar/default.png')

    @classmethod_cache
    def isteacher(self):
        return self.role.filter(name='教师').exists()

    @classmethod_cache
    def isstudent(self):
        return self.role.filter(name='学生').exists()

    def has_perm(self, permission):
        # permbool = Role.objects.filter(user=self,permission__contains=[permission]).exists()
        perm_cache = cache.get('perm_%d_cache' % self.id)
        if not perm_cache:
            perms_cache = []
            perms = list(Role.objects.filter(user=self).values_list('permission', flat=True))
            for p in perms:
                perms_cache = list(set(perms_cache).union(set(p)))
            cache.set('perm_%d_cache' % self.id, perms_cache, 86400)
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

    def updateavatarfromwechat(self):
        if self.openid is not None:
            from wechat.api import wechat
            userinfo = wechat.get_user_info(self.openid, lang='zh_CN')
            avatar_url = userinfo['headimgurl']
            from django.core.files import File
            from django.core.files.temp import NamedTemporaryFile
            import urllib2
            img_temp = NamedTemporaryFile(delete=True)
            img_temp.write(urllib2.urlopen(avatar_url).read())
            img_temp.flush()
            self.avatar.save('%s.jpeg' % self.openid, File(img_temp))

    def __unicode__(self):
        return u"%s" % (self.username)

    class Meta:
        db_table = 'User'


class Usertorole(models.Model):
    user = models.ForeignKey(User, models.DO_NOTHING, db_column='userid', blank=True, null=True)
    role = models.ForeignKey(Role, models.DO_NOTHING, db_column='roleid', blank=True, null=True)

    class Meta:
        db_table = 'UsertoRole'


@receiver(post_save, sender=Role)
def role_pre_save(sender, **kwargs):
    for user in kwargs['instance'].usertorole_set.values('user'):
        cache.delete('perm_%d_cache' % user['user'])


@receiver(post_save, sender=Usertorole)
def usertorole_pre_save(sender, **kwargs):
    cache.delete('perm_%d_cache' % kwargs['instance'].user.id)
