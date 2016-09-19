from django.db import models


# Create your models here.
class Resourcejurisdiction(models.Model):
    name = models.CharField(max_length=20, blank=True, null=True)
    direction = models.CharField(max_length=20, blank=True, null=True)
    urlname = models.CharField(max_length=40, blank=True, null=True)
    parent = models.ForeignKey('self', models.DO_NOTHING, db_column='parentid', blank=True, null=True,
                               related_name="children")

    class Meta:
        db_table = 'ResourceJurisdiction'


class Roletoresourcejurisdiction(models.Model):
    role = models.ForeignKey('user.Role', models.DO_NOTHING, db_column='roleid', blank=True, null=True)
    resourcejurisdiction = models.ForeignKey(Resourcejurisdiction, models.DO_NOTHING,
                                               db_column='resourcejurisdictionid', blank=True, null=True)

    class Meta:
        db_table = 'RoletoResourceJurisdiction'
