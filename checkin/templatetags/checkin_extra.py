# coding:utf-8
from django import template
from checkin.constant import *
import json

register = template.Library()


@register.assignment_tag
def CHECKIN_STATUS_JSON():
    data = {CHECKIN_STATUS_NORMAL: u"未到", CHECKIN_STATUS_SUCCESS: u"正常", CHECKIN_STATUS_EARLY: u"早退",
            CHECKIN_STATUS_LATEEARLY: u"迟到早退",
            CHECKIN_STATUS_LATE: u"迟到", CHECKIN_STATUS_ASK: u"请假", CHECKIN_STATUS_CANCEL: u"取消"}
    return json.dumps(data)


@register.assignment_tag
def CHECKIN_STATUS_STYLE_JSON():
    data = {CHECKIN_STATUS_NORMAL: "default", CHECKIN_STATUS_SUCCESS: "success", CHECKIN_STATUS_EARLY: "danger",
            CHECKIN_STATUS_LATEEARLY: "danger",
            CHECKIN_STATUS_LATE: "danger", CHECKIN_STATUS_ASK: "info", CHECKIN_STATUS_CANCEL: "warning"}
    return json.dumps(data)
