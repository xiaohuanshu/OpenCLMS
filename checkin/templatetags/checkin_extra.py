# coding:utf-8
from django import template
from checkin.constant import *
import json

register = template.Library()


@register.assignment_tag
def CHECKIN_STATUS_JSON():
    data = {CHECKIN_STATUS_NORMAL: u"未到", CHECKIN_STATUS_SUCCESS: u"正常", CHECKIN_STATUS_EARLY: u"早退",
            CHECKIN_STATUS_LATEEARLY: u"迟&早", CHECKIN_STATUS_PRIVATE_ASK: u"事假", CHECKIN_STATUS_SICK_ASK: u"病假",
            CHECKIN_STATUS_LATE: u"迟到", CHECKIN_STATUS_PUBLIC_ASK: u"公假", CHECKIN_STATUS_CANCEL: u"取消"}
    return json.dumps(data)


@register.assignment_tag
def CHECKIN_STATUS_STYLE_JSON():
    data = {CHECKIN_STATUS_NORMAL: "gray", CHECKIN_STATUS_SUCCESS: "green", CHECKIN_STATUS_EARLY: "fuchsia",
            CHECKIN_STATUS_LATEEARLY: "purple", CHECKIN_STATUS_PRIVATE_ASK: "blue", CHECKIN_STATUS_SICK_ASK: "blue",
            CHECKIN_STATUS_LATE: "maroon", CHECKIN_STATUS_PUBLIC_ASK: "blue", CHECKIN_STATUS_CANCEL: "yellow"}
    return json.dumps(data)


@register.assignment_tag
def ASK_STATUS_STYLE_JSON():
    data = {ASK_STATUS_WAITING: "info", ASK_STATUS_APPROVE: "success", ASK_STATUS_CANCEL: "danger"}
    return json.dumps(data)


@register.assignment_tag
def ASK_STATUS_JSON():
    data = {ASK_STATUS_WAITING: u"等待批准", ASK_STATUS_APPROVE: u"批准", ASK_STATUS_CANCEL: u"取消"}
    return json.dumps(data)


@register.filter
def CHECKIN_STATUS(status):
    if status == CHECKIN_STATUS_NORMAL:
        return u'未到'
    elif status == CHECKIN_STATUS_SUCCESS:
        return u'正常'
    elif status == CHECKIN_STATUS_EARLY:
        return u'早退'
    elif status == CHECKIN_STATUS_LATEEARLY:
        return u'迟&早'
    elif status == CHECKIN_STATUS_LATE:
        return u'迟到'
    elif status == CHECKIN_STATUS_PRIVATE_ASK:
        return u'事假'
    elif status == CHECKIN_STATUS_PUBLIC_ASK:
        return u'公假'
    elif status == CHECKIN_STATUS_SICK_ASK:
        return u'病假'
    elif status == CHECKIN_STATUS_CANCEL:
        return u'取消'


@register.filter
def CHECKIN_STATUS_STYLE(status):
    if status == CHECKIN_STATUS_NORMAL:
        return 'gray'
    elif status == CHECKIN_STATUS_SUCCESS:
        return 'green'
    elif status == CHECKIN_STATUS_EARLY:
        return 'fuchsia'
    elif status == CHECKIN_STATUS_LATEEARLY:
        return 'purple'
    elif status == CHECKIN_STATUS_LATE:
        return 'maroon'
    elif status == CHECKIN_STATUS_PRIVATE_ASK:
        return 'blue'
    elif status == CHECKIN_STATUS_PUBLIC_ASK:
        return 'blue'
    elif status == CHECKIN_STATUS_SICK_ASK:
        return 'blue'
    elif status == CHECKIN_STATUS_CANCEL:
        return 'yellow'


@register.assignment_tag
def CHECKINURL():
    from django.conf import settings
    return settings.CHECKINURL


@register.filter
def CHECKIN_ABNORMAL(status):
    if status == CHECKIN_ABNORMAL_ACCOUNT:
        return u'帐号异常'
    elif status == CHECKIN_ABNORMAL_LOCATION:
        return u'位置异常'


@register.assignment_tag
def CHECKIN_ABNORMAL_JSON():
    data = {CHECKIN_ABNORMAL_ACCOUNT: u"帐号异常", CHECKIN_ABNORMAL_LOCATION: u"位置异常"}
    return json.dumps(data)
