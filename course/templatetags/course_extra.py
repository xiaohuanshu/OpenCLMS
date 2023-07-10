# coding:utf-8
from django import template
from course.constant import *
from course.models import Homeworkcommit
import json

register = template.Library()


@register.filter
def COURSE_STATUS(status):
    if status == 0:
        return u'未上课'
    elif status == 1:
        return u'上课中'


@register.filter
def COURSE_STATUS_STYLE(status):
    if status == 0:
        return 'default'
    elif status == 1:
        return 'success'


@register.filter
def LESSON_STATUS(status):
    if status == LESSON_STATUS_AWAIT or status == LESSON_STATUS_NEW_AWAIT:
        return u'未开始'
    elif status == LESSON_STATUS_AGREE:
        return u'允许开始'
    elif status == LESSON_STATUS_CHECKIN:
        return u'正在签到'
    elif status == LESSON_STATUS_NOW:
        return u'正在上课'
    elif status == LESSON_STATUS_CHECKIN_ADD:
        return u'正在签到'
    elif status == LESSON_STATUS_CHECKIN_AGAIN:
        return u'正在签到'
    elif status == LESSON_STATUS_WRONG:
        return u'课程未正常开始'
    elif status == LESSON_STATUS_END:
        return u'课程结束'
    elif status == LESSON_STATUS_END_EARLY:
        return u'超前结束'
    elif status == LESSON_STATUS_START_LATE:
        return u'较晚开始'
    elif status == LESSON_STATUS_CANCLE:
        return u'课程取消'


@register.filter
def COURSE_HOMEWORK_TYPE(status):
    if status == COURSE_HOMEWORK_TYPE_NOSUBMIT:
        return u'无需提交'
    elif status == COURSE_HOMEWORK_TYPE_ONLINESUBMIT:
        return u'在线提交'
    elif status == COURSE_HOMEWORK_TYPE_ONLINEANSWER:
        return u'在线作答'


@register.filter
def LESSON_STATUS_STYLE(status):
    if status == LESSON_STATUS_AWAIT or status == LESSON_STATUS_NEW_AWAIT:
        return 'default'
    elif status == LESSON_STATUS_AGREE:
        return 'warning'
    elif status == LESSON_STATUS_CHECKIN:
        return 'info'
    elif status == LESSON_STATUS_NOW:
        return 'success'
    elif status == LESSON_STATUS_CHECKIN_ADD:
        return 'info'
    elif status == LESSON_STATUS_CHECKIN_AGAIN:
        return 'info'
    elif status == LESSON_STATUS_WRONG:
        return 'warning'
    elif status == LESSON_STATUS_END:
        return 'danger'
    elif status == LESSON_STATUS_END_EARLY:
        return 'danger'
    elif status == LESSON_STATUS_START_LATE:
        return 'warning'


@register.simple_tag
def LESSON_STATUS_JSON():
    data = {LESSON_STATUS_AWAIT: u"未开始", LESSON_STATUS_AGREE: u"允许开始", LESSON_STATUS_CHECKIN: u"正在签到",
            LESSON_STATUS_NOW: u"正在上课", LESSON_STATUS_CHECKIN_ADD: u"正在签到", LESSON_STATUS_CHECKIN_AGAIN: u"正在签到",
            LESSON_STATUS_WRONG: u"课程未正常开始", LESSON_STATUS_NEW_AWAIT: u'未开始', LESSON_STATUS_CANCLE: u'课程取消',
            LESSON_STATUS_END: u"课程结束", LESSON_STATUS_END_EARLY: u"超前结束", LESSON_STATUS_START_LATE: u"较晚开始"}
    return json.dumps(data)


@register.simple_tag
def LESSON_STATUS_STYLE_JSON():
    data = {LESSON_STATUS_AWAIT: "default", LESSON_STATUS_AGREE: "warning", LESSON_STATUS_CHECKIN: "info",
            LESSON_STATUS_NOW: "success", LESSON_STATUS_CHECKIN_ADD: "info", LESSON_STATUS_CHECKIN_AGAIN: "info",
            LESSON_STATUS_WRONG: "warning", LESSON_STATUS_NEW_AWAIT: 'default', LESSON_STATUS_CANCLE: 'danger',
            LESSON_STATUS_END: "danger", LESSON_STATUS_END_EARLY: "danger", LESSON_STATUS_START_LATE: "warning"}
    return json.dumps(data)


@register.simple_tag
def student_submit_homework(student, homework):
    try:
        return Homeworkcommit.objects.filter(coursehomework=homework, student=student).get()
    except:
        return None
