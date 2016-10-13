# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from school.function import getnowlessontime
from course.models import Lesson
from course.constant import *
from django.db.models import Q, F


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('before', type=str)

    def handle(self, *args, **options):
        nowlessontime = getnowlessontime()
        week = nowlessontime['week']
        day = nowlessontime['day']
        time = nowlessontime['time']
        term = nowlessontime['term']
        qs = {
            'today': Q(week=week, day=day, time__lt=time - 1 - F('length')),
            'week': Q(week=week, day__lt=day),
            'term': Q(week__lt=week)
        }
        qbefore={
            'today': qs['today'],# stop lessons in today
            'week': qs['today'] | qs['week'],#stop lessons in this week
            'all': qs['today'] | qs['term'] | qs['week']#stop lesson in this term
        }
        unstoplessons = Lesson.objects.filter(term=term).filter(qbefore[options['before']])
        unstoplessons.filter(status=LESSON_STATUS_NOW).update(status=LESSON_STATUS_END)
