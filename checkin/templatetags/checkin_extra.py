# coding:utf-8
from django import template
from checkin.constant import *
import json

register = template.Library()


@register.assignment_tag
def CHECKIN_STATUS_JSON():
    data = {CHECKIN_STATUS_NORMAL: u"未到", CHECKIN_STATUS_SUCCESS: u"正常", CHECKIN_STATUS_EARLY: u"早退",
            CHECKIN_STATUS_LATEEARLY: u"迟&早",
            CHECKIN_STATUS_LATE: u"迟到", CHECKIN_STATUS_ASK: u"请假", CHECKIN_STATUS_CANCEL: u"取消"}
    return json.dumps(data)


@register.assignment_tag
def CHECKIN_STATUS_STYLE_JSON():
    data = {CHECKIN_STATUS_NORMAL: "gray", CHECKIN_STATUS_SUCCESS: "success", CHECKIN_STATUS_EARLY: "orange",
            CHECKIN_STATUS_LATEEARLY: "purple",
            CHECKIN_STATUS_LATE: "danger", CHECKIN_STATUS_ASK: "info", CHECKIN_STATUS_CANCEL: "warning"}
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
    elif status == CHECKIN_STATUS_ASK:
        return u'请假'
    elif status == CHECKIN_STATUS_CANCEL:
        return u'取消'


@register.filter
def CHECKIN_STATUS_STYLE(status):
    if status == CHECKIN_STATUS_NORMAL:
        return 'gray'
    elif status == CHECKIN_STATUS_SUCCESS:
        return 'success'
    elif status == CHECKIN_STATUS_EARLY:
        return 'orange'
    elif status == CHECKIN_STATUS_LATEEARLY:
        return 'purple'
    elif status == CHECKIN_STATUS_LATE:
        return 'danger'
    elif status == CHECKIN_STATUS_ASK:
        return 'info'
    elif status == CHECKIN_STATUS_CANCEL:
        return 'warning'