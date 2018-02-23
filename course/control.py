# coding=utf-8
from models import Lesson, Homeworkcommit, Course, Studentcourse
from school.models import Student
from constant import *
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render
import json
from course.auth import has_course_permission
from django.db.models import F
from django.conf import settings
from wechat.client import wechat_client


def startLesson(request):
    lessondata = Lesson.objects.get(id=request.GET.get('lessonid'))
    if not has_course_permission(request.user, lessondata.course):
        if request.is_ajax():
            return HttpResponse(json.dumps({'error': 101, 'message': '没有权限'}), content_type="application/json")
        else:
            return render(request, 'error.html',
                          {'message': '没有权限'})
    if request.is_ajax():
        return HttpResponse(json.dumps(lessondata.startlesson()), content_type="application/json")
    else:
        re = lessondata.startlesson()
        if re['error'] != 0:
            return render(request, 'error.html',
                          {'message': re['message'],
                           'submessage': lessondata.course.title,
                           'jumpurl': str(
                               reverse('course:information', args=[lessondata.course.id]))})
        else:
            if request.GET.get('jumptocheckin', default=0) == '1':
                return redirect(reverse('checkin:startcheckin', args=[lessondata.id]))
            else:
                return redirect(reverse('checkin:lesson_data', args=[lessondata.id]))


def stopLesson(request):
    lessondata = Lesson.objects.get(id=request.GET.get('lessonid'))
    if not has_course_permission(request.user, lessondata.course):
        if request.is_ajax():
            return HttpResponse(json.dumps({'error': 101, 'message': '没有权限'}), content_type="application/json")
        else:
            return render(request, 'error.html',
                          {'message': '没有权限'})
    if request.is_ajax():
        return HttpResponse(json.dumps(lessondata.stoplesson()), content_type="application/json")
    else:
        re = lessondata.stoplesson()
        if re['error'] != 0:
            return render(request, 'error.html',
                          {'message': re['message'],
                           'submessage': lessondata.course.title,
                           'jumpurl': str(
                               reverse('course:information', args=[lessondata.course.id]))})
        else:
            return redirect(reverse('course:information', args=[lessondata.course.id]))


def clearLesson(request):
    lessondata = Lesson.objects.get(id=request.GET.get('lessonid'))
    if not has_course_permission(request.user, lessondata.course):
        if request.is_ajax():
            return HttpResponse(json.dumps({'error': 101, 'message': '没有权限'}), content_type="application/json")
        else:
            return render(request, 'error.html',
                          {'message': '没有权限'})
    if request.is_ajax():
        return HttpResponse(json.dumps(lessondata.cleardata()), content_type="application/json")
    else:
        re = lessondata.cleardata()
        if re['error'] != 0:
            return render(request, 'error.html',
                          {'message': re['message'],
                           'submessage': lessondata.course.title,
                           'jumpurl': str(
                               reverse('course:information', args=[lessondata.course.id]))})
        else:
            return redirect(reverse('course:information', args=[lessondata.course.id]))


def sethomeworkscore(request):
    homeworkcommit = Homeworkcommit.objects.select_related('coursehomework').get(id=request.GET.get('homeworkcommitid'))
    score = request.GET.get('score')
    if not score.isdigit():
        return HttpResponse(json.dumps({'error': 101, 'message': '分数只能设置为数字'}), content_type="application/json")
    if not has_course_permission(request.user, homeworkcommit.coursehomework.course):
        return HttpResponse(json.dumps({'error': 101, 'message': '没有权限'}), content_type="application/json")
    homeworkcommit.score = score
    homeworkcommit.save()
    return HttpResponse(json.dumps({'error': 0, 'score': score, 'message': '评分成功'}), content_type="application/json")


def leavehomeworkcomment(request):
    homeworkcommit = Homeworkcommit.objects.select_related('coursehomework').get(
        id=request.POST.get('homeworkcommitid'))
    comment = request.POST.get('comment', '')
    if comment == '':
        return HttpResponse(json.dumps({'error': 101, 'message': '留言不能为空'}), content_type="application/json")
    if not has_course_permission(request.user, homeworkcommit.coursehomework.course):
        return HttpResponse(json.dumps({'error': 101, 'message': '没有权限'}), content_type="application/json")
    homeworkcommit.comment = comment
    homeworkcommit.save()
    # send wechat notification
    article = {
        "title": u"作业留言提醒!",
        "description": u"教师留言：" + comment,
        "url": "%s%s" % (settings.DOMAIN, reverse('course:homework', args=[
            homeworkcommit.coursehomework.course_id]) + '?homeworkid=%d' % homeworkcommit.coursehomework_id),
        "image": "%s/static/img/homework.png"
    }
    wechat_client.message.send_articles(agent_id=settings.AGENTID, user_ids=[homeworkcommit.student.user.openid],
                                        articles=[article])
    return HttpResponse(json.dumps({'error': 0, 'message': '留言成功'}), content_type="application/json")


def setperformance_score(request, courseid):
    course = Course.objects.get(id=courseid)
    student = Student.objects.get(studentid=request.GET.get('studentid'))
    score = request.GET.get('score')
    if not has_course_permission(request.user, course):
        return HttpResponse(json.dumps({'error': 101, 'message': '没有权限'}), content_type="application/json")
    sc = Studentcourse.objects.get(student=student, course=course)
    sc.performance_score += int(score)
    sc.save()
    return HttpResponse(json.dumps({'error': 0, 'message': '加分成功', 'performance_score': sc.performance_score}),
                        content_type="application/json")
