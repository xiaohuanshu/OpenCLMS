from school.function import getCurrentSchoolYearTerm, getTermDate, datetoTermdate, getClassTime
from django.shortcuts import render
import json
import time
from django.db.models import Q
from django.http import HttpResponse
from school.models import Student
from .models import Studentcourse, Lesson, Course
from django.core.exceptions import ObjectDoesNotExist
import datetime
from django.core.urlresolvers import reverse


def schedule(request):
    tdata = {}
    if request.GET.get('term', default=False):
        term = request.GET.get('term')
    else:
        term = getCurrentSchoolYearTerm()
        term = term['term']
    tdata['term'] = term
    termdate = getTermDate(term)
    tdata['startdate'] = termdate[0]
    tdata['enddate'] = termdate[1]
    classtime = getClassTime()
    for key in classtime:
        # classtime[key][0]=str(classtime[key][0])
        # classtime[key][1]=str(classtime[key][1])
        classtime[key][0] = datetime.time.strftime(classtime[key][0], '%H:%M')
        classtime[key][1] = datetime.time.strftime(classtime[key][1], '%H:%M')
    tdata['classtime'] = json.dumps(classtime)

    if request.GET.get('day', default=False):
        tdata['day'] = request.GET.get('day')
    if request.GET.get('view', default=False):
        tdata['view'] = request.GET.get('view')
    return render(request, 'schedule.html', tdata)


def schedule_data(request):
    # tfrom = time.strftime('%Y-%m-%d',time.localtime(round(string.atoi(request.GET.get('from'))/1000.0)))
    # tto = time.strftime('%Y-%m-%d',time.localtime(round(string.atoi(request.GET.get('to'))/1000.0)))
    start = request.GET.get('start')
    end = request.GET.get('end')
    try:
        startinf = datetoTermdate(start)
        endinf = datetoTermdate(end)
    except ObjectDoesNotExist:
        return HttpResponse(json.dumps([]), content_type="application/json")
    term = request.GET.get('term')
    if request.user.isteacher:
        courses = request.user.teacher_set.get().course_set.all()
    else:
        student = Student.objects.get(user=request.user)
        courses = Studentcourse.objects.filter(student=student).values_list('course', flat=True)
    plessonlist = Lesson.objects.select_related('course').select_related('classroom') \
        .filter(term=term, course__in=courses)
    if startinf['week'] == endinf['week']:
        plessonlist = plessonlist.filter(week=startinf['week'], day__gte=startinf['day'], day__lte=endinf['day'])
    else:
        plessonlist = plessonlist.filter(
            Q(Q(Q(week=startinf['week'], day__gte=startinf['day']) | Q(week=endinf['week'],
                                                                       day__lte=endinf['day'])) |
              Q(week__gt=startinf['week'], week__lt=endinf['week']))).all()
    data = []
    colordata = {}
    lastcolorid = 0
    for m in plessonlist:
        if m.course.id not in colordata:
            colordata.update({m.course.id: eventClass(lastcolorid)})
            lastcolorid += 1
        data.append({'id': m.course.id, 'title': m.course.title,
                     'start': time.mktime(m.getTime[0]),
                     'end': time.mktime(m.getTime[1]),
                     'classtime_time': m.time,
                     'classtime_length': m.length,
                     'location': m.classroom.location,
                     'class': colordata.get(m.course.id),
                     'url': reverse('course:information', args=[m.course.id])
                     })
        # print "%s,%s" % (m.lessonid.name, time.strftime('%Y-%m-%dT%H:%M:%S',
        # getlessontime(m.term, m.week, m.day, m.time, m.length)[0]))
    return HttpResponse(json.dumps(data), content_type="application/json")


def eventClass(index):
    index = index % 10
    color = ['#84b6d4', '#7bd7f5', '#77c595', '#f9bf76', '#ea8e81',
             '#e2e4ea', '#8adede', '#9896c6', '#ffb078', '#e87599']
    return color[index]
