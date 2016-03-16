from django.db import models

# Create your models here.


class Role(models.Model):
    name = models.CharField(max_length=20, blank=True, null=True)

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
