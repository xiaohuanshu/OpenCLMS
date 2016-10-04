# -*- coding: utf-8 -*-
from course.models import Course, Lesson, Studentcourse
from course.constant import *
from django.core.exceptions import ObjectDoesNotExist
from models import Checkin, Checkinrecord
from constant import *
from django.db.models import F, Q
import time, os
from django.core.cache import cache


def startcheckin(lessonid, mode='first'):
    try:
        lesson = Lesson.objects.get(id=lessonid)
    except ObjectDoesNotExist:
        return {'error': 101, 'message': '课程不存在'}
    if lesson.status == LESSON_STATUS_AWAIT:
        return {'error': 101, 'message': '课程还未开始'}
    elif lesson.status == LESSON_STATUS_CANCLE:
        return {'error': 101, 'message': '课程被取消'}
    elif lesson.status == LESSON_STATUS_END or lesson.status == LESSON_STATUS_END_EARLY or lesson.status == LESSON_STATUS_START_LATE:
        return {'error': 101, 'message': '课程已结束'}
    elif lesson.status == LESSON_STATUS_WRONG:
        return {'error': 101, 'message': '课程未正常开启'}

    if (mode == 'first' and lesson.status == LESSON_STATUS_CHECKIN) or (
                    mode == 'again' and lesson.status == LESSON_STATUS_CHECKIN_AGAIN) or (
                    mode == 'add' and lesson.status == LESSON_STATUS_CHECKIN_ADD):
        return {'error': 0, 'message': '课程正在签到'}
    lesson.checkincount = (lesson.checkincount and [lesson.checkincount] or [0])[0] + 1
    checkin_record = Checkinrecord()
    nowtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

    if mode == 'first':
        if lesson.status == LESSON_STATUS_CHECKIN:
            return {'error': 0, 'message': '课程正在签到'}
        if not lesson.checkincount == 1:
            return {'error': 101, 'message': '不能进行首签模式'}
        lesson.status = LESSON_STATUS_CHECKIN
        checkin_record.status = CHECKIN_RECORD_FIRST
        '''
        nowstudent = Checkin.objects.filter(lesson=lesson).values_list('student', flat=True)
        studentcourse = Studentcourse.objects.filter(course=lesson.course).exclude(student__in=nowstudent)
        #Checkin.objects.create(lesson=lesson, status=CHECKIN_STATUS_NORMAL, student__in=studentcourse.values_list('student',flat=True))
        newstudent = []
        for s in studentcourse:
            newstudent.append(
                Checkin(lesson=lesson, status=CHECKIN_STATUS_NORMAL, student=s.student))
        Checkin.objects.bulk_create(newstudent)
        '''

    if mode == 'add':
        if lesson.checkincount == 1:
            return {'error': 101, 'message': '不能进行补签模式'}
        lesson.status = LESSON_STATUS_CHECKIN_ADD
        checkin_record.status = CHECKIN_RECORD_ADD
        Checkin.objects.filter(lesson=lesson).exclude(status=CHECKIN_STATUS_ASK).update(laststatus=F('status'))

    if mode == 'again':
        if lesson.checkincount == 1:
            return {'error': 101, 'message': '不能进行再签模式'}
        lesson.status = LESSON_STATUS_CHECKIN_AGAIN
        checkin_record.status = CHECKIN_RECORD_AGAIN
        Checkin.objects.filter(lesson=lesson).exclude(status=CHECKIN_STATUS_ASK).update(
            laststatus=F('status'), status=CHECKIN_STATUS_NORMAL)

    checkin_record.lesson = lesson
    checkin_record.starttime = nowtime
    checkin_record.time = lesson.checkincount
    checkin_record.shouldnumber = lesson.shouldnumber()
    lesson.save()
    checkin_record.save()

    return {'error': 0}


def endcheckin(lessonid):
    try:
        lesson = Lesson.objects.get(id=lessonid)
    except ObjectDoesNotExist:
        return {'error': 101, 'message': '课程不存在'}
    if not lesson.status == LESSON_STATUS_CHECKIN and not lesson.status == LESSON_STATUS_CHECKIN_ADD and not lesson.status == LESSON_STATUS_CHECKIN_AGAIN:
        return {'error': 101, 'message': '课程未开始签到'}
    nowtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    checkin_record = Checkinrecord.objects.filter(lesson=lesson).order_by('-time').first()
    checkin_status = checkin_record.status
    lesson.status = LESSON_STATUS_NOW
    checkin_record.status = CHECKIN_RECORD_END
    checkin_record.endtime = nowtime
    lesson.save()
    # 人员统计计算过程
    if checkin_status == CHECKIN_RECORD_FIRST:
        checkin_record.actuallynumber = lesson.actuallynumber()
        checkin_record.newnumber = checkin_record.actuallynumber
        checkin_record.leavenumber = 0
    elif checkin_status == CHECKIN_RECORD_ADD:
        checkin_record.actuallynumber = lesson.actuallynumber()
        checkin_record.newnumber = Checkin.objects.filter(lesson=lesson, laststatus=CHECKIN_STATUS_NORMAL,
                                                          status=CHECKIN_STATUS_LATE).count()
        checkin_record.leavenumber = 0
    elif checkin_status == CHECKIN_RECORD_AGAIN:
        checkin_record.actuallynumber = lesson.actuallynumber()
        checkin_record.newnumber = Checkin.objects.filter(lesson=lesson, laststatus=CHECKIN_STATUS_NORMAL,
                                                          status=CHECKIN_STATUS_LATE).count()
        checkin_record.leavenumber = Checkin.objects.filter(lesson=lesson, status=CHECKIN_STATUS_NORMAL).filter(
            Q(laststatus=CHECKIN_STATUS_LATE) | Q(laststatus=CHECKIN_STATUS_SUCCESS)).count()
        Checkin.objects.filter(lesson=lesson, status=CHECKIN_STATUS_NORMAL).filter(
            laststatus=CHECKIN_STATUS_LATE).update(status=CHECKIN_STATUS_LATEEARLY)
        Checkin.objects.filter(lesson=lesson, status=CHECKIN_STATUS_NORMAL).filter(
            laststatus=CHECKIN_STATUS_SUCCESS).update(status=CHECKIN_STATUS_EARLY)

    checkin_record.save()
    return {'error': 0}


def clear_checkin(lessonid):
    try:
        lesson = Lesson.objects.get(id=lessonid)
    except ObjectDoesNotExist:
        return {'error': 101, 'message': '课程不存在'}
    if lesson.status == LESSON_STATUS_AWAIT:
        return {'error': 101, 'message': '课程还未开始'}
    Checkinrecord.objects.filter(lesson=lesson).all().delete()
    Checkin.objects.filter(lesson=lesson).all().delete()
    lesson.status = LESSON_STATUS_NOW
    lesson.checkincount = 0
    lesson.save()


def clear_last_checkin(lessonid):
    try:
        lesson = Lesson.objects.get(id=lessonid)
    except ObjectDoesNotExist:
        return {'error': 101, 'message': '课程不存在'}
    if not lesson.status == LESSON_STATUS_CHECKIN and not lesson.status == LESSON_STATUS_CHECKIN_ADD and not lesson.status == LESSON_STATUS_CHECKIN_AGAIN:
        return {'error': 101, 'message': '课程未开始签到'}
    Checkinrecord.objects.filter(lesson=lesson).order_by('-time').first().delete()
    if lesson.checkincount == 1:
        Checkin.objects.filter(lesson=lesson).delete()
    else:
        Checkin.objects.filter(lesson=lesson).update(status=F('laststatus'))
    lesson.checkincount -= 1
    lesson.status = LESSON_STATUS_NOW
    lesson.save()


def student_checkin(student, lesson):
    checkin = Checkin.objects.get(lesson=lesson, student=student)
    # checkindata.seatid = seatid
    nowtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    if checkin.status == CHECKIN_STATUS_ASK:
        return {'error': 101, 'message': '学生已经请假'}
    if not checkin.time:
        checkin.time = nowtime
    if lesson.status == LESSON_STATUS_CHECKIN:
        if checkin.status == CHECKIN_STATUS_NORMAL:
            checkin.status = CHECKIN_STATUS_SUCCESS
    elif lesson.status == LESSON_STATUS_CHECKIN_ADD:
        if checkin.status == CHECKIN_STATUS_NORMAL:
            checkin.status = CHECKIN_STATUS_LATE
        elif checkin.status == CHECKIN_STATUS_EARLY:
            checkin.status = CHECKIN_STATUS_SUCCESS
        elif checkin.status == CHECKIN_STATUS_LATEEARLY:
            checkin.status = CHECKIN_STATUS_LATE
    elif lesson.status == LESSON_STATUS_CHECKIN_AGAIN:
        if checkin.laststatus == CHECKIN_STATUS_NORMAL:
            checkin.status = CHECKIN_STATUS_LATE
        elif checkin.laststatus == CHECKIN_STATUS_LATE:
            checkin.status = CHECKIN_STATUS_LATE
        elif checkin.laststatus == CHECKIN_STATUS_EARLY:
            checkin.status = CHECKIN_STATUS_SUCCESS
        elif checkin.laststatus == CHECKIN_STATUS_LATEEARLY:
            checkin.status = CHECKIN_STATUS_LATE
        elif checkin.status == CHECKIN_STATUS_NORMAL:
            checkin.status = CHECKIN_STATUS_SUCCESS
    checkin.save()
    return {'error': 0, 'status': checkin.status}


def generateqrstr(lessonid):
    qrstr = str(lessonid).join(map(lambda xx:(hex(ord(xx))[2:]),os.urandom(2)))
    cache.set("qr%s" % (qrstr), lessonid, 20)
    return qrstr
