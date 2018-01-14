# -*- coding: utf-8 -*-
import datetime
from center.cache import cache_func
from models import Major, Schoolterm, Classtime, Department, Administration
from django.db.models import ObjectDoesNotExist
from django.core.cache import cache
from django.conf import settings


@cache_func('majordata', 60 * 60 * 24)
def getMajor():
    majordata = Major.objects.select_related('department').all()
    mdata = {}
    last = ''
    for major in majordata:
        if last != major.department.name:
            last = major.department.name
            mdata.update({last: []})
        mdata[last].append(major.name)
    return mdata


@cache_func('currentschoolyearterm', 60 * 60 * 24)
def getCurrentSchoolYearTerm():
    data = Schoolterm.objects.get(now=True)
    return {'year': data.schoolyear, 'term': data.description}


def getTermDate(term):
    data = cache.get('gettermdate_%s' % term, default=None)
    if not data:
        data = Schoolterm.objects.get(description=term)
        data = [data.startdate, data.enddate]
        cache.set('gettermdate_%s' % term, data, 60 * 60 * 24)
    return data


@cache_func('termdata', 60 * 60 * 24)
def getTerm():
    termdata = Schoolterm.objects.all()
    mdata = []
    for m in termdata:
        mdata.append(m.description)
    return mdata


@cache_func('classtimedata', 60 * 60 * 24)
def getClassTime():
    classtimedata = Classtime.objects.all()
    mdata = {}
    for m in classtimedata:
        mdata[m.id] = [m.starttime, m.endtime]
    return mdata


@cache_func('administrationdata', 60 * 60 * 24)
def getAdministration():
    administrationdata = Administration.objects.values_list('name', flat=True)
    return administrationdata


@cache_func('departmentdata', 60 * 60 * 24)
def getDepartment():
    departmentdata = Department.objects.values_list('name', flat=True)
    return departmentdata


@cache_func('schoolyeardata', 60 * 60 * 24)
def getSchoolyear():
    schoolyeardata = Schoolterm.objects.order_by('schoolyear').values_list('schoolyear', flat=True)
    schoolyeardata.query.group_by = ['schoolyear']
    return schoolyeardata


def datetoTermdate(date):
    datet = datetime.datetime.strptime(date, '%Y-%m-%d')
    date = datet.date()
    term = Schoolterm.objects.get(startdate__lte=date, enddate__gte=date)
    thistermtime = datetime.datetime.strptime(str(term.startdate), '%Y-%m-%d')
    time = datet - thistermtime
    day = time.days
    week = 0
    while day >= 7:
        day = day - 7
        week = week + 1
    week += 1
    return {'term': term.description, 'week': week, 'day': day}


def getnowlessontime():
    term = getCurrentSchoolYearTerm()['term']
    startdate = getTermDate(term)[0]
    thistermdate = datetime.datetime.strptime(str(startdate), '%Y-%m-%d').date()
    nowtime = datetime.datetime.now()
    time = nowtime.date() - thistermdate
    day = time.days
    week = 0
    while day >= 7:
        day = day - 7
        week = week + 1
    week += 1
    try:
        nowlessontime = Classtime.objects.get(starttime__lte=nowtime.time(), endtime__gte=nowtime.time()).id
    except ObjectDoesNotExist:
        nowlessontime = 0
    return {'week': week, 'day': day, 'time': nowlessontime, 'term': term}


def timetoclasstime(time, move=0):  # move=   -1:lessontime back 0:lesson time 1:lessontime forward
    classtimedata = getClassTime()
    if move == 0:
        for t in classtimedata:
            if time >= classtimedata[t][0] and time <= classtimedata[t][1]:
                return t
        return 0
    elif move == -1:
        for t in sorted(classtimedata.keys()):
            if (time >= classtimedata[t][0] and time <= classtimedata[t][1]) or time <= classtimedata[t][0]:
                return t
        return 999
    elif move == 1:
        for t in sorted(classtimedata.keys(), reverse=True):
            if (time >= classtimedata[t][0] and time <= classtimedata[t][1]) or time >= classtimedata[t][1]:
                return t
        return 0


def day_to_week_string(day):
    if settings.WEEK_FIRST_DAY == 1:
        week_day_dict = {
            0: u'星期一',
            1: u'星期二',
            2: u'星期三',
            3: u'星期四',
            4: u'星期五',
            5: u'星期六',
            6: u'星期日',
        }
    else:
        week_day_dict = {
            0: u'星期日',
            1: u'星期一',
            2: u'星期二',
            3: u'星期三',
            4: u'星期四',
            5: u'星期五',
            6: u'星期六',
        }
    return week_day_dict[day]
