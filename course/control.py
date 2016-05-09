# coding=utf-8
from models import Lesson
from constant import *
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render_to_response, RequestContext
import json
from course.auth import has_course_permission


def startLesson(request):
    lessondata = Lesson.objects.get(id=request.GET.get('lessonid'))
    if not has_course_permission(request.user, lessondata.course):
        if request.is_ajax():
            return HttpResponse(json.dumps({'error': 101, 'message': '没有权限'}), content_type="application/json")
        else:
            return render_to_response('error.html',
                                      {'message': '没有权限'},
                                      context_instance=RequestContext(request))
    if request.is_ajax():
        return HttpResponse(json.dumps(lessondata.startlesson()), content_type="application/json")
    else:
        re = lessondata.startlesson()
        if re['error'] != 0:
            return render_to_response('error.html',
                                      {'message': re['message'],
                                       'submessage': lessondata.course.title,
                                       'jumpurl': str(
                                           reverse('course:information', args=[lessondata.course.id]))},
                                      context_instance=RequestContext(request))
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
            return render_to_response('error.html',
                                      {'message': '没有权限'},
                                      context_instance=RequestContext(request))
    if request.is_ajax():
        return HttpResponse(json.dumps(lessondata.stoplesson()), content_type="application/json")
    else:
        re = lessondata.stoplesson()
        if re['error'] != 0:
            return render_to_response('error.html',
                                      {'message': re['message'],
                                       'submessage': lessondata.course.title,
                                       'jumpurl': str(
                                           reverse('course:information', args=[lessondata.course.id]))},
                                      context_instance=RequestContext(request))
        else:
            return redirect(reverse('course:information', args=[lessondata.course.id]))
