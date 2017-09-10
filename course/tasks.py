# Create your tasks here
# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from celery import shared_task

from school.function import getnowlessontime
from course.models import Lesson
from course.constant import LESSON_STATUS_NOW, LESSON_STATUS_END
from django.db.models import Q, F
import logging

logger = logging.getLogger(__name__)


@shared_task(name='auto_stop_lesson')
def auto_stop_lesson(before):
    nowlessontime = getnowlessontime()
    week = nowlessontime['week']
    day = nowlessontime['day']
    time = nowlessontime['time']
    term = nowlessontime['term']
    qs = {
        'today': Q(week=week, day=day, time__lt=time + 1 - F('length')),
        # 上课时间 + 课程长度 - 1 < 现在时间   =>  上课时间 < 现在时间 + 1 - 课程长度
        'week': Q(week=week, day__lt=day),
        'term': Q(week__lt=week)
    }
    qbefore = {
        'today': qs['today'],  # stop lessons in today
        'week': qs['today'] | qs['week'],  # stop lessons in this week
        'all': qs['today'] | qs['term'] | qs['week']  # stop lesson in this term
    }
    unstoplessons = Lesson.objects.filter(term=term).filter(qbefore[before])
    count = unstoplessons.filter(status=LESSON_STATUS_NOW).update(status=LESSON_STATUS_END)
    if count:
        logger.info('autostop %d lessons this %s' % (count, before))
    return count
