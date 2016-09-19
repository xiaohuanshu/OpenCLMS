from django.db import models

# Create your models here.

class Wechatkeyword(models.Model):
    keyword = models.CharField(max_length=255, blank=True, null=True)
    type = models.SmallIntegerField(blank=True, null=True)
    data = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'WechatKeyword'


class Wechatuser(models.Model):
    openid = models.CharField(primary_key=True, max_length=28)
    nickname = models.CharField(max_length=16, blank=True, null=True)
    sex = models.SmallIntegerField(blank=True, null=True)
    city = models.CharField(max_length=10, blank=True, null=True)
    country = models.CharField(max_length=10, blank=True, null=True)
    province = models.CharField(max_length=10, blank=True, null=True)
    headimgurl = models.TextField(blank=True, null=True)
    subscribe_time = models.DateTimeField(blank=True, null=True)
    lastpositiontime = models.DateTimeField(blank=True, null=True)
    unsubscribe = models.NullBooleanField()
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    accuracy = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = 'WechatUser'