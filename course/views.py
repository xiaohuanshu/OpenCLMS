# -*- coding: utf-8 -*-
import json

from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from course.auth import has_course_permission, is_course_student
from models import Course, Lesson, Studentcourse, Courseresource, Coursehomework, Homeworkfile, Homeworkcommit
from constant import *
from user.auth import permission_required
from school.function import getCurrentSchoolYearTerm
import time


def information(request, courseid):
    coursedata = Course.objects.get(id=courseid)
    lessondata = Lesson.objects.filter(course=coursedata).order_by('week', 'day', 'time').all()
    return render(request, 'information.html',
                  {'coursedata': coursedata, 'lessondata': lessondata,
                   'courseperms': has_course_permission(request.user, coursedata)})


@permission_required(permission='course_viewlist')
def list(request):
    return render(request, 'list.html', {'term': getCurrentSchoolYearTerm()})


@permission_required(permission='course_viewlist')
def data(request):
    order = request.GET['order']
    limit = int(request.GET['limit'])
    offset = int(request.GET['offset'])
    # lessondata = Lesson.objects.all()[offset: (offset + limit)]
    sort = request.GET.get('sort', '')
    if not sort == '':
        if order == "asc":
            coursedata = Course.objects.order_by(sort)
        else:
            coursedata = Course.objects.order_by("-%s" % sort)
    else:
        coursedata = Course.objects
    schoolterm = request.GET.get('schoolterm', default=None)
    if schoolterm:
        coursedata = coursedata.filter(schoolterm=schoolterm)
    major = request.GET.get('major', '')
    if not major == '':
        if major[:1] == '*':
            coursedata = coursedata.filter(department__name=major[1:])
        else:
            coursedata = coursedata.filter(major__name=major)
    search = request.GET.get('search', '')
    if not search == '':
        count = coursedata.filter(
            (Q(title__icontains=search) | Q(teacher__name__icontains=search)) | Q(serialnumber=search)
        ).count()
        coursedata = coursedata.select_related('teacher').select_related('major').select_related(
            'department').filter(
            (Q(title__icontains=search) | Q(teacher__name__icontains=search)) | Q(serialnumber=search)
        )[offset: (offset + limit)]
    else:
        count = coursedata.count()
        coursedata = coursedata.select_related('teacher').select_related('major').select_related(
            'department').all()[offset: (offset + limit)]

    rows = []
    for p in coursedata:
        ld = {'id': p.id, 'serialnumber': p.serialnumber, 'title': p.title, 'number': p.number,
              'schoolterm': p.schoolterm, 'time': p.time, 'location': p.location, 'teacher': p.teacher.name,
              'major': (p.major and [p.major.name] or [None])[0], 'department': p.department.name}
        rows.append(ld)
    data = {'total': count, 'rows': rows}
    return HttpResponse(json.dumps(data), content_type="application/json")


def studentcourse(request, courseid):
    coursedata = Course.objects.get(id=courseid)
    students = Studentcourse.objects.filter(course=coursedata).select_related('student', 'student__classid',
                                                                              'student__classid__major',
                                                                              'student__classid__department').all()
    return render(request, 'studentcourse.html',
                  {'coursedata': coursedata, 'students': students,
                   'courseperms': has_course_permission(request.user, coursedata)})


def resource(request, courseid):
    coursedata = Course.objects.get(id=courseid)
    resources = Courseresource.objects.filter(course=coursedata).all()
    resources.order_by('uploadtime')
    return render(request, 'resource.html',
                  {'coursedata': coursedata, 'courseperms': has_course_permission(request.user, coursedata),
                   'resources': resources})


def resourceupload(request):
    coursedata = Course.objects.get(id=request.POST.get('courseid'))
    if not has_course_permission(request.user, coursedata):
        return HttpResponse(json.dumps({'error': u'没有权限上传到此课程'}), content_type="application/json")
    res = Courseresource(course=coursedata, uploadtime=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
    res.file = request.FILES['file_data']
    res.title = res.file.name
    res.save()
    deleteurl = reverse('course:resourcedelete', args=[])
    initialpreviewdata = res.initialPreview()
    data = {
        'initialPreview': [initialpreviewdata['data']],
        'initialPreviewConfig': [
            {
                'caption': res.title,
                'url': deleteurl,
                'key': res.id
            },
        ]
    }
    if initialpreviewdata.has_key('type'):
        data['initialPreviewConfig'][0]['type'] = initialpreviewdata['type']
    if initialpreviewdata.has_key('filetype'):
        data['initialPreviewConfig'][0]['filetype'] = initialpreviewdata['filetype']
    return HttpResponse(json.dumps(data), content_type="application/json")


def resourcedelete(request):
    key = request.POST.get('key')
    res = Courseresource.objects.get(id=key)
    if not has_course_permission(request.user, res.course):
        return HttpResponse(json.dumps({'error': u'没有权限删除此课程文件'}), content_type="application/json")
    res.file.delete()
    res.delete()
    return HttpResponse(json.dumps([]), content_type="application/json")


def homework(request, courseid):
    coursedata = Course.objects.get(id=courseid)
    courseperms = has_course_permission(request.user, coursedata)
    coursestudent = is_course_student(coursedata, request.user)
    if request.GET.get('newhomework'):
        if request.META['REQUEST_METHOD'] == 'POST':
            if not courseperms:
                return HttpResponse(json.dumps({'error': 101, 'message': '没有权限'}), content_type="application/json")
            title = request.POST.get('title')
            deadline = request.POST.get('deadline')
            type = request.POST.get('type')
            if type == 'onlinesubmit':
                type = COURSE_HOMEWORK_TYPE_ONLINESUBMIT
            elif type == 'nosubmit':
                type = COURSE_HOMEWORK_TYPE_NOSUBMIT
            instruction = request.POST.get('instruction')
            attachments = request.FILES.getlist('attachment')
            weight = request.POST.get('weight')
            homework = Coursehomework(title=title, deadline=deadline, type=type, instruction=instruction,
                                      weight=weight, course=coursedata)
            homework.save()
            for file in attachments:
                homework.attachment.add(Homeworkfile.objects.create(file=file, title=file.name))
            return redirect(reverse('course:homework', args=[courseid]) + '?homeworkid=%d' % homework.id)
        else:
            return render(request, 'newhomework.html',
                          {'coursedata': coursedata, 'courseperms': courseperms})
    elif request.GET.get('homeworkid'):
        homeworkdata = Coursehomework.objects.get(id=request.GET.get('homeworkid'))
        data = {'coursedata': coursedata, 'courseperms': courseperms,
                'homework': homeworkdata, 'coursestudent': coursestudent}
        if request.META['REQUEST_METHOD'] == 'POST' and COURSE_HOMEWORK_TYPE_ONLINESUBMIT == homeworkdata.type:
            if not coursestudent:
                return HttpResponse(json.dumps({'error': 101, 'message': '上课名单里没有你'}), content_type="application/json")
            text = request.POST.get('text')
            attachments = request.FILES.getlist('attachment')
            commitdata, created = Homeworkcommit.objects.get_or_create(student=coursestudent,
                                                                       coursehomework=homeworkdata)
            if commitdata.score:
                pass  # 已经判完分数
            commitdata.text = text
            commitdata.submittime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            if not created:
                for ca in commitdata.attachment.all():
                    ca.file.delete()
                    ca.delete()
            for file in attachments:
                commitdata.attachment.add(Homeworkfile.objects.create(file=file, title=file.name))
            commitdata.save()
            data['commitdata'] = commitdata
        else:
            if coursestudent:
                try:
                    commitdata = Homeworkcommit.objects.get(student=coursestudent, coursehomework=homeworkdata)
                    data['commitdata'] = commitdata
                except:
                    pass
            if courseperms:
                allcommit = Homeworkcommit.objects.filter(coursehomework=homeworkdata).all()
                data['allcommit'] = allcommit
        return render(request, 'homeworkinformation.html', data)
    elif request.GET.get('delhomeworkid'):
        if not courseperms:
            return HttpResponse(json.dumps({'error': 101, 'message': '没有权限'}), content_type="application/json")
        homeworkdata = Coursehomework.objects.get(id=request.GET.get('delhomeworkid'))
        for ca in homeworkdata.attachment.all():
            ca.file.delete()
            ca.delete()
        for hc in Homeworkcommit.objects.filter(coursehomework=homeworkdata).all():
            for ca in hc.attachment.all():
                ca.file.delete()
                ca.delete()
            hc.delete()
        homeworkdata.delete()
        return redirect(reverse('course:homework', args=[courseid]))
    elif request.GET.get('edithomeworkid'):
        homeworkdata = Coursehomework.objects.get(id=request.GET.get('edithomeworkid'))
        if request.META['REQUEST_METHOD'] == 'POST':
            if not courseperms:
                return HttpResponse(json.dumps({'error': 101, 'message': '没有权限'}), content_type="application/json")
            homeworkdata.title = request.POST.get('title')
            homeworkdata.deadline = request.POST.get('deadline')
            type = request.POST.get('type')
            if type == 'onlinesubmit':
                type = COURSE_HOMEWORK_TYPE_ONLINESUBMIT
            elif type == 'nosubmit':
                type = COURSE_HOMEWORK_TYPE_NOSUBMIT
            homeworkdata.type = type
            homeworkdata.instruction = request.POST.get('instruction')
            attachments = request.FILES.getlist('attachment')
            homeworkdata.weight = request.POST.get('weight')
            homeworkdata.save()
            for ca in homeworkdata.attachment.all():
                ca.file.delete()
                ca.delete()
            for file in attachments:
                homeworkdata.attachment.add(Homeworkfile.objects.create(file=file, title=file.name))
            return redirect(reverse('course:homework', args=[courseid]) + '?homeworkid=%d' % homeworkdata.id)
        else:
            return render(request, 'newhomework.html',
                          {'coursedata': coursedata, 'courseperms': courseperms, 'homework': homeworkdata})
    else:
        homeworks = Coursehomework.objects.filter(course=coursedata).only('title', 'deadline').all()
        return render(request, 'homeworklist.html',
                      {'coursedata': coursedata, 'courseperms': courseperms,
                       'homeworks': homeworks, 'coursestudent': coursestudent})
