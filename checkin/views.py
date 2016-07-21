# coding:utf-8
from course.models import Lesson, Studentcourse, Course
from models import Checkin, Checkinrecord
from school.models import Student
from constant import *
from django.shortcuts import render_to_response, RequestContext
from django.core.urlresolvers import reverse
from course.constant import *
from checkin.function import clear_checkin, clear_last_checkin
import json
from django.shortcuts import redirect, HttpResponseRedirect
from course.auth import has_course_permission
from function import generateqrstr


def checkin(request, lessonid):
    lesson = Lesson.objects.get(id=lessonid)
    if not has_course_permission(request.user, lesson.course):
        return render_to_response('error.html',
                                  {'message': '没有权限'},
                                  context_instance=RequestContext(request))
    if not (
                        lesson.status == LESSON_STATUS_CHECKIN or lesson.status == LESSON_STATUS_CHECKIN_AGAIN or lesson.status == LESSON_STATUS_CHECKIN_ADD):
        return render_to_response('error.html',
                                  {'message': '签到还未开始',
                                   'submessage': lesson.course.title,
                                   'jumpurl': str(
                                       reverse('course:information', args=[lesson.course.id]))},
                                  context_instance=RequestContext(request))
    if request.GET.get('deleteall', 0):
        clear_checkin(lessonid)
        return redirect(reverse('course:information', args=[lesson.course.id]))
    if request.GET.get('deletethis', 0):
        clear_last_checkin(lessonid)
        return redirect(reverse('course:information', args=[lesson.course.id]))
    studentlist = Studentcourse.objects.filter(course=lesson.course).all()
    data = {'lessondata': lesson, 'studentlist': studentlist}
    if lesson.status == LESSON_STATUS_CHECKIN_ADD:
        data['checkintype'] = u'补签'
    elif lesson.status == LESSON_STATUS_CHECKIN_AGAIN:
        data['checkintype'] = u'再签'
    data['firstqrstr'] = generateqrstr(lessonid)
    return render_to_response('checkin.html', data,
                              context_instance=RequestContext(request))


def lesson_data(request, lessonid):
    lesson = Lesson.objects.get(id=lessonid)
    if not has_course_permission(request.user, lesson.course):
        return render_to_response('error.html',
                                  {'message': '没有权限'},
                                  context_instance=RequestContext(request))
    t = {'lessondata': lesson}
    if lesson.status == LESSON_STATUS_CHECKIN or lesson.status == LESSON_STATUS_CHECKIN_AGAIN or lesson.status == LESSON_STATUS_CHECKIN_ADD:
        return redirect(reverse('checkin:qrcheckin', args=[lessonid]))
    checkinrecord = Checkinrecord.objects.filter(lesson=lesson)
    checkincount = checkinrecord.count()

    shouldnumber = lesson.shouldnumber()
    actuallynumber = lesson.actuallynumber()
    asknumber = lesson.asknumber()
    notreachnumber = lesson.notreachnumber()
    t['shouldnumber'] = shouldnumber
    t['actuallynumber'] = actuallynumber
    t['asknumber'] = asknumber
    t['notreachnumber'] = notreachnumber

    checkin_success = Checkin.objects.filter(lesson=lesson).filter(status=CHECKIN_STATUS_SUCCESS).count()
    checkin_early = Checkin.objects.filter(lesson=lesson).filter(status=CHECKIN_STATUS_EARLY).count()
    checkin_late = Checkin.objects.filter(lesson=lesson).filter(status=CHECKIN_STATUS_LATE).count()
    checkin_lateearly = Checkin.objects.filter(lesson=lesson).filter(status=CHECKIN_STATUS_LATEEARLY).count()
    checkin_normal = Checkin.objects.filter(lesson=lesson).filter(status=CHECKIN_STATUS_NORMAL).count()
    t['checkin_success'] = checkin_success
    t['checkin_early'] = checkin_early
    t['checkin_late'] = checkin_late
    t['checkin_lateearly'] = checkin_lateearly
    t['checkin_normal'] = checkin_normal

    t['checkincount'] = checkincount
    if not checkincount == 0:
        checkinrecord = checkinrecord.order_by('time').all()
        t['checkinrecord'] = checkinrecord

    checkindata = Checkin.objects.filter(lesson=lesson).exclude(status=CHECKIN_STATUS_ASK).select_related(
        'student').select_related('student__classid').select_related('student__classid__department').select_related(
        'student__classid__major').all()
    t['checkindata'] = checkindata

    askdata = Checkin.objects.filter(lesson=lesson, status=CHECKIN_STATUS_ASK).select_related('student').select_related(
        'student__classid').select_related('student__classid__department').select_related(
        'student__classid__major').all()
    t['askdata'] = askdata

    return render_to_response('lesson_data.html', t, context_instance=RequestContext(request))


def course_data(request, courseid):
    modify = False
    if request.GET.get('mode', default=None) == 'modify':
        constantdata = {CHECKIN_STATUS_NORMAL: u"未到", CHECKIN_STATUS_SUCCESS: u"正常", CHECKIN_STATUS_EARLY: u"早退",
                        CHECKIN_STATUS_LATEEARLY: u"迟到早退",
                        CHECKIN_STATUS_LATE: u"迟到", CHECKIN_STATUS_CANCEL: u"取消"}
        modify = True
    course = Course.objects.get(id=courseid)
    if not has_course_permission(request.user, course):
        return render_to_response('error.html',
                                  {'message': '没有权限'},
                                  context_instance=RequestContext(request))
    alllesson = Lesson.objects.filter(course=course).exclude(status=LESSON_STATUS_AWAIT).order_by(
        'week',
        'day',
        'time').all()
    columns = [
        [{'field': 'name', 'title': u'学生', 'rowspan': 2, 'align': 'center', 'valign': 'middle', 'searchable': True},
         {'field': 'studentid', 'title': u'学号', 'rowspan': 2, 'align': 'center', 'valign': 'middle', 'searchable': True,
          'sortable': True},
         {'field': 'ratio', 'title': u'出勤率', 'rowspan': 2, 'align': 'center', 'valign': 'middle'},
         {'title': u'签到数据', 'colspan': alllesson.count(), 'align': 'center'}], []]
    # for i in range(0, count - 1):
    #    columns.append({'field': 'lesson%d' % i, 'title': i + 1, 'formatter': 'identifierFormatter'})
    for i, l in enumerate(alllesson):
        if modify and l.status != LESSON_STATUS_AWAIT and l.status != LESSON_STATUS_CANCLE:
            columns[1].append(
                    {'field': 'lesson%d' % l.id, 'title': i + 1, 'align': 'center',
                     'editable': {'url': reverse('checkin:changecheckinstatus', args=[l.id])}})
        else:
            columns[1].append(
                {'field': 'lesson%d' % l.id, 'title': i + 1, 'align': 'center', 'formatter': 'identifierFormatter',
                 'cellStyle': 'cellStyle'})
    studentdata = Studentcourse.objects.filter(course=course).order_by('student').all()
    lessoncheckindata = []
    '''for s in studentdata:
        studentcheckindata[s.student.studentid] = {'studentid': s.student.studentid, 'name': s.student.name}
    for l in alllesson:
        checkin = Checkin.objects.filter(lesson=l).all()
        for c in checkin:
    '''
    count = Checkin.objects.filter(lesson__course=course).distinct('lesson').count()
    for s in studentdata:
        studentcheckindata = {'studentid': s.student.studentid, 'name': s.student.name}
        checkindata = Checkin.objects.filter(student=s.student, lesson__course=course).order_by(
            'lesson__week',
            'lesson__day',
            'lesson__time').select_related(
            'lesson').all()
        ratio = 0.0
        for c in checkindata:
            studentcheckindata['lesson%d' % (c.lesson.id)] = c.status
            if c.status != 0:
                ratio += 1
        if count == 0:
            ratio = 1
        else:
            ratio = ratio / count
        studentcheckindata['ratio'] = '%.1f%%' % (ratio * 100)
        lessoncheckindata.append(studentcheckindata)
    data = {'header': json.dumps(columns), 'newrows': json.dumps(lessoncheckindata)}
    return render_to_response('course_data.html', {'coursedata': course, 'data': data},
                              context_instance=RequestContext(request))


def student_data(request, studentid):
    student = Student.objects.get(studentid=studentid)
    studentcourse = Studentcourse.objects.filter(student=student).all()
    coursecount = studentcourse.count()
    course = {}
    maxlength = 0
    for sc in studentcourse:
        course[sc.course.id] = {'name': sc.course.title, 'courseid': sc.course.id, 'checkindata': {}}
        if sc.course.lesson_set.count() > maxlength:
            maxlength = sc.course.lesson_set.count()
        for (offset, l) in enumerate(sc.course.lesson_set.order_by('week', 'day', 'time').all()):
            course[sc.course.id]['checkindata'].update({l.id: {'status': None, 'offset': offset}})
    checkindata = Checkin.objects.filter(student=student).select_related('lesson').all()
    for c in checkindata:
        course[c.lesson.course.id]['checkindata'][c.lesson.id]['status'] = c.status

    rows = []
    for (k, v) in course.items():
        ld = {'courseid': v['courseid'], 'name': v['name']}
        # ld['data'] = []
        ratio = 0.0
        len = 0
        for (key, item) in v['checkindata'].items():
            if item['status'] != None:
                len += 1
                if item['status'] != 0:
                    ratio = ratio + 1
            ld.update({'lesson%d' % item['offset']: item['status']})
        if len == 0:
            ratio = 1
        else:
            ratio = ratio / len
        ld['ratio'] = '%.1f%%' % (ratio * 100)
        rows.append(ld)
    '''
    newrows = []
    for new in rows:
        a = {'name': new['name'], 'ratio': new['ratio']}
        for (offset, item) in enumerate(new['data']):
            a['lesson%d' % (offset)] = item
        newrows.append(a)
    print newrows
    '''

    columns = [
        [{'field': 'name', 'title': u'课程名称', 'rowspan': 2, 'align': 'center', 'valign': 'middle', 'searchable': True},
         {'field': 'ratio', 'title': u'出勤率', 'rowspan': 2, 'align': 'center', 'valign': 'middle'},
         {'title': u'签到数据', 'colspan': maxlength, 'align': 'center'}], []]

    for i in range(0, maxlength):
        columns[1].append(
            {'field': 'lesson%d' % i, 'title': i + 1, 'cellStyle': 'cellStyle', 'formatter': 'identifierFormatter',
             'align': 'center'})
    data = {'total': coursecount, 'rows': json.dumps(rows), 'header': json.dumps(columns)}
    return render_to_response('student_data.html', {'student': student, 'data': data},
                              context_instance=RequestContext(request))


def personaldata(request):
    if request.user.isteacher():
        pass
    else:
        student = Student.objects.get(user=request.user)
        # return HttpResponseRedirect(reverse('checkin:student_data', args=[student.studentid]))
        return student_data(request, student.studentid)
