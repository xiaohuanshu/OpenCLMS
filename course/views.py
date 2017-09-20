# -*- coding: utf-8 -*-
import json

from django.db.models import Q
from django.http import HttpResponse
from django.utils.http import urlunquote
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from course.auth import has_course_permission, is_course_student
from models import Course, Lesson, Studentcourse, Courseresource, Coursehomework, Homeworkfile, Homeworkcommit
from school.models import Student, Teacher
from checkin.models import Scoreregulation
from django.db.models import ObjectDoesNotExist
from constant import *
from user_system.auth import permission_required
from school.function import getCurrentSchoolYearTerm
import time
from message import sendmessagetocoursestudent


def information(request, courseid):
    coursedata = Course.objects.get(id=courseid)
    lessondata = Lesson.objects.filter(course=coursedata) \
        .exclude(status=LESSON_STATUS_TRANSFERRED) \
        .order_by('week', 'day', 'time').all()
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
            (Q(title__icontains=search) | Q(teachers__name__icontains=search)) | Q(serialnumber=search)
        ).count()
        coursedata = coursedata.prefetch_related('teachers').select_related('major').select_related(
            'department').filter(
            (Q(title__icontains=search) | Q(teachers__name__icontains=search)) | Q(serialnumber=search)
        )[offset: (offset + limit)]
    else:
        count = coursedata.count()
        coursedata = coursedata.select_related('major').select_related(
            'department').all()[offset: (offset + limit)]

    rows = []
    for p in coursedata:
        ld = {'id': p.id, 'serialnumber': p.serialnumber, 'title': p.title, 'number': p.number,
              'schoolterm': p.schoolterm, 'time': p.time, 'location': p.location,
              'teacher': ",".join(p.teachers.values_list('name', flat=True)),
              'major': (p.major and [p.major.name] or [None])[0],
              'department': (p.department and [p.department.name] or [None])[0]}
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


def sendmessage(request, courseid):
    coursedata = Course.objects.get(id=courseid)
    data = {'coursedata': coursedata, 'courseperms': has_course_permission(request.user, coursedata)}
    if request.META['REQUEST_METHOD'] == 'POST':
        message = request.POST.get('message')
        errorsendstudentnames = sendmessagetocoursestudent(coursedata, message)
        data['send'] = True
        data['errorsendstudentnames'] = errorsendstudentnames
    return render(request, 'sendmessage.html', data)


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
    if 'type' in initialpreviewdata:
        data['initialPreviewConfig'][0]['type'] = initialpreviewdata['type']
    if 'filetype' in initialpreviewdata:
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
            homework = Coursehomework.objects.create(title=title, deadline=deadline, type=type, weight=weight,
                                                     course=coursedata)
            homework.instruction = instruction
            homework.deal_base64img()
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
            commitdata.deal_base64img()
            commitdata.submittime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            if not created:
                for ca in commitdata.attachment.exclude(title=None).all():
                    ca.file.delete()
                    ca.delete()
            for file in attachments:
                commitdata.attachment.add(Homeworkfile.objects.create(file=file, title=file.name))
            commitdata.save()
            return redirect(reverse('course:homework', args=[courseid]) + '?homeworkid=%d' % homeworkdata.id)
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
            homeworkdata.deal_base64img()
            homeworkdata.save()
            for ca in homeworkdata.attachment.exclude(title=None).all():
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


def codeview(request):
    url = request.GET.get('url')
    url = urlunquote(url)
    return render(request, 'codeview.html', {'url': url})


def imgview(request):
    url = request.GET.get('url')
    url = urlunquote(url)
    return render(request, 'imgview.html', {'imgurl': url})


def settings(request, courseid):
    course = Course.objects.get(id=courseid)
    try:
        scoreregulation = Scoreregulation.objects.get(course=course)
    except ObjectDoesNotExist:
        scoreregulation = Scoreregulation(course=course)
    if request.META['REQUEST_METHOD'] == 'POST':
        type = request.GET.get('type')
        if type == 'checkinscore':
            scoreregulation.normal = request.POST.get('normal')
            scoreregulation.success = request.POST.get('success')
            scoreregulation.early = request.POST.get('early')
            scoreregulation.lateearly = request.POST.get('lateearly')
            scoreregulation.late = request.POST.get('late')
            scoreregulation.private_ask = request.POST.get('private_ask')
            scoreregulation.public_ask = request.POST.get('public_ask')
            scoreregulation.save()
        elif type == 'people':
            students = request.POST.getlist('addstudents', default=None)
            teachers = request.POST.getlist('addteachers', default=None)
            disable_sync = request.POST.get('disable_sync', default=None)
            add_student_from_course = request.POST.get('add_student_from_course', default=None)
            if disable_sync and disable_sync == 'on':
                disable_sync = True
            else:
                disable_sync = False
            if course.disable_sync != disable_sync:
                course.disable_sync = disable_sync
                course.save()
            if add_student_from_course and add_student_from_course != '':
                try:
                    if add_student_from_course.isdigit():
                        from_course = Course.objects.get(id=int(add_student_from_course))
                    else:
                        from_course = Course.objects.get(serialnumber=add_student_from_course)
                except ObjectDoesNotExist:
                    return render(request, 'error.html',
                                  {'message': '没有找到课程，请检查课程编号或id'})
                new_students = Studentcourse.objects.filter(course=from_course).values_list('student', flat=True)
                new_students_create = []
                for ns in new_students:
                    if not Studentcourse.objects.filter(course=course, student_id=ns).exists():
                        new_students_create.append(Studentcourse(course=course, student_id=ns))
                Studentcourse.objects.bulk_create(new_students_create)
            if students:
                for s in students:
                    if not Studentcourse.objects.filter(course=course, student_id=s).exists():
                        Studentcourse.objects.create(course=course, student_id=s)
            if teachers:
                for t in teachers:
                    course.teachers.add(Teacher.objects.get(teacherid=t))

    data = {'normal': scoreregulation.normal,
            'success': scoreregulation.success,
            'early': scoreregulation.early,
            'lateearly': scoreregulation.lateearly,
            'late': scoreregulation.late,
            'private_ask': scoreregulation.private_ask,
            'public_ask': scoreregulation.public_ask,
            'coursedata': course,
            'courseperms': has_course_permission(request.user, course)
            }
    return render(request, 'settings.html', data)
