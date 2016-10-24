# -*- coding: utf-8 -*-
import json
from django.core.cache import cache
from django.http import HttpResponse
from course.models import Lesson, Studentcourse
from course.constant import *
from checkin.constant import *
from django.shortcuts import redirect, HttpResponseRedirect, render, render_to_response, RequestContext
from django.core.urlresolvers import reverse
from function import startcheckin, endcheckin, student_checkin, generateqrstr, addaskinformationinstartedlesson, \
    delaskinformationinstartedlesson, clear_checkin, clear_last_checkin
from models import Checkin, Ask, Asktostudent
from user.models import User
from school.models import Student
from django.db.models import ObjectDoesNotExist, Q
from course.auth import has_course_permission
import datetime
from school.function import getCurrentSchoolYearTerm
from user.auth import permission_required


def getqrstr(request, lessonid):
    lesson = Lesson.objects.get(id=lessonid)
    if not (has_course_permission(request.user, lesson.course) or request.user.has_perm('course_control')):
        return HttpResponse(json.dumps({'error': 101, 'message': '没有权限'}), content_type="application/json")
    str = generateqrstr(lessonid)
    data = {'qr': str}
    return HttpResponse(json.dumps(data), content_type="application/json")


def getcheckinnowdata(request, lessonid):
    lesson = Lesson.objects.get(id=lessonid)
    checkindata = Checkin.objects.filter(lesson=lesson).select_related('student').only('student__studentid',
                                                                                       'status').all()
    checkinnowdata = []
    for cnd in checkindata:
        checkinnowdata.append({"studentid": cnd.student.studentid, "status": cnd.status})
    shoudnumber = lesson.shouldnumber()
    actuallynumber = lesson.actuallynumber()
    data = {'should': shoudnumber, 'actually': actuallynumber, 'rows': checkinnowdata}
    return HttpResponse(json.dumps(data), content_type="application/json")


def changecheckinstatus(request, lessonid):
    lesson = Lesson.objects.get(id=lessonid)
    studentid = request.GET.get('studentid', default=False) or request.GET.get('pk')
    newstatus = request.GET.get('newstatus', default=False) or request.GET.get('value')
    student = Student.objects.get(studentid=studentid)
    if not (has_course_permission(request.user, lesson.course) or request.user.has_perm('checkin_modify')):
        return HttpResponse(json.dumps({'error': 101, 'message': '没有权限'}), content_type="application/json")
    try:
        checkin = Checkin.objects.get(student=student, lesson=lesson)
    except ObjectDoesNotExist:
        if Studentcourse.objects.filter(course=lesson.course, student=student).exists():
            checkin = Checkin(student=student, lesson=lesson)
        else:
            return HttpResponse(json.dumps({'error': 101, 'message': '学生没有此课'}), content_type="application/json")
    if checkin.status > 10:  # ASK
        return HttpResponse(json.dumps({'error': 101, 'message': '学生已经请假'}), content_type="application/json")
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
    elif newstatus.isdigit():
        checkin.status = newstatus
        checkin.save()
        data = {'studentid': studentid, 'status': checkin.status}
    return HttpResponse(json.dumps(data), content_type="application/json")


def ck(request, qr_str):
    agent = request.META.get('HTTP_USER_AGENT', None)
    if "MicroMessenger" not in agent:
        return render_to_response('error.html', {'message': u'签到失败', 'submessage': u'请在微信中打开此链接'},
                                  context_instance=RequestContext(request))
    lessonid = cache.get("qr%s" % (qr_str), default=None)
    if not lessonid:
        return render_to_response('error.html', {'message': u'签到失败', 'submessage': u'二维码失效或不存在', 'wechatclose': True},
                                  context_instance=RequestContext(request))
    lesson = Lesson.objects.get(id=lessonid)
    user = User.objects.get(id=request.session.get('userid'))
    student = Student.objects.get(user=user)
    if not Studentcourse.objects.filter(course=lesson.course, student=student).exists():
        return render_to_response('error.html', {'message': u'签到失败', 'submessage': u'上课名单中没有你', 'wechatclose': True},
                                  context_instance=RequestContext(request))
    else:
        re = student_checkin(student, lesson)
        if re['error'] != 0:
            return render_to_response('error.html', {'message': re['message'], 'submessage': lesson.course.title,
                                                     'wechatclose': True}, context_instance=RequestContext(request))
        return render_to_response('success.html',
                                  {'message': u'签到成功', 'submessage': lesson.course.title, 'wechatclose': True},
                                  context_instance=RequestContext(request))


def startCheckin(request, lessonid):
    lesson = Lesson.objects.get(id=lessonid)
    if not has_course_permission(request.user, lesson.course):
        return render_to_response('error.html',
                                  {'message': '没有权限'},
                                  context_instance=RequestContext(request))
    mode = request.GET.get('mode', default='first')
    if lesson.status == LESSON_STATUS_AWAIT:
        return render_to_response('error.html',
                                  {'message': '课程还未开始',
                                   'submessage': lesson.course.title,
                                   'jumpurl': str(
                                       reverse('course:information', args=[lesson.course.id]))},
                                  context_instance=RequestContext(request))
    elif lesson.status == LESSON_STATUS_NOW:
        re = startcheckin(lessonid, mode)
        if re['error'] != 0:
            return render_to_response('error.html', {'message': re['message'], 'submessage': lesson.course.title},
                                      context_instance=RequestContext(request))
        return redirect(reverse('checkin:qrcheckin', args=[lessonid]))
    elif lesson.status == LESSON_STATUS_CHECKIN or lesson.status == LESSON_STATUS_CHECKIN_ADD or lesson.status == LESSON_STATUS_CHECKIN_AGAIN:
        return redirect(reverse('checkin:qrcheckin', args=[lessonid]))
    return render_to_response('error.html',
                              {'message': '开始签到失败',
                               'submessage': lesson.course.title,
                               'jumpurl': str(
                                   reverse('course:information', args=[lesson.course.id]))},
                              context_instance=RequestContext(request))


def stopCheckin(request, lessonid):
    lesson = Lesson.objects.get(id=lessonid)
    if not has_course_permission(request.user, lesson.course):
        return render_to_response('error.html',
                                  {'message': '没有权限'},
                                  context_instance=RequestContext(request))
    if lesson.status == LESSON_STATUS_CHECKIN or lesson.status == LESSON_STATUS_CHECKIN_ADD or lesson.status == LESSON_STATUS_CHECKIN_AGAIN:
        re = endcheckin(lessonid)
        if re['error'] != 0:
            return render_to_response('error.html',
                                      {'message': re['message'],
                                       'submessage': lesson.course.title,
                                       'jumpurl': str(
                                           reverse('course:information', args=[lesson.course.id]))},
                                      context_instance=RequestContext(request))
    # checkin_start(lessonruntimeid)
    return redirect(reverse('checkin:lesson_data', args=[lesson.id]))


def addask(request):
    student = request.GET.getlist('students[]', default=False)
    starttime = datetime.datetime.strptime(request.GET.get('starttime', default=False), "%Y-%m-%d %I:%M %p")
    endtime = datetime.datetime.strptime(request.GET.get('endtime', default=False), "%Y-%m-%d %I:%M %p")
    reason = request.GET.get('reason', default='')
    typedata = {u'公假': CHECKIN_STATUS_PUBLIC_ASK, u'私假': CHECKIN_STATUS_PRIVATE_ASK}
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
        return render_to_response('error.html',
                                  {'message': '没有权限'},
                                  context_instance=RequestContext(request))
    if request.GET.get('deleteall', 0):
        clear_checkin(lesson)
        return redirect(reverse('checkin:lesson_data', args=[lesson.id]))
    if request.GET.get('deletethis', 0):
        clear_last_checkin(lesson)
        return redirect(reverse('checkin:lesson_data', args=[lesson.id]))
