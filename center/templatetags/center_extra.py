# coding:utf-8
from django import template
from django.urls import resolve
from django.conf import settings

register = template.Library()


@register.simple_tag
def DOMAIN():
    from django.conf import settings
    return settings.DOMAIN


@register.simple_tag
def nav_active(path, name):
    if name in resolve(path).url_name:
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
    if settings.WEEK_FIRST_DAY == 0:
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
    else:
        if week == 6:
            return u'周日'
        elif week == 0:
            return u'周一'
        elif week == 1:
            return u'周二'
        elif week == 2:
            return u'周三'
        elif week == 3:
            return u'周四'
        elif week == 4:
            return u'周五'
        elif week == 5:
            return u'周六'
