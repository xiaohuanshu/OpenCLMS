# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from school.function import getnowlessontime
from course.models import Lesson
from course.constant import *
from django.db.models import Q, F


class Command(BaseCommand):
    def handle(self, *args, **options):
        nowlessontime = getnowlessontime()
        week = nowlessontime['week']
        day = nowlessontime['day']
        time = nowlessontime['time']
        term = nowlessontime['term']
        unstoplessons = Lesson.objects.filter(term=term).filter(
            Q(week__lt=week) | Q(week=week, day__lt=day) | Q(week=week, day=day, time__gt=time - 1 - F('length')))
        unstoplessons.filter(status=LESSON_STATUS_NOW).update(status=LESSON_STATUS_END)
