# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2020-04-14 01:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0011_auto_20180225_1231'),
    ]

    operations = [
        migrations.AlterField(
            model_name='homeworkcommit',
            name='submittime',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]