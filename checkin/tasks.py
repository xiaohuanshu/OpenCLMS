# -*- coding: utf-8 -*-
from school.function import getnowlessontime, day_to_week_string
from course.models import Lesson
from models import Checkin
from django.db.models import Count, Case, When, Q, F, OuterRef, Subquery, IntegerField
from checkin.constant import *
import xlsxwriter
import datetime
from celery import shared_task
from django.conf import settings
from checkin.models import CheckinHistory, DailySubscibe
from django.core.mail import EmailMessage
import logging

logger = logging.getLogger(__name__)


@shared_task(name='generate_checkin_daily_excel')
def generate_checkin_daily_excel():
    now_lesson_time = getnowlessontime()
    now_week = now_lesson_time['week']
    now_day = now_lesson_time['day']
    now_term = now_lesson_time['term']
    today_lessons = Lesson.objects.filter(week=now_week, day=now_day, term=now_term)
    count = today_lessons.count()
    if count == 0:
        return
    name = "daily/%s.xlsx" % datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')
    workbook = xlsxwriter.Workbook(settings.MEDIA_ROOT + '/' + name)
    worksheet = workbook.add_worksheet()
    other = workbook.add_format({'bold': True, 'fg_color': '#D7E4BC'})
    date_format = workbook.add_format({'bold': True, 'fg_color': '#D7E4BC', 'num_format': 'yyyy-mm-dd'})
    merge_format = workbook.add_format({
        'bold': True,
        'font_size': 20,
        'align': 'center',
        'valign': 'vcenter',
        'fg_color': '#D7E4BC',
    })
    worksheet.merge_range('A1:N1', settings.SCHOOL_NAME + u'每日考勤记录', merge_format)
    worksheet.write('A2', now_term + u'学期', other)
    worksheet.write('B2', u'第%d周' % now_week, other)
    day_string = day_to_week_string(now_day)
    worksheet.write('C2', day_string, other)
    worksheet.merge_range('D2:K2', '', other)
    worksheet.merge_range('L2:N2', datetime.datetime.now(), date_format)

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

    row_offset = 2
    columns = [
        {'header': u'课程名称'},
        {'header': u'课程编号'},
        {'header': u'时间'},
        {'header': u'教师'},
        {'header': u'教学班'},
        {'header': u'开课院系'},
        {'header': u'应到'},
        {'header': u'实到'},
        {'header': u'迟到'},
        {'header': u'早退'},
        {'header': u'迟&早'},
        {'header': u'请假'},
        {'header': u'出勤率', 'format': workbook.add_format({'num_format': '0.00%'})},
        {'header': u'签到次数'},
    ]
    data = []
    for index, p in enumerate(today_lessons.all()):
        data.append([
            p.course.title,
            p.course.serialnumber,
            "%d-%d" % (p.time, p.time + p.length - 1),
            ",".join(p.course.teachers.values_list('name', flat=True)),
            p.course.teachclass.name if p.course.teachclass else None,
            p.course.department.name if p.course.department else None,
            p.should if p.isnow() or p.isend() else p.shouldnumber,
            p.actually if p.actually else 0,
            p.late if p.late else 0,
            p.early if p.early else 0,
            p.late_early if p.late_early else 0,
            p.asknumber if p.checkincount else p.ask,
            (p.actually * 1.0 / p.shouldnumber) if p.actually else None,
            p.checkincount if p.checkincount else 0
        ])

    worksheet.add_table(row_offset, 0, row_offset + count, 13,
                        {'data': data, 'columns': columns, 'style': 'Table Style Light 11'})
    worksheet.set_column('A:A', 34)
    worksheet.set_column('B:B', 33)
    worksheet.set_column('C:C', 6)
    worksheet.set_column('D:D', 12)
    worksheet.set_column('E:E', 14)
    worksheet.set_column('F:F', 17)
    worksheet.set_column('G:L', 5.83)
    worksheet.set_column('M:M', 7.83)
    worksheet.set_column('N:N', 9.83)
    workbook.close()
    ch = CheckinHistory(term=now_term, day=now_day, week=now_week, course_count=count)
    ch.file.name = name
    ch.save()

    logger.info("[generate_checkin_daily_excel] Successful generate")
    emails = DailySubscibe.objects.values_list('user__email', flat=True)
    if len(emails) > 0:
        email = EmailMessage(
            u'【checkinsystem】%s学期 第%d周 %s 考勤数据' % (now_term, now_week, day_string),
            u'自动发送，请勿回复此邮件',
            settings.SERVER_EMAIL,
            emails,
        )
        email.attach_file(ch.file.path)
        email.send(fail_silently=True)
        logger.info("[generate_checkin_daily_excel] Successful send email")

    return name
