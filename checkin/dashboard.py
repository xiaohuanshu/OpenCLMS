from __future__ import division
from course.models import Lesson
from models import Checkin
from school.models import Student
from school.function import getnowlessontime
from constant import *
from django.shortcuts import render
from django.core.urlresolvers import reverse
from course.constant import *
import json
from django.shortcuts import HttpResponse, HttpResponseRedirect
from django.db.models import Count, Case, When, Q, F
from school.models import Classtime, Department
from django.views.decorators.cache import cache_page


def overview(request):
    return HttpResponseRedirect(reverse('checkin:dashboard_today', args=[]))


def today(request):
    return render(request, 'dashboard_today.html', {})


@cache_page(60)
def today_data(request):
    data = {}
    now_lesson_time = getnowlessontime()
    now_week = now_lesson_time['week']
    now_day = now_lesson_time['day']
    now_time = now_lesson_time['time']
    now_term = now_lesson_time['term']

    class_time_count = Classtime.objects.count()
    class_times = [(time, time + 1) for time in range(1, class_time_count, 2)]
    class_times_str = ['%s-%s' % (time[0], time[1]) for time in class_times]
    data['class_times'] = class_times_str
    data.update(**now_lesson_time)

    today_lessons = Lesson.objects.filter(week=now_week, day=now_day, term=now_term)
    data['today_lessons'] = today_lessons.count()
    today_start_lessons = today_lessons.filter(status__in=[LESSON_STATUS_NOW, LESSON_STATUS_CHECKIN,
                                                           LESSON_STATUS_CHECKIN_ADD, LESSON_STATUS_CHECKIN_AGAIN,
                                                           LESSON_STATUS_END])
    data['today_start_lessons'] = today_start_lessons.count()
    today_start_checkin_lessons = today_start_lessons.filter(checkincount__gt=0)
    data['today_start_checkin_lessons'] = today_start_checkin_lessons.count()
    # course_status
    course_status_data = Checkin.objects.filter(lesson__in=today_start_checkin_lessons).aggregate(
        normal=Count(Case(When(status=CHECKIN_STATUS_NORMAL, then=1))),
        private_ask=Count(Case(When(status=CHECKIN_STATUS_PRIVATE_ASK, then=1))),
        success=Count(Case(When(status=CHECKIN_STATUS_SUCCESS, then=1))),
        early=Count(Case(When(status=CHECKIN_STATUS_EARLY, then=1))),
        late=Count(Case(When(status=CHECKIN_STATUS_LATE, then=1))),
        lateearly=Count(Case(When(status=CHECKIN_STATUS_LATEEARLY, then=1))),
        public_ask=Count(Case(When(status=CHECKIN_STATUS_PUBLIC_ASK, then=1))),
    )
    course_status_data['arrive'] = course_status_data['success'] + course_status_data['early'] + \
                                   course_status_data['late'] + course_status_data['lateearly']
    course_status_data['ask'] = course_status_data['private_ask'] + course_status_data['public_ask']

    data['course_status_data'] = course_status_data
    # student_status
    student_all_count = Checkin.objects.filter(lesson__in=today_start_checkin_lessons).distinct('student').count()
    student_all_arrive = Checkin.objects.filter(lesson__in=today_start_checkin_lessons). \
        annotate(all=Count('status'), num=Count(Case(When(status=CHECKIN_STATUS_SUCCESS, then=1)))).filter(num=F('all'))
    student_all_arrive.query.group_by = 'student'
    student_all_arrive = student_all_arrive.count()
    student_all_normal = Checkin.objects.filter(lesson__in=today_start_checkin_lessons). \
        annotate(all=Count('status'), num=Count(Case(When(status=CHECKIN_STATUS_NORMAL, then=1)))).filter(num=F('all'))
    student_all_normal.query.group_by = 'student'
    student_all_normal = student_all_normal.count()
    student_public_ask = Checkin.objects.filter(lesson__in=today_start_checkin_lessons).filter(
        status=CHECKIN_STATUS_PUBLIC_ASK).distinct('student').count()
    student_private_ask = Checkin.objects.filter(lesson__in=today_start_checkin_lessons).filter(
        status=CHECKIN_STATUS_PRIVATE_ASK).distinct('student').count()
    student_other = Checkin.objects.filter(lesson__in=today_start_checkin_lessons).exclude(
        status__in=[CHECKIN_STATUS_SUCCESS, CHECKIN_STATUS_NORMAL, CHECKIN_STATUS_PUBLIC_ASK,
                    CHECKIN_STATUS_PRIVATE_ASK]).distinct('student').count()
    student_late_count = Checkin.objects.filter(lesson__in=today_start_checkin_lessons).filter(
        Q(status=CHECKIN_STATUS_LATE) | Q(status=CHECKIN_STATUS_LATEEARLY)).distinct('student').count()
    student_early_count = Checkin.objects.filter(lesson__in=today_start_checkin_lessons).filter(
        Q(status=CHECKIN_STATUS_EARLY) | Q(status=CHECKIN_STATUS_LATEEARLY)).distinct('student').count()
    student_normal_count = Checkin.objects.filter(lesson__in=today_start_checkin_lessons).filter(
        status=CHECKIN_STATUS_NORMAL).distinct('student').count()
    course_late_count = Checkin.objects.filter(lesson__in=today_start_checkin_lessons).filter(
        Q(status=CHECKIN_STATUS_LATE) | Q(status=CHECKIN_STATUS_LATEEARLY)).count()
    course_early_count = Checkin.objects.filter(lesson__in=today_start_checkin_lessons).filter(
        Q(status=CHECKIN_STATUS_EARLY) | Q(status=CHECKIN_STATUS_LATEEARLY)).count()
    course_normal_count = Checkin.objects.filter(lesson__in=today_start_checkin_lessons).filter(
        status=CHECKIN_STATUS_EARLY).count()
    data.update({'student_all_arrive': student_all_arrive,
                 'student_all_normal': student_all_normal,
                 'student_public_ask': student_public_ask,
                 'student_private_ask': student_private_ask,
                 'student_other': student_other,
                 'student_late_count': student_late_count,
                 'student_early_count': student_early_count,
                 'course_late_count': course_late_count,
                 'course_early_count': course_early_count,
                 'course_normal_count': course_normal_count,
                 'student_all_count': student_all_count,
                 'student_normal_count': student_normal_count})

    # Department status
    department_list = Department.objects.filter(pk__in=Student.objects.distinct('department').values_list('department'))
    data['department_list'] = [d.name for d in department_list]

    department_normal_value = []
    department_ask_value = []
    department_success_value = []
    department_late_value = []
    department_early_value = []
    department_lateearly_value = []

    for d in department_list:
        res = Checkin.objects.filter(lesson__in=today_start_checkin_lessons, student__in=d.student_set.all()).aggregate(
            normal=Count(Case(When(status=CHECKIN_STATUS_NORMAL, then=1))),
            ask=Count(Case(When(status__in=[CHECKIN_STATUS_PRIVATE_ASK, CHECKIN_STATUS_PUBLIC_ASK], then=1))),
            success=Count(Case(When(status=CHECKIN_STATUS_SUCCESS, then=1))),
            early=Count(Case(When(status=CHECKIN_STATUS_EARLY, then=1))),
            late=Count(Case(When(status=CHECKIN_STATUS_LATE, then=1))),
            lateearly=Count(Case(When(status=CHECKIN_STATUS_LATEEARLY, then=1))),
        )
        department_normal_value.append(res['normal'])
        department_ask_value.append(res['ask'])
        department_success_value.append(res['success'])
        department_late_value.append(res['late'])
        department_early_value.append(res['early'])
        department_lateearly_value.append(res['lateearly'])

    data.update({'department_normal_value': department_normal_value,
                 'department_ask_value': department_ask_value,
                 'department_success_value': department_success_value,
                 'department_late_value': department_late_value,
                 'department_early_value': department_early_value,
                 'department_lateearly_value': department_lateearly_value})

    # Course time status

    coursetime_normal_value = []
    coursetime_ask_value = []
    coursetime_success_value = []
    coursetime_late_value = []
    coursetime_early_value = []
    coursetime_lateearly_value = []
    coursetime_arrive_value = []

    for cs in class_times:
        time_filter = Q(lesson__time__gte=cs[0], lesson__length__gte=cs[1] - F('lesson__time'),
                        lesson__time__lte=cs[1]) | \
                      Q(lesson__time__lte=cs[0], lesson__length__gte=cs[1] - F('lesson__time')) | \
                      Q(lesson__time__lte=cs[0], lesson__length__lte=cs[1] - F('lesson__time'),
                        lesson__length__gte=cs[0] - F('lesson__time'))
        res = Checkin.objects.filter(lesson__in=today_start_checkin_lessons).filter(time_filter).aggregate(
            normal=Count(Case(When(status=CHECKIN_STATUS_NORMAL, then=1))),
            ask=Count(Case(When(status__in=[CHECKIN_STATUS_PRIVATE_ASK, CHECKIN_STATUS_PUBLIC_ASK], then=1))),
            success=Count(Case(When(status=CHECKIN_STATUS_SUCCESS, then=1))),
            early=Count(Case(When(status=CHECKIN_STATUS_EARLY, then=1))),
            late=Count(Case(When(status=CHECKIN_STATUS_LATE, then=1))),
            lateearly=Count(Case(When(status=CHECKIN_STATUS_LATEEARLY, then=1))),
        )
        coursetime_normal_value.append(res['normal'])
        coursetime_ask_value.append(res['ask'])
        coursetime_success_value.append(res['success'])
        coursetime_late_value.append(res['late'])
        coursetime_early_value.append(res['early'])
        coursetime_lateearly_value.append(res['lateearly'])
        coursetime_arrive_value.append(res['lateearly'] + res['early'] + res['late'] + res['success'])
    data.update({'coursetime_normal_value': coursetime_normal_value,
                 'coursetime_ask_value': coursetime_ask_value,
                 'coursetime_success_value': coursetime_success_value,
                 'coursetime_late_value': coursetime_late_value,
                 'coursetime_early_value': coursetime_early_value,
                 'coursetime_lateearly_value': coursetime_lateearly_value,
                 'coursetime_arrive_value': coursetime_arrive_value})

    return HttpResponse(json.dumps(data), content_type="application/json")
