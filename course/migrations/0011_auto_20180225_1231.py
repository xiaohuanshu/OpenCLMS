# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-02-25 12:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0010_homeworkcommit_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='homeworkfile',
            name='file',
            field=models.FileField(max_length=255, upload_to=b'homeworkfile/%Y/%m/%d/'),
        ),
    ]
