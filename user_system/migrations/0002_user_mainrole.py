# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-07 09:54
from __future__ import unicode_literals

from django.db import migrations, models


def add_mainrole(apps, schema_editor):
    User = apps.get_model("user_system", "User")
    Role = apps.get_model("user_system", "Role")
    db_alias = schema_editor.connection.alias

    teacherrole = Role.objects.using(db_alias).get(name=u'教师')
    studentrole = Role.objects.using(db_alias).get(name=u'学生')

    User.objects.using(db_alias).filter(role=teacherrole, mainrole=None).update(mainrole=u'教师')
    User.objects.using(db_alias).filter(role=studentrole, mainrole=None).update(mainrole=u'学生')


class Migration(migrations.Migration):
    dependencies = [
        ('user_system', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='mainrole',
            field=models.CharField(max_length=40, null=True),
        ),
        migrations.RunPython(add_mainrole),
    ]
