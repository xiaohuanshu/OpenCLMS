# coding:utf-8
__author__ = 'xiaohuanshu'
from django import template
from django.core.urlresolvers import resolve
# from lessonmodel.constant import *
import json

register = template.Library()


@register.assignment_tag
def DOMAIN():
    from django.conf import settings
    return settings.DOMAIN


@register.simple_tag
def nav_active(path, name):
    if resolve(path).url_name == name:
        return 'active'
    else:
        return ''


@register.simple_tag
def nav_menu_active(path, name):
    if name == resolve(path).namespace:
        return 'active'
    else:
        return ''


@register.filter
def weekdeal(week):
    if week == 0:
        return u'周日'
    elif week == 1:
        return u'周一'
    elif week == 2:
        return u'周二'
    elif week == 3:
        return u'周三'
    elif week == 4:
        return u'周四'
    elif week == 5:
        return u'周五'
    elif week == 6:
        return u'周六'