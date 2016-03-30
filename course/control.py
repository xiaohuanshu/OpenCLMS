# coding=utf-8
from models import Lesson
from constant import *
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import redirect,render_to_response, RequestContext
import json


def startLesson(request):
    lessondata=Lesson.objects.get(id=request.GET.get('lessonid'))
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
            if request.GET.get('jumptocheckin',default=0) == '1':
                return redirect(reverse('checkin:startcheckin', args=[lessondata.id]))
            else:
                return redirect(reverse('checkin:lesson_data', args=[lessondata.id]))



def stopLesson(request):
    lessondata=Lesson.objects.get(id=request.GET.get('lessonid'))
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
