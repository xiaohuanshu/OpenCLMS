# Create your tasks here
# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from celery import shared_task

from school.function import getnowlessontime
from course.models import Lesson, Coursehomework, Studentcourse, Courseresource
from course.constant import LESSON_STATUS_NOW, LESSON_STATUS_END, COURSE_HOMEWORK_TYPE_NOSUBMIT
from wechat.client import wechat_client
from django.conf import settings
from django.db.models import Q, F
from django.urls import reverse
from django.core.cache import cache
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


@shared_task(name='send_homework_notification')
def send_homework_notification(homeworkid):
    homework = Coursehomework.objects.get(pk=homeworkid)
    course = homework.course
    studentcourses = Studentcourse.objects.select_related("student__user").filter(course=course).all()
    userid = []
    for sc in studentcourses:
        if sc.student.user and sc.student.user.openid:
            userid.append(sc.student.user.openid)
    if homework.type == COURSE_HOMEWORK_TYPE_NOSUBMIT:
        description = "%s\n点击查看详情" % (homework.title)
    else:
        description = "%s\n点击提交或查看详情，电脑提交请访问%s" % (homework.title, settings.DOMAIN)
    article = {
        "title": "[%s]新作业!" % (course.title),
        "description": description,
        "url": "%s%s" % (settings.DOMAIN, reverse('course:homework', args=[course.id]) + '?homeworkid=%d' % homeworkid),
        "image": "%s/static/img/homework.png"
    }
    wechat_client.message.send_articles(agent_id=settings.AGENTID, user_ids=userid, articles=[article])


@shared_task(name='send_homework_remind')
def send_homework_remind(homeworkid):
    homework = Coursehomework.objects.get(pk=homeworkid)
    course = homework.course
    studentcourses = Studentcourse.objects.select_related("student__user").filter(course=course).only(
        "student__user__openid").all()
    userid = []
    for sc in studentcourses:
        if sc.student.user and sc.student.user.openid:
            userid.append(sc.student.user.openid)
    # 剔除已经交过作业的名单
    for sc in homework.homeworkcommit_set.select_related("student__user").only("student__user__openid").all():
        if sc.student.user and sc.student.user.openid:
            try:
                userid.remove(sc.student.user.openid)
            except ValueError:
                pass
    description = "%s\n教师发送了催交作业提醒，点击提交或查看详情，电脑提交请访问%s" % (homework.title, settings.DOMAIN)
    article = {
        "title": "[%s]催交作业提醒!" % (course.title),
        "description": description,
        "url": "%s%s" % (settings.DOMAIN, reverse('course:homework', args=[course.id]) + '?homeworkid=%d' % homeworkid),
        "image": "%s/static/img/homework.png"
    }
    wechat_client.message.send_articles(agent_id=settings.AGENTID, user_ids=userid, articles=[article])


@shared_task(name='send_resource_notification')
def send_resource_notification(resourceid):
    resource = Courseresource.objects.select_related('course').get(pk=resourceid)
    course = resource.course
    if cache.get("course_resource_notification_lock_%s" % course.id):
        return  # 同课程五分钟内只发送一个提醒
    cache.set("course_resource_notification_lock_%s" % course.id, True, 5 * 60)
    studentcourses = Studentcourse.objects.select_related("student__user").filter(course=course).only(
        "student__user__openid").all()
    userid = []
    for sc in studentcourses:
        if sc.student.user and sc.student.user.openid:
            userid.append(sc.student.user.openid)
    description = "%s\n教师上传了新的课程资源，点击查看详情，电脑下载请访问%s" % (resource.title, settings.DOMAIN)
    article = {
        "title": "[%s]新资源!" % (course.title),
        "description": description,
        "url": "%s%s" % (settings.DOMAIN, reverse('course:resource', args=[course.id])),
        "image": "%s/static/img/resource.png"
    }
    wechat_client.message.send_articles(agent_id=settings.AGENTID, user_ids=userid, articles=[article])
