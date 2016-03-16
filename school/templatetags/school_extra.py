from school.function import getMajor, getTerm, getTermDate, getSchoolyear, getAdministration, getDepartment
from django import template

register = template.Library()


@register.assignment_tag
def getmajor():
    try:
        return getMajor()
    except UnicodeEncodeError:
        return ''


@register.assignment_tag
def getadministration():
    try:
        return getAdministration()
    except UnicodeEncodeError:
        return ''


@register.assignment_tag
def getdepartment():
    try:
        return getDepartment()
    except UnicodeEncodeError:
        return ''


@register.assignment_tag
def getterm():
    try:
        return getTerm()
    except UnicodeEncodeError:
        return ''


@register.assignment_tag
def gettermdate(term):
    try:
        return getTermDate(term)
    except UnicodeEncodeError:
        return ''


@register.assignment_tag
def getschoolyear():
    try:
        return getSchoolyear()
    except UnicodeEncodeError:
        return ''