# -*- coding: utf-8 -*-
from course.models import Course, Studentcourse, StudentExam
from django.urls import reverse
from icalendar import Calendar, Event
from datetime import datetime, timedelta
from course.function import getweek, gettime, getday
from school.function import getTermDate, getClassTime, getCurrentSchoolYearTerm
from django.conf import settings
from user_system.models import User
from django.shortcuts import get_object_or_404, render
import pytz
from django.http import HttpResponse
from django.db.models import Q


def get_lesson_time(term, week, day, time, length):
    # allowcheckinbeforetime = 10
    classtime = getClassTime()
    termtime = getTermDate(term)
    thistermtime = datetime.strptime(str(termtime[0]), '%Y-%m-%d')
    dayplus = (week - 1) * 7 + day
    thistermtime = thistermtime + timedelta(days=dayplus)
    coursestarttime = datetime.strptime(str(classtime[time][0]), '%H:%M:%S')
    courseendtime = datetime.strptime(str(classtime[time + length - 1][1]), '%H:%M:%S')
    starttime = thistermtime + timedelta(hours=coursestarttime.hour, minutes=coursestarttime.minute,
                                         seconds=coursestarttime.second)
    endtime = thistermtime + timedelta(hours=courseendtime.hour, minutes=courseendtime.minute,
                                       seconds=courseendtime.second)
    tzinfo = pytz.timezone(settings.TIME_ZONE)
    starttime.replace(tzinfo=tzinfo)
    endtime.replace(tzinfo=tzinfo)
    return [starttime, endtime]


def course_event(course):
    times = course.time.split(';')
    term = course.schoolterm
    locations = course.location.split(';')
    events = []

    for i, time in enumerate(times):
        uid = "%d-%d" % (course.id, i)
        url = "%s%s" % (settings.DOMAIN, reverse('course:information', args=[course.id]))
        event = Event()
        LOCATION = locations[i]
        first_week = getweek(time)[0]
        last_week = getweek(time)[-1]
        week_length = last_week - first_week + 1
        issingle = u'|单周' in time
        isdouble = u'|双周' in time
        repeat_two_week = issingle or isdouble
        first_time = gettime(time)[0]
        last_time = gettime(time)[-1]
        time_length = last_time - first_time + 1
        day = getday(time)

        DTSTART, DTEND = get_lesson_time(term, first_week, day, first_time, time_length)
        # UNTIL = get_lesson_time(term, last_week, day, first_time, time_length)[1]
        event['uid'] = uid
        event.add('summary', course.title)
        event.add('dtstart', DTSTART)
        event.add('dtend', DTEND)
        event.add('url', url)
        event.add('location', LOCATION)
        if week_length != 1:
            if not repeat_two_week:
                event.add('RRULE', {'FREQ': 'WEEKLY', 'count': week_length})
            else:
                if issingle:
                    week_length = week_length / 2 + 1
                else:
                    week_length = week_length / 2
                event.add('RRULE', {'FREQ': 'WEEKLY', 'count': week_length, 'INTERVAL': 2, 'WKST': 'SU'})

        events.append(event)
    return events


def exam_event(exam):
    event = Event()
    uid = "%d-exam" % (exam.course.id if exam.course else exam.id)
    if exam.course:
        url = "%s%s" % (settings.DOMAIN, reverse('course:information', args=[exam.course.id]))
        event.add('url', url)
    location = exam.location.location
    starttime = exam.starttime
    endtime = exam.endtime
    tzinfo = pytz.timezone(settings.TIME_ZONE)
    starttime.replace(tzinfo=tzinfo)
    endtime.replace(tzinfo=tzinfo)

    event['uid'] = uid
    event.add('summary', u"(考试)" + exam.course.title if exam.course else '考试')
    event.add('dtstart', starttime)
    event.add('dtend', endtime)
    event.add('location', location)
    event.add('description', u"座位:" + exam.seat)

    return event


def generate_ics(courses, exams):
    cal = Calendar()
    cal.add('X-WR-CALNAME', '课程')
    cal.add('version', '2.0')
    for course in courses:
        if course.time == '' or course.time is None:
            continue
        for ce in course_event(course):
            cal.add_component(ce)
    for exam in exams:
        cal.add_component(exam_event(exam))
    return cal.to_ical()


def ics(request, userid):
    user = get_object_or_404(User, id=userid)
    agent = request.META.get('HTTP_USER_AGENT', None)
    if agent and "MicroMessenger" in agent:
        return render(request, 'openinbrowser.html')
    schoolterm = getCurrentSchoolYearTerm()['term']
    if user.isteacher:
        teacher = user.teacher_set.get()
        course = teacher.course_set.filter(schoolterm=schoolterm).all()
        exams = []
    else:
        student = user.student_set.get()
        termcourse = Studentcourse.objects.filter(student=student, course__schoolterm=schoolterm) \
            .values_list('course', flat=True)
        course = Course.objects.filter(id__in=termcourse).all()
        exams = StudentExam.objects.filter(student=student).filter(Q(course__schoolterm=schoolterm) | Q(course=None)) \
            .select_related('course', 'location').all()
    return HttpResponse(generate_ics(course, exams), content_type="text/calendar")


def download(request):
    return render(request, 'ics_introduce.html', {'url': reverse('course:ics', args=[request.user.id])})
