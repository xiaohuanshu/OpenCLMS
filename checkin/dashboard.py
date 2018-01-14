from __future__ import division
from course.models import Lesson
from checkin.models import Checkin, CheckinHistory, DailySubscibe
from school.models import Student
from school.function import getnowlessontime
from constant import *
from django.shortcuts import render
from django.core.urlresolvers import reverse
from course.constant import *
import json
import datetime
from django.shortcuts import HttpResponse, HttpResponseRedirect
from django.db.models import Count, Case, When, Q, F, OuterRef, Subquery, IntegerField
from school.models import Classtime, Department
from django.views.decorators.cache import cache_page
from django.db import connection, transaction
from user_system.auth import permission_required


def overview(request):
    return HttpResponseRedirect(reverse('checkin:dashboard_today', args=[]))


def today(request):
    return render(request, 'dashboard_today.html', {})


def week(request):
    return render(request, 'dashboard_week.html', {})


def term(request):
    return render(request, 'dashboard_term.html', {})


@permission_required(permission='checkin_view')
def history(request):
    chs = CheckinHistory.objects.filter().all()
    data = []
    for ch in chs:
        data.append({
            'term': ch.term,
            'week': ch.week,
            'day': ch.day,
            'file': ch.file.url,
            'generated_time': datetime.datetime.strftime(ch.generated_time, '%Y-%m-%d %I:%M %p') \
                if ch.generated_time else None,
            'course_count': ch.course_count,
        })
    subscibe = request.GET.get("subscibe", default=None)
    if subscibe == '1':
        DailySubscibe.objects.get_or_create(user=request.user)
        subscibed = True
    elif subscibe == '0':
        DailySubscibe.objects.filter(user=request.user).delete()
        subscibed = False
    else:
        subscibed = DailySubscibe.objects.filter(user=request.user).exists()
    return render(request, 'history.html', {'data': json.dumps(data), 'subscibed': subscibed})


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
    course_status_data = Checkin.objects.filter(lesson__in=today_start_lessons).aggregate(
        normal=Count(Case(When(status=CHECKIN_STATUS_NORMAL, then=1))),
        private_ask=Count(Case(When(status=CHECKIN_STATUS_PRIVATE_ASK, then=1))),
        success=Count(Case(When(status=CHECKIN_STATUS_SUCCESS, then=1))),
        early=Count(Case(When(status=CHECKIN_STATUS_EARLY, then=1))),
        late=Count(Case(When(status=CHECKIN_STATUS_LATE, then=1))),
        lateearly=Count(Case(When(status=CHECKIN_STATUS_LATEEARLY, then=1))),
        public_ask=Count(Case(When(status=CHECKIN_STATUS_PUBLIC_ASK, then=1))),
        sick_ask=Count(Case(When(status=CHECKIN_STATUS_SICK_ASK, then=1))),
    )
    course_status_data['arrive'] = course_status_data['success'] + course_status_data['early'] + \
                                   course_status_data['late'] + course_status_data['lateearly']
    course_status_data['ask'] = course_status_data['private_ask'] + course_status_data['public_ask'] + \
                                course_status_data['sick_ask']

    data['course_status_data'] = course_status_data
    # student_status
    student_all_count = Checkin.objects.filter(lesson__in=today_start_lessons).distinct('student').count()
    student_all_arrive = Checkin.objects.filter(lesson__in=today_start_lessons). \
        annotate(all=Count('status'), num=Count(Case(When(status=CHECKIN_STATUS_SUCCESS, then=1)))).filter(num=F('all'))
    student_all_arrive.query.group_by = 'student'
    student_all_arrive = student_all_arrive.count()
    student_all_normal = Checkin.objects.filter(lesson__in=today_start_lessons). \
        annotate(all=Count('status'), num=Count(Case(When(status=CHECKIN_STATUS_NORMAL, then=1)))).filter(num=F('all'))
    student_all_normal.query.group_by = 'student'
    student_all_normal = student_all_normal.count()
    student_public_ask = Checkin.objects.filter(lesson__in=today_start_lessons).filter(
        status=CHECKIN_STATUS_PUBLIC_ASK).distinct('student').count()
    student_private_ask = Checkin.objects.filter(lesson__in=today_start_lessons).filter(
        status=CHECKIN_STATUS_PRIVATE_ASK).distinct('student').count()
    student_sick_ask = Checkin.objects.filter(lesson__in=today_start_lessons).filter(
        status=CHECKIN_STATUS_SICK_ASK).distinct('student').count()
    student_other = Checkin.objects.filter(lesson__in=today_start_lessons).exclude(
        status__in=[CHECKIN_STATUS_SUCCESS, CHECKIN_STATUS_NORMAL, CHECKIN_STATUS_PUBLIC_ASK,
                    CHECKIN_STATUS_PRIVATE_ASK, CHECKIN_STATUS_SICK_ASK]).distinct('student').count()
    student_late_count = Checkin.objects.filter(lesson__in=today_start_lessons).filter(
        Q(status=CHECKIN_STATUS_LATE) | Q(status=CHECKIN_STATUS_LATEEARLY)).distinct('student').count()
    student_early_count = Checkin.objects.filter(lesson__in=today_start_lessons).filter(
        Q(status=CHECKIN_STATUS_EARLY) | Q(status=CHECKIN_STATUS_LATEEARLY)).distinct('student').count()
    student_normal_count = Checkin.objects.filter(lesson__in=today_start_lessons).filter(
        status=CHECKIN_STATUS_NORMAL).distinct('student').count()
    course_late_count = Checkin.objects.filter(lesson__in=today_start_lessons).filter(
        Q(status=CHECKIN_STATUS_LATE) | Q(status=CHECKIN_STATUS_LATEEARLY)).count()
    course_early_count = Checkin.objects.filter(lesson__in=today_start_lessons).filter(
        Q(status=CHECKIN_STATUS_EARLY) | Q(status=CHECKIN_STATUS_LATEEARLY)).count()
    course_normal_count = Checkin.objects.filter(lesson__in=today_start_lessons).filter(
        status=CHECKIN_STATUS_EARLY).count()
    data.update({'student_all_arrive': student_all_arrive,
                 'student_all_normal': student_all_normal,
                 'student_public_ask': student_public_ask,
                 'student_private_ask': student_private_ask,
                 'student_sick_ask': student_sick_ask,
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
        res = Checkin.objects.filter(lesson__in=today_start_lessons, student__in=d.student_set.all()).aggregate(
            normal=Count(Case(When(status=CHECKIN_STATUS_NORMAL, then=1))),
            ask=Count(Case(When(status__in=[CHECKIN_STATUS_PRIVATE_ASK, CHECKIN_STATUS_PUBLIC_ASK
                , CHECKIN_STATUS_SICK_ASK], then=1))),
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
        res = Checkin.objects.filter(lesson__in=today_start_lessons).filter(time_filter).aggregate(
            normal=Count(Case(When(status=CHECKIN_STATUS_NORMAL, then=1))),
            ask=Count(Case(When(status__in=[CHECKIN_STATUS_PRIVATE_ASK, CHECKIN_STATUS_PUBLIC_ASK,
                                            CHECKIN_STATUS_SICK_ASK], then=1))),
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


@cache_page(600)
def week_data(request):
    data = {}
    now_lesson_time = getnowlessontime()
    now_week = now_lesson_time['week']
    now_term = now_lesson_time['term']

    week_lessons = Lesson.objects.filter(week=now_week, term=now_term)
    data['week_lessons'] = week_lessons.count()
    week_start_lessons = week_lessons.filter(status__in=[LESSON_STATUS_NOW, LESSON_STATUS_CHECKIN,
                                                         LESSON_STATUS_CHECKIN_ADD, LESSON_STATUS_CHECKIN_AGAIN,
                                                         LESSON_STATUS_END])
    data['week_start_lessons'] = week_start_lessons.count()
    week_start_checkin_lessons = week_start_lessons.filter(checkincount__gt=0)
    data['week_start_checkin_lessons'] = week_start_checkin_lessons.count()
    # course_status
    course_status_data = Checkin.objects.filter(lesson__in=week_start_lessons).aggregate(
        normal=Count(Case(When(status=CHECKIN_STATUS_NORMAL, then=1))),
        private_ask=Count(Case(When(status=CHECKIN_STATUS_PRIVATE_ASK, then=1))),
        success=Count(Case(When(status=CHECKIN_STATUS_SUCCESS, then=1))),
        early=Count(Case(When(status=CHECKIN_STATUS_EARLY, then=1))),
        late=Count(Case(When(status=CHECKIN_STATUS_LATE, then=1))),
        lateearly=Count(Case(When(status=CHECKIN_STATUS_LATEEARLY, then=1))),
        public_ask=Count(Case(When(status=CHECKIN_STATUS_PUBLIC_ASK, then=1))),
        sick_ask=Count(Case(When(status=CHECKIN_STATUS_SICK_ASK, then=1))),
    )
    course_status_data['arrive'] = course_status_data['success'] + course_status_data['early'] + \
                                   course_status_data['late'] + course_status_data['lateearly']
    course_status_data['ask'] = course_status_data['private_ask'] + course_status_data['public_ask'] + \
                                course_status_data['sick_ask']

    data['course_status_data'] = course_status_data
    # student_status
    student_all_count = Checkin.objects.filter(lesson__in=week_start_lessons).distinct('student').count()
    student_all_arrive = Checkin.objects.filter(lesson__in=week_start_lessons). \
        annotate(all=Count('status'), num=Count(Case(When(status=CHECKIN_STATUS_SUCCESS, then=1)))).filter(num=F('all'))
    student_all_arrive.query.group_by = 'student'
    student_all_arrive = student_all_arrive.count()
    student_all_normal = Checkin.objects.filter(lesson__in=week_start_lessons). \
        annotate(all=Count('status'), num=Count(Case(When(status=CHECKIN_STATUS_NORMAL, then=1)))).filter(num=F('all'))
    student_all_normal.query.group_by = 'student'
    student_all_normal = student_all_normal.count()
    student_public_ask = Checkin.objects.filter(lesson__in=week_start_lessons).filter(
        status=CHECKIN_STATUS_PUBLIC_ASK).distinct('student').count()
    student_private_ask = Checkin.objects.filter(lesson__in=week_start_lessons).filter(
        status=CHECKIN_STATUS_PRIVATE_ASK).distinct('student').count()
    student_sick_ask = Checkin.objects.filter(lesson__in=week_start_lessons).filter(
        status=CHECKIN_STATUS_SICK_ASK).distinct('student').count()
    student_other = Checkin.objects.filter(lesson__in=week_start_lessons).exclude(
        status__in=[CHECKIN_STATUS_SUCCESS, CHECKIN_STATUS_NORMAL, CHECKIN_STATUS_PUBLIC_ASK,
                    CHECKIN_STATUS_PRIVATE_ASK, CHECKIN_STATUS_SICK_ASK]).distinct('student').count()
    student_late_count = Checkin.objects.filter(lesson__in=week_start_lessons).filter(
        Q(status=CHECKIN_STATUS_LATE) | Q(status=CHECKIN_STATUS_LATEEARLY)).distinct('student').count()
    student_early_count = Checkin.objects.filter(lesson__in=week_start_lessons).filter(
        Q(status=CHECKIN_STATUS_EARLY) | Q(status=CHECKIN_STATUS_LATEEARLY)).distinct('student').count()
    student_normal_count = Checkin.objects.filter(lesson__in=week_start_lessons).filter(
        status=CHECKIN_STATUS_NORMAL).distinct('student').count()
    course_late_count = Checkin.objects.filter(lesson__in=week_start_lessons).filter(
        Q(status=CHECKIN_STATUS_LATE) | Q(status=CHECKIN_STATUS_LATEEARLY)).count()
    course_early_count = Checkin.objects.filter(lesson__in=week_start_lessons).filter(
        Q(status=CHECKIN_STATUS_EARLY) | Q(status=CHECKIN_STATUS_LATEEARLY)).count()
    course_normal_count = Checkin.objects.filter(lesson__in=week_start_lessons).filter(
        status=CHECKIN_STATUS_EARLY).count()
    data.update({'student_all_arrive': student_all_arrive,
                 'student_all_normal': student_all_normal,
                 'student_public_ask': student_public_ask,
                 'student_private_ask': student_private_ask,
                 'student_sick_ask': student_sick_ask,
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
        res = Checkin.objects.filter(lesson__in=week_start_lessons, student__in=d.student_set.all()).aggregate(
            normal=Count(Case(When(status=CHECKIN_STATUS_NORMAL, then=1))),
            ask=Count(Case(When(status__in=[CHECKIN_STATUS_PRIVATE_ASK, CHECKIN_STATUS_PUBLIC_ASK
                , CHECKIN_STATUS_SICK_ASK], then=1))),
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

    # week time status

    weektime_normal_value = []
    weektime_ask_value = []
    weektime_success_value = []
    weektime_late_value = []
    weektime_early_value = []
    weektime_lateearly_value = []
    weektime_arrive_value = []
    for day in range(0, 7):
        res = Checkin.objects.filter(lesson__in=week_start_lessons, lesson__day=day).aggregate(
            normal=Count(Case(When(status=CHECKIN_STATUS_NORMAL, then=1))),
            ask=Count(Case(When(status__in=[CHECKIN_STATUS_PRIVATE_ASK, CHECKIN_STATUS_PUBLIC_ASK,
                                            CHECKIN_STATUS_SICK_ASK], then=1))),
            success=Count(Case(When(status=CHECKIN_STATUS_SUCCESS, then=1))),
            early=Count(Case(When(status=CHECKIN_STATUS_EARLY, then=1))),
            late=Count(Case(When(status=CHECKIN_STATUS_LATE, then=1))),
            lateearly=Count(Case(When(status=CHECKIN_STATUS_LATEEARLY, then=1))),
        )
        weektime_normal_value.append(res['normal'])
        weektime_ask_value.append(res['ask'])
        weektime_success_value.append(res['success'])
        weektime_late_value.append(res['late'])
        weektime_early_value.append(res['early'])
        weektime_lateearly_value.append(res['lateearly'])
        weektime_arrive_value.append(res['lateearly'] + res['early'] + res['late'] + res['success'])
    data.update({'weektime_normal_value': weektime_normal_value,
                 'weektime_ask_value': weektime_ask_value,
                 'weektime_success_value': weektime_success_value,
                 'weektime_late_value': weektime_late_value,
                 'weektime_early_value': weektime_early_value,
                 'weektime_lateearly_value': weektime_lateearly_value,
                 'weektime_arrive_value': weektime_arrive_value})

    return HttpResponse(json.dumps(data), content_type="application/json")


@cache_page(600)
def term_data(request):
    cursor = connection.cursor()
    data = {}
    now_lesson_time = getnowlessontime()
    now_week = now_lesson_time['week']
    now_term = now_lesson_time['term']

    term_lessons = Lesson.objects.filter(term=now_term)
    data['term_lessons'] = term_lessons.count()
    term_start_lessons = term_lessons.filter(status__in=[LESSON_STATUS_NOW, LESSON_STATUS_CHECKIN,
                                                         LESSON_STATUS_CHECKIN_ADD, LESSON_STATUS_CHECKIN_AGAIN,
                                                         LESSON_STATUS_END])
    data['term_start_lessons'] = term_start_lessons.count()
    term_start_checkin_lessons = term_start_lessons.filter(checkincount__gt=0)
    data['term_start_checkin_lessons'] = term_start_checkin_lessons.count()
    # course_status
    course_status_data = Checkin.objects.filter(lesson__in=term_start_lessons).aggregate(
        normal=Count(Case(When(status=CHECKIN_STATUS_NORMAL, then=1))),
        private_ask=Count(Case(When(status=CHECKIN_STATUS_PRIVATE_ASK, then=1))),
        success=Count(Case(When(status=CHECKIN_STATUS_SUCCESS, then=1))),
        early=Count(Case(When(status=CHECKIN_STATUS_EARLY, then=1))),
        late=Count(Case(When(status=CHECKIN_STATUS_LATE, then=1))),
        lateearly=Count(Case(When(status=CHECKIN_STATUS_LATEEARLY, then=1))),
        public_ask=Count(Case(When(status=CHECKIN_STATUS_PUBLIC_ASK, then=1))),
        sick_ask=Count(Case(When(status=CHECKIN_STATUS_SICK_ASK, then=1))),
    )
    course_status_data['arrive'] = course_status_data['success'] + course_status_data['early'] + \
                                   course_status_data['late'] + course_status_data['lateearly']
    course_status_data['ask'] = course_status_data['private_ask'] + course_status_data['public_ask'] + \
                                course_status_data['sick_ask']

    data['course_status_data'] = course_status_data
    # student_status
    student_all_count = Checkin.objects.filter(lesson__in=term_start_lessons).distinct('student').count()
    # can't use because group_by don't work
    # student_all_arrive = Checkin.objects.filter(lesson__in=term_start_lessons). \
    #     annotate(all=Count('status'), num=Count(Case(When(status=CHECKIN_STATUS_SUCCESS, then=1)))).filter(num=F('all'))
    # student_all_arrive.query.group_by = 'student'
    # student_all_arrive = student_all_arrive.count()

    cursor.execute(
        'SELECT COUNT(*) FROM (SELECT "Checkin"."studentid" FROM "Checkin" WHERE "Checkin"."lessonid" IN (SELECT U0."id" AS Col1 FROM "Lesson" U0 WHERE (U0."term" = %s AND U0."status" IN (2, 3, 4, 10, 7))) GROUP BY "Checkin"."studentid" HAVING COUNT(CASE WHEN "Checkin"."status" = %s THEN 1 ELSE NULL END) = (COUNT("Checkin"."status"))) subquery;',
        [now_term, CHECKIN_STATUS_SUCCESS])
    student_all_arrive = cursor.fetchone()[0]
    cursor.execute(
        'SELECT COUNT(*) FROM (SELECT "Checkin"."studentid" FROM "Checkin" WHERE "Checkin"."lessonid" IN (SELECT U0."id" AS Col1 FROM "Lesson" U0 WHERE (U0."term" = %s AND U0."status" IN (2, 3, 4, 10, 7))) GROUP BY "Checkin"."studentid" HAVING COUNT(CASE WHEN "Checkin"."status" = %s THEN 1 ELSE NULL END) = (COUNT("Checkin"."status"))) subquery;',
        [now_term, CHECKIN_STATUS_NORMAL])
    student_all_normal = cursor.fetchone()[0]
    student_public_ask = Checkin.objects.filter(lesson__in=term_start_lessons).filter(
        status=CHECKIN_STATUS_PUBLIC_ASK).distinct('student').count()
    student_private_ask = Checkin.objects.filter(lesson__in=term_start_lessons).filter(
        status=CHECKIN_STATUS_PRIVATE_ASK).distinct('student').count()
    student_sick_ask = Checkin.objects.filter(lesson__in=term_start_lessons).filter(
        status=CHECKIN_STATUS_SICK_ASK).distinct('student').count()
    student_other = Checkin.objects.filter(lesson__in=term_start_lessons).exclude(
        status__in=[CHECKIN_STATUS_SUCCESS, CHECKIN_STATUS_NORMAL, CHECKIN_STATUS_PUBLIC_ASK,
                    CHECKIN_STATUS_PRIVATE_ASK, CHECKIN_STATUS_SICK_ASK]).distinct('student').count()
    student_late_count = Checkin.objects.filter(lesson__in=term_start_lessons).filter(
        Q(status=CHECKIN_STATUS_LATE) | Q(status=CHECKIN_STATUS_LATEEARLY)).distinct('student').count()
    student_early_count = Checkin.objects.filter(lesson__in=term_start_lessons).filter(
        Q(status=CHECKIN_STATUS_EARLY) | Q(status=CHECKIN_STATUS_LATEEARLY)).distinct('student').count()
    student_normal_count = Checkin.objects.filter(lesson__in=term_start_lessons).filter(
        status=CHECKIN_STATUS_NORMAL).distinct('student').count()
    course_late_count = Checkin.objects.filter(lesson__in=term_start_lessons).filter(
        Q(status=CHECKIN_STATUS_LATE) | Q(status=CHECKIN_STATUS_LATEEARLY)).count()
    course_early_count = Checkin.objects.filter(lesson__in=term_start_lessons).filter(
        Q(status=CHECKIN_STATUS_EARLY) | Q(status=CHECKIN_STATUS_LATEEARLY)).count()
    course_normal_count = Checkin.objects.filter(lesson__in=term_start_lessons).filter(
        status=CHECKIN_STATUS_EARLY).count()
    data.update({'student_all_arrive': student_all_arrive,
                 'student_all_normal': student_all_normal,
                 'student_public_ask': student_public_ask,
                 'student_private_ask': student_private_ask,
                 'student_sick_ask': student_sick_ask,
                 'student_other': student_other,
                 'student_late_count': student_late_count,
                 'student_early_count': student_early_count,
                 'course_late_count': course_late_count,
                 'course_early_count': course_early_count,
                 'course_normal_count': course_normal_count,
                 'student_all_count': student_all_count,
                 'student_normal_count': student_normal_count})

    # term time status

    termtime_normal_value = []
    termtime_ask_value = []
    termtime_success_value = []
    termtime_late_value = []
    termtime_early_value = []
    termtime_lateearly_value = []
    termtime_arrive_value = []
    termtime_arrive_ratio = []

    x = []
    for week in range(1, now_week + 1):
        for day in range(0, 7):
            res = Checkin.objects.filter(lesson__in=term_start_lessons, lesson__day=day, lesson__week=week).aggregate(
                normal=Count(Case(When(status=CHECKIN_STATUS_NORMAL, then=1))),
                ask=Count(Case(When(status__in=[CHECKIN_STATUS_PRIVATE_ASK, CHECKIN_STATUS_PUBLIC_ASK,
                                                CHECKIN_STATUS_SICK_ASK], then=1))),
                success=Count(Case(When(status=CHECKIN_STATUS_SUCCESS, then=1))),
                early=Count(Case(When(status=CHECKIN_STATUS_EARLY, then=1))),
                late=Count(Case(When(status=CHECKIN_STATUS_LATE, then=1))),
                lateearly=Count(Case(When(status=CHECKIN_STATUS_LATEEARLY, then=1))),
            )
            if res['lateearly'] + res['early'] + res['late'] + res['success'] == 0:
                continue
            termtime_normal_value.append(res['normal'])
            termtime_ask_value.append(res['ask'])
            termtime_success_value.append(res['success'])
            termtime_late_value.append(res['late'])
            termtime_early_value.append(res['early'])
            termtime_lateearly_value.append(res['lateearly'])
            arrive_count = res['lateearly'] + res['early'] + res['late'] + res['success']
            should_count = arrive_count + res['normal']
            termtime_arrive_value.append(arrive_count)
            termtime_arrive_ratio.append(int(arrive_count * 100.0 / should_count))
            x.append("%d-%d" % (week, day))
    data.update({'xAxis': x,
                 'termtime_normal_value': termtime_normal_value,
                 'termtime_ask_value': termtime_ask_value,
                 'termtime_success_value': termtime_success_value,
                 'termtime_late_value': termtime_late_value,
                 'termtime_early_value': termtime_early_value,
                 'termtime_lateearly_value': termtime_lateearly_value,
                 'termtime_arrive_ratio': termtime_arrive_ratio,
                 'termtime_arrive_value': termtime_arrive_value})

    return HttpResponse(json.dumps(data), content_type="application/json")


@permission_required(permission='checkin_view')
@cache_page(60)
def lesson_data(request):
    now_lesson_time = getnowlessontime()
    now_week = now_lesson_time['week']
    now_day = now_lesson_time['day']
    now_time = now_lesson_time['time']
    now_term = now_lesson_time['term']
    today_lessons = Lesson.objects.filter(week=now_week, day=now_day, term=now_term)
    checkindata = Checkin.objects.filter(lesson=OuterRef('id')).values('lesson_id').annotate(count=Count('*')).values(
        'count')
    today_lessons = today_lessons.select_related('course').select_related('classroom').select_related(
        'course__department')
    today_lessons = today_lessons.annotate(
        actually=Subquery(checkindata.filter(
            status__in=[CHECKIN_STATUS_EARLY, CHECKIN_STATUS_SUCCESS, CHECKIN_STATUS_LATE, CHECKIN_STATUS_LATEEARLY]),
            output_field=IntegerField()),
        late=Subquery(checkindata.filter(status=CHECKIN_STATUS_LATE), output_field=IntegerField()),
        early=Subquery(checkindata.filter(status=CHECKIN_STATUS_EARLY), output_field=IntegerField()),
        late_early=Subquery(checkindata.filter(status=CHECKIN_STATUS_LATEEARLY), output_field=IntegerField()),
        should=Subquery(checkindata, output_field=IntegerField()),
        ask=Subquery(checkindata.filter(status__gte=10), output_field=IntegerField()),
    )

    rows = []
    for p in today_lessons.all():
        ld = {
            'id': p.id,
            'serialnumber': p.course.serialnumber,
            'title': p.course.title,
            'time': "%d-%d" % (p.time, p.time + p.length - 1),
            'location': p.classroom.location,
            'teacher': ",".join(p.course.teachers.values_list('name', flat=True)),
            'teach_class': p.course.teachclass.name if p.course.teachclass else None,
            'department': p.course.department.name if p.course.department else None,
            'should': p.should if p.isnow() or p.isend() else p.shouldnumber,
            'actually': p.actually,
            'late': p.late,
            'early': p.early,
            'late_early': p.late_early,
            'asknumber': p.asknumber if p.checkincount else p.ask,
            'attendance': "%.2f%%" % (p.actually / p.shouldnumber * 100) if p.actually else None,
            'checkincount': p.checkincount,
            'status': p.status,
            'starttime': datetime.datetime.strftime(p.starttime, '%Y-%m-%d %I:%M %p') if p.starttime else None,
            'endtime': datetime.datetime.strftime(p.endtime, '%Y-%m-%d %I:%M %p') if p.endtime else None,
        }
        rows.append(ld)
    return HttpResponse(json.dumps(rows), content_type="application/json")
