# -*- coding: utf-8 -*-
import json
from django.core.cache import cache
from django.http import HttpResponse
from course.models import Lesson, Studentcourse
from course.constant import *
from checkin.constant import *
from django.shortcuts import redirect, render
from django.core.urlresolvers import reverse
from function import startcheckin, endcheckin, student_checkin, generateqrstr, addaskinformationinstartedlesson, \
    delaskinformationinstartedlesson, clear_checkin, clear_last_checkin
from models import Checkin, Ask, Asktostudent
from user_system.models import User
from school.models import Student
from django.db.models import ObjectDoesNotExist, Q
from course.auth import has_course_permission
import datetime
from school.function import getCurrentSchoolYearTerm
from user_system.auth import permission_required


def getqrstr(request, lessonid):
    lesson = Lesson.objects.get(id=lessonid)
    if not (has_course_permission(request.user, lesson.course) or request.user.has_perm('course_control')):
        return HttpResponse(json.dumps({'error': 101, 'message': '没有权限'}), content_type="application/json")
    str = generateqrstr(lessonid)
    data = {'qr': str}
    return HttpResponse(json.dumps(data), content_type="application/json")


def getcheckinnowdata(request, lessonid):
    lesson = Lesson.objects.get(id=lessonid)
    checkindata = Checkin.objects.filter(lesson=lesson).only('student__studentid', 'status', 'abnormal').all()
    checkinnowdata = []
    for cnd in checkindata:
        checkinnowdata.append({"studentid": cnd.student_id, "status": cnd.status, 'abnormal': cnd.abnormal})
    shoudnumber = lesson.shouldnumber
    actuallynumber = lesson.actuallynumber
    data = {'should': shoudnumber, 'actually': actuallynumber, 'rows': checkinnowdata}
    return HttpResponse(json.dumps(data), content_type="application/json")


def changecheckinstatus(request, lessonid):
    lesson = Lesson.objects.get(id=lessonid)
    studentid = request.GET.get('studentid', default=False) or request.GET.get('pk')
    newstatus = request.GET.get('newstatus', default=False) or request.GET.get('value')
    try:
        student = Student.objects.get(studentid=studentid)
    except ObjectDoesNotExist:
        return HttpResponse(json.dumps({'error': 101, 'message': '未找到，请输入正确的学号'}), content_type="application/json")
    if not (has_course_permission(request.user, lesson.course) or request.user.has_perm('checkin_modify')):
        return HttpResponse(json.dumps({'error': 101, 'message': '没有权限'}), content_type="application/json")
    try:
        checkin = Checkin.objects.get(student=student, lesson=lesson)
    except ObjectDoesNotExist:
        if not Studentcourse.objects.filter(course=lesson.course, student=student).exists():
            Studentcourse.objects.create(course=lesson.course, student=student)
        checkin = Checkin(student=student, lesson=lesson)
    """ 关闭请假不允许修改功能
    if checkin.status > 10:  # ASK
        return HttpResponse(json.dumps({'error': 101, 'message': '学生已经请假'}), content_type="application/json")
    """
    if newstatus == 'newcheckin':
        data = student_checkin(student, lesson)
    elif newstatus == 'delete':
        checkin.status = CHECKIN_STATUS_NORMAL
        checkin.save()
        data = {'studentid': studentid, 'status': checkin.status}
    elif newstatus == 'late':
        checkin.status = CHECKIN_STATUS_LATE
        checkin.save()
        data = {'studentid': studentid, 'status': checkin.status}
    elif newstatus == 'success':
        checkin.status = CHECKIN_STATUS_SUCCESS
        checkin.save()
        data = {'studentid': studentid, 'status': checkin.status}
    elif newstatus == 'early':
        checkin.status = CHECKIN_STATUS_EARLY
        checkin.save()
        data = {'studentid': studentid, 'status': checkin.status}
    elif newstatus == 'lateearly':
        checkin.status = CHECKIN_STATUS_LATEEARLY
        checkin.save()
        data = {'studentid': studentid, 'status': checkin.status}
    elif newstatus == 'private_ask':
        checkin.status = CHECKIN_STATUS_PRIVATE_ASK
        checkin.save()
        data = {'studentid': studentid, 'status': checkin.status}
    elif newstatus == 'public_ask':
        checkin.status = CHECKIN_STATUS_PRIVATE_ASK
        checkin.save()
        data = {'studentid': studentid, 'status': checkin.status}
    elif newstatus == 'sick_ask':
        checkin.status = CHECKIN_STATUS_SICK_ASK
        checkin.save()
        data = {'studentid': studentid, 'status': checkin.status}
    elif newstatus.isdigit():
        checkin.status = newstatus
        checkin.save()
        data = {'studentid': studentid, 'status': checkin.status}
    return HttpResponse(json.dumps(data), content_type="application/json")


def ck(request, qr_str):
    agent = request.META.get('HTTP_USER_AGENT', None)
    if "MicroMessenger" not in agent:
        return render(request, 'error.html', {'message': u'签到失败', 'submessage': u'请在微信中打开此链接'})
    lessonid = cache.get("qr%s" % (qr_str), default=None)
    if not lessonid:
        return render(request, 'error.html',
                      {'message': u'签到失败', 'submessage': u'二维码失效或不存在', 'wechatclose': True})
    lesson = Lesson.objects.get(id=lessonid)
    try:
        student = Student.objects.get(user=request.user)
    except ObjectDoesNotExist:
        return render(request, 'error.html',
                      {'message': u'签到失败', 'submessage': u'您的身份不是学生', 'wechatclose': True})
    if not Studentcourse.objects.filter(course=lesson.course, student=student).exists():
        return render(request, 'error.html',
                      {'message': u'签到失败', 'submessage': u'上课名单中没有你', 'wechatclose': True})
    else:
        if request.user.checkinaccountabnormal:
            abnormal = CHECKIN_ABNORMAL_ACCOUNT
            request.user.checkinaccountabnormal = False
            request.user.save()
        else:
            abnormal = None
        re = student_checkin(student, lesson, abnormal)
        if re['error'] != 0:
            return render(request, 'error.html', {'message': re['message'], 'submessage': lesson.course.title,
                                                  'wechatclose': True})
        return render(request, 'checkin_success.html',
                      {
                          'coursename': lesson.course.title,
                          'studentname': student.name,
                          'status': re['status'],
                          'courseid': lesson.course_id,
                          'checkinid': re['checkin_id']
                      })


def get_position(request):
    checkin_id = request.GET.get('checkinid')
    try:
        checkindata = Checkin.objects.get(pk=checkin_id)
    except ObjectDoesNotExist:
        return HttpResponse(json.dumps({'error': 101, 'message': "checkin not found"}), content_type="application/json")
    try:
        student = Student.objects.get(user=request.user)
    except ObjectDoesNotExist:
        return HttpResponse(json.dumps({'error': 101, 'message': "student not found"}), content_type="application/json")
    if student != checkindata.student:
        return HttpResponse(json.dumps({'error': 101, 'message': "student not match"}), content_type="application/json")
    latitude = request.GET.get('latitude')
    longitude = request.GET.get('longitude')
    accuracy = request.GET.get('accuracy')
    checkindata.positionaccuracy = accuracy
    checkindata.positionlatitude = latitude
    checkindata.positionlongitude = longitude
    checkindata.save()
    return HttpResponse(json.dumps({'error': 0, 'message': "success!"}), content_type="application/json")


def startCheckin(request, lessonid):
    lesson = Lesson.objects.get(id=lessonid)
    if not has_course_permission(request.user, lesson.course):
        return render(request, 'error.html', {'message': '没有权限'})
    mode = request.GET.get('mode', default='first')
    if lesson.status == LESSON_STATUS_AWAIT:
        return render(request, 'error.html',
                      {'message': '课程还未开始',
                       'submessage': lesson.course.title,
                       'jumpurl': str(
                           reverse('course:information', args=[lesson.course.id]))})
    elif lesson.status == LESSON_STATUS_NOW:
        re = startcheckin(lessonid, mode)
        if re['error'] != 0:
            return render(request, 'error.html', {'message': re['message'], 'submessage': lesson.course.title})
        return redirect(reverse('checkin:qrcheckin', args=[lessonid]))
    elif lesson.status in (LESSON_STATUS_CHECKIN, LESSON_STATUS_CHECKIN_ADD, LESSON_STATUS_CHECKIN_AGAIN):
        return redirect(reverse('checkin:qrcheckin', args=[lessonid]))
    return render(request, 'error.html',
                  {'message': '开始签到失败',
                   'submessage': lesson.course.title,
                   'jumpurl': str(
                       reverse('course:information', args=[lesson.course.id]))})


def stopCheckin(request, lessonid):
    lesson = Lesson.objects.get(id=lessonid)
    if not has_course_permission(request.user, lesson.course):
        return render(request, 'error.html', {'message': '没有权限'})
    if lesson.status in (LESSON_STATUS_CHECKIN, LESSON_STATUS_CHECKIN_ADD, LESSON_STATUS_CHECKIN_AGAIN):
        re = endcheckin(lessonid)
        if re['error'] != 0:
            return render(request, 'error.html',
                          {'message': re['message'],
                           'submessage': lesson.course.title,
                           'jumpurl': str(
                               reverse('course:information', args=[lesson.course.id]))})
    # checkin_start(lessonruntimeid)
    return redirect(reverse('checkin:lesson_data', args=[lesson.id]))


def addask(request):
    student = request.GET.getlist('students[]', default=False)
    starttime = datetime.datetime.strptime(request.GET.get('starttime', default=False), "%Y-%m-%d %I:%M %p")
    endtime = datetime.datetime.strptime(request.GET.get('endtime', default=False), "%Y-%m-%d %I:%M %p")
    reason = request.GET.get('reason', default='')
    typedata = {u'公假': CHECKIN_STATUS_PUBLIC_ASK, u'事假': CHECKIN_STATUS_PRIVATE_ASK, u'病假': CHECKIN_STATUS_SICK_ASK}
    type = typedata[request.GET.get('type')]
    schoolterm = getCurrentSchoolYearTerm()['term']
    students = Student.objects.in_bulk(student)

    if (Ask.objects.filter(student__in=students, schoolterm=schoolterm).filter(
                Q(starttime__range=(starttime, endtime)) | Q(endtime__range=(starttime, endtime))).exists()):
        return HttpResponse(json.dumps({'error': 101, 'message': "部分学生在此时间段内有请假信息,时间冲突!"}),
                            content_type="application/json")
    ask = Ask()
    ask.starttime = starttime
    ask.endtime = endtime
    ask.reason = reason
    ask.type = type
    if request.user.has_perm('checkin_ask_approve'):
        ask.status = ASK_STATUS_APPROVE
        ask.operater = request.user
        for s in students:
            addaskinformationinstartedlesson(s, starttime, endtime, type)
    else:
        ask.status = ASK_STATUS_WAITING
    ask.schoolterm = schoolterm

    ask.save()
    querysetlist = []
    for i in students:
        s = students[i]
        querysetlist.append(Asktostudent(ask=ask, student=s))
    Asktostudent.objects.bulk_create(querysetlist)
    data = {'error': 0, 'message': '添加成功', 'status': ask.status, 'askid': ask.id}
    return HttpResponse(json.dumps(data), content_type="application/json")


@permission_required(permission='checkin_ask_modify')
def delask(request):
    ask = Ask.objects.get(id=request.GET.get('askid'))
    asktostudents = Asktostudent.objects.filter(ask=ask)
    starttime = ask.starttime
    endtime = ask.endtime
    for a in asktostudents:
        delaskinformationinstartedlesson(a.student, starttime, endtime)
    asktostudents.delete()
    ask.delete()
    data = {'error': 0, 'message': '删除成功', 'status': ask.status}
    return HttpResponse(json.dumps(data), content_type="application/json")


def clearcheckin(request, lessonid):
    lesson = Lesson.objects.get(id=lessonid)
    if not has_course_permission(request.user, lesson.course):
        return render(request, 'error.html', {'message': '没有权限'})
    if request.GET.get('deleteall', 0):
        clear_checkin(lesson)
    elif request.GET.get('deletethis', 0):
        if lesson.ischeckinnow():
            clear_last_checkin(lesson)
            cache.delete('lesson_%d_clear_flag' % lesson.id)
        elif cache.get('lesson_%d_clear_flag' % lesson.id, default=False):
            clear_last_checkin(lesson)
            cache.delete('lesson_%d_clear_flag' % lesson.id)
        else:
            return render(request, 'error.html', {'message': '无法清除', 'submessage': '间隔时间太久'})
    return redirect(reverse('checkin:lesson_data', args=[lesson.id]))
