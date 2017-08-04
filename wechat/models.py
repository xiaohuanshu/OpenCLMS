from django.db import models


# Create your models here.

class Wechatkeyword(models.Model):
    keyword = models.CharField(max_length=255, blank=True, null=True)
    type = models.SmallIntegerField(blank=True, null=True)
    data = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'WechatKeyword'
