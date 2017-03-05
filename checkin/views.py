# coding:utf-8
from __future__ import division
from course.models import Lesson, Studentcourse, Course
from models import Checkin, Checkinrecord, Ask, Scoreregulation
from school.models import Student, Teacher
from school.function import getCurrentSchoolYearTerm
from constant import *
from django.shortcuts import render
from django.core.urlresolvers import reverse
from course.constant import *
from django.db.models import ObjectDoesNotExist
import json
from django.shortcuts import redirect, HttpResponse, HttpResponseRedirect
from course.auth import has_course_permission
from function import generateqrstr
import datetime
from django.db.models import Count, Case, When, Q
from django.core.cache import cache


def checkin(request, lessonid):
    lesson = Lesson.objects.get(id=lessonid)
    if not has_course_permission(request.user, lesson.course):
        return render(request, 'error.html', {'message': '没有权限'})
    if not (
                        lesson.status == LESSON_STATUS_CHECKIN or lesson.status == LESSON_STATUS_CHECKIN_AGAIN or lesson.status == LESSON_STATUS_CHECKIN_ADD):
        return render(request, 'error.html',
                      {'message': '签到还未开始',
                       'submessage': lesson.course.title,
                       'jumpurl': str(
                           reverse('course:information', args=[lesson.course.id]))})

    studentlist = Studentcourse.objects.filter(course=lesson.course).select_related('student').order_by(
        'student__studentid').all()
    data = {'lessondata': lesson, 'studentlist': studentlist}
    if lesson.status == LESSON_STATUS_CHECKIN_ADD:
        data['checkintype'] = u'补签'
    elif lesson.status == LESSON_STATUS_CHECKIN_AGAIN:
        data['checkintype'] = u'再签'
    data['firstqrstr'] = generateqrstr(lessonid)
    return render(request, 'checkin.html', data)


def lesson_data(request, lessonid):
    lesson = Lesson.objects.get(id=lessonid)
    if not (has_course_permission(request.user, lesson.course) or request.user.has_perm('checkin_view')):
        return render(request, 'error.html', {'message': '没有权限'})
    t = {'lessondata': lesson, 'coursedata': lesson.course,
         'courseperms': has_course_permission(request.user, lesson.course)}
    if lesson.ischeckinnow():
        return redirect(reverse('checkin:qrcheckin', args=[lessonid]))
    if not (lesson.isnow() or lesson.isend()):
        return render(request, 'error.html',
                      {'message': '课程还未开启',
                       'jumpurl': reverse('course:information', args=[lesson.course_id])})
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

    checkindata = Checkin.objects.filter(lesson=lesson).exclude(status__gt=10).select_related(
        'student').select_related('student__classid').select_related('student__classid__department').select_related(
        'student__classid__major').order_by('student__studentid').all()
    t['checkindata'] = checkindata

    askdata = Checkin.objects.filter(lesson=lesson, status__gt=10).select_related('student').select_related(
        'student__classid').select_related('student__classid__department').select_related(
        'student__classid__major').all()
    t['askdata'] = askdata
    t['canclearlastdata'] = cache.get('lesson_%d_clear_flag' % lesson.id, default=False)
    return render(request, 'lesson_data.html', t)


def course_data(request, courseid):
    modify = False
    if request.GET.get('mode', default=None) == 'modify':
        constantdata = {CHECKIN_STATUS_NORMAL: u"未到", CHECKIN_STATUS_SUCCESS: u"正常", CHECKIN_STATUS_EARLY: u"早退",
                        CHECKIN_STATUS_LATEEARLY: u"迟到早退",
                        CHECKIN_STATUS_LATE: u"迟到", CHECKIN_STATUS_CANCEL: u"取消"}
        modify = True
    course = Course.objects.get(id=courseid)
    if not (has_course_permission(request.user, course) or request.user.has_perm('checkin_view')):
        return render(request, 'error.html', {'message': '没有权限'})
    alllesson = Lesson.objects.filter(course=course).exclude(status=LESSON_STATUS_AWAIT).order_by(
        'week',
        'day',
        'time').all()
    columns = [
        [{'field': 'name', 'title': u'学生', 'rowspan': 2, 'align': 'center', 'valign': 'middle', 'searchable': True},
         {'field': 'studentid', 'title': u'学号', 'rowspan': 2, 'align': 'center', 'valign': 'middle', 'searchable': True,
          'sortable': True},
         {'field': 'ratio', 'title': u'出勤率', 'rowspan': 2, 'align': 'center', 'valign': 'middle'},
         {'field': 'score', 'title': u'考勤分数', 'rowspan': 2, 'align': 'center', 'valign': 'middle'},
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
    studentdata = Studentcourse.objects.filter(course=course).select_related('student').order_by('student').all()
    lessoncheckindata = []
    '''for s in studentdata:
        studentcheckindata[s.student.studentid] = {'studentid': s.student.studentid, 'name': s.student.name}
    for l in alllesson:
        checkin = Checkin.objects.filter(lesson=l).all()
        for c in checkin:
    '''
    count = Checkin.objects.filter(lesson__course=course).distinct('lesson').count()
    try:
        scoreregulation = Scoreregulation.objects.get(course=course)
    except ObjectDoesNotExist:
        scoreregulation = Scoreregulation(course=course)
    for s in studentdata:
        studentcheckindata = {'studentid': s.student.studentid, 'name': s.student.name}
        checkindata = Checkin.objects.filter(student=s.student, lesson__course=course).order_by(
            'lesson__week',
            'lesson__day',
            'lesson__time').select_related(
            'lesson').all()
        ratio = 0.0
        score = 0.0
        totalscore = 0
        for c in checkindata:
            studentcheckindata['lesson%d' % (c.lesson.id)] = c.status
            if c.status != CHECKIN_STATUS_NORMAL:
                ratio += 1
            score += scoreregulation.getscore(c.status)
            totalscore += 100
        if count == 0:
            ratio = 1
        else:
            ratio = ratio / count
        if totalscore == 0:
            score = 100
        else:
            score = int((score / totalscore) * 100)
        studentcheckindata['ratio'] = '%.1f%%' % (ratio * 100)
        studentcheckindata['score'] = '%d' % (score)
        lessoncheckindata.append(studentcheckindata)
    data = {'header': json.dumps(columns), 'newrows': json.dumps(lessoncheckindata)}
    return render(request, 'course_data.html', {'coursedata': course, 'data': data,
                                                'courseperms': has_course_permission(request.user, course)})


def student_data(request, studentid):
    student = Student.objects.get(studentid=studentid)
    if not (student.user == request.user or request.user.has_perm('checkin_view')):
        return render(request, 'error.html', {'message': '没有权限'})
    studentcourse = Studentcourse.objects.filter(student=student).all()
    coursecount = studentcourse.count()
    course = {}
    maxlength = 0
    for sc in studentcourse:
        course[sc.course.id] = {'course': sc.course, 'checkindata': {}}
        if sc.course.lesson_set.count() > maxlength:
            maxlength = sc.course.lesson_set.count()
        for (offset, l) in enumerate(sc.course.lesson_set.order_by('week', 'day', 'time').all()):
            course[sc.course.id]['checkindata'].update({l.id: {'status': None, 'offset': offset}})
    checkindata = Checkin.objects.filter(student=student).select_related('lesson').all()
    for c in checkindata:
        course[c.lesson.course.id]['checkindata'][c.lesson.id]['status'] = c.status

    rows = []
    for (k, v) in course.items():
        ld = {'courseid': v['course'].id, 'name': v['course'].title}
        # ld['data'] = []
        ratio = 0.0
        score = 0.0
        totalscore = 0
        try:
            scoreregulation = Scoreregulation.objects.get(course=v['course'])
        except ObjectDoesNotExist:
            scoreregulation = Scoreregulation(course=v['course'])
        len = 0
        for (key, item) in v['checkindata'].items():
            if item['status'] != None:
                len += 1
                if item['status'] != 0:
                    ratio = ratio + 1
                score += scoreregulation.getscore(item['status'])
                totalscore += 100
            ld.update({'lesson%d' % item['offset']: item['status']})
        if len == 0:
            ratio = 1
        else:
            ratio = ratio / len
        if totalscore == 0:
            score = 100
        else:
            score = int((score / totalscore) * 100)
        ld['ratio'] = '%.1f%%' % (ratio * 100)
        ld['score'] = '%d' % (score)
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
         {'field': 'score', 'title': u'考勤成绩', 'rowspan': 2, 'align': 'center', 'valign': 'middle'},
         {'title': u'签到数据', 'colspan': maxlength, 'align': 'center'}], []]

    for i in range(0, maxlength):
        columns[1].append(
            {'field': 'lesson%d' % i, 'title': i + 1, 'cellStyle': 'cellStyle', 'formatter': 'identifierFormatter',
             'align': 'center'})
    data = {'total': coursecount, 'rows': json.dumps(rows), 'header': json.dumps(columns)}
    return render(request, 'student_data.html', {'student': student, 'data': data})


def teacher_data(request, teacherid):
    teacher = Teacher.objects.get(teacherid=teacherid)
    if not (teacher.user == request.user or request.user.has_perm('checkin_view')):
        return render(request, 'error.html', {'message': '没有权限'})
    teachercourse = Course.objects.filter(teacher=teacher).all()
    coursecount = teachercourse.count()
    course = {}
    maxlength = 0
    for tc in teachercourse:
        course[tc.id] = {'name': tc.title, 'schoolterm': tc.schoolterm, 'courseid': tc.id, 'checkindata': {}}
        if tc.lesson_set.count() > maxlength:
            maxlength = tc.lesson_set.count()
        for (offset, l) in enumerate(tc.lesson_set.order_by('week', 'day', 'time').all()):
            course[tc.id]['checkindata'].update({l.id: {'status': None, 'offset': offset}})
    checkindata = Checkin.objects.filter(lesson__course__in=teachercourse).annotate(
        should=Count(Case(When(~Q(status__gt=10), then=1))), actually=Count(Case(
            When(Q(status=CHECKIN_STATUS_EARLY) | Q(status=CHECKIN_STATUS_SUCCESS) | Q(status=CHECKIN_STATUS_LATE) | Q(
                status=CHECKIN_STATUS_LATEEARLY), then=2)))).values('lesson__course',
                                                                    'lesson', 'should', 'actually')
    checkindata.query.group_by = ['lesson']

    for c in checkindata:
        if c['should'] == 0:
            course[c['lesson__course']]['checkindata'][c['lesson']]['status'] = None
        else:
            course[c['lesson__course']]['checkindata'][c['lesson']]['status'] = "%.1f" % (
                c['actually'] / c['should'] * 100)

    rows = []
    for (k, v) in course.items():
        ld = {'courseid': v['courseid'], 'name': v['name'], 'schoolterm': v['schoolterm']}
        # ld['data'] = []
        for (key, item) in v['checkindata'].items():
            ld.update({'lesson%d' % item['offset']: item['status']})
        rows.append(ld)

    columns = [
        [{'field': 'name', 'title': u'课程名称', 'rowspan': 2, 'align': 'center', 'valign': 'middle', 'searchable': True,
          'formatter': 'identifierFormatter'},
         {'field': 'schoolterm', 'title': u'学期', 'rowspan': 2, 'align': 'center', 'valign': 'middle'},
         {'title': u'课程学生到达率', 'colspan': maxlength, 'align': 'center'}], []]

    for i in range(0, maxlength):
        columns[1].append(
            {'field': 'lesson%d' % i, 'title': i + 1, 'align': 'center'})
    data = {'total': coursecount, 'rows': json.dumps(rows), 'header': json.dumps(columns)}
    return render(request, 'teacher_data.html', {'teacher': teacher, 'data': data})


def personaldata(request):
    if request.user.isteacher():
        teacher = Teacher.objects.get(user=request.user)
        return teacher_data(request, teacher.teacherid)
    else:
        student = Student.objects.get(user=request.user)
        # return HttpResponseRedirect(reverse('checkin:student_data', args=[student.studentid]))
        return student_data(request, student.studentid)


def askmanager(request):
    return render(request, 'askmanager.html')


def askdata(request):
    typedata = {CHECKIN_STATUS_PRIVATE_ASK: '私假', CHECKIN_STATUS_PUBLIC_ASK: '公假'}
    order = request.GET['order']
    limit = int(request.GET['limit'])
    offset = int(request.GET['offset'])
    sort = request.GET.get('sort', '')
    if not sort == '':
        if order == "asc":
            ask = Ask.objects.order_by(sort)
        else:
            ask = Ask.objects.order_by("-%s" % sort)
    else:
        ask = Ask.objects.order_by('-id')
    schoolterm = getCurrentSchoolYearTerm()['term']
    ask = ask.filter(schoolterm=schoolterm, operater=request.user)
    search = request.GET.get('search', '')
    if not search == '':
        if search.isdigit():
            count = ask.filter(student=search).count()
            ask = ask.filter(
                studentid=search
            )[offset: (offset + limit)]
        else:
            count = ask.filter(student__name=search).count()
            ask = ask.filter(
                student__name=search
            )[offset: (offset + limit)]
    else:
        count = ask.count()
        ask = ask.all()[offset: (offset + limit)]

    rows = []
    for p in ask:
        ld = {'id': p.id, 'student': ", ".join("%s(%s)" % (s.name, s.studentid) for s in p.student.all()),
              'starttime': datetime.datetime.strftime(p.starttime, '%Y-%m-%d %I:%M %p'),
              'endtime': datetime.datetime.strftime(p.endtime, '%Y-%m-%d %I:%M %p'),
              'reason': p.reason, 'status': p.status, 'type': typedata[p.type]}
        rows.append(ld)
    data = {'total': count, 'rows': rows}
    return HttpResponse(json.dumps(data), content_type="application/json")


def scoreregulationsetting(request, courseid):
    course = Course.objects.get(id=courseid)
    try:
        scoreregulation = Scoreregulation.objects.get(course=course)
    except ObjectDoesNotExist:
        scoreregulation = Scoreregulation(course=course)
    if request.META['REQUEST_METHOD'] == 'POST':
        scoreregulation.normal = request.POST.get('normal')
        scoreregulation.success = request.POST.get('success')
        scoreregulation.early = request.POST.get('early')
        scoreregulation.lateearly = request.POST.get('lateearly')
        scoreregulation.late = request.POST.get('late')
        scoreregulation.private_ask = request.POST.get('private_ask')
        scoreregulation.public_ask = request.POST.get('public_ask')
        scoreregulation.save()
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
    return render(request, 'scoreregulation.html', data)


def jumptolesson_data(request, courseid):
    course = Course.objects.get(id=courseid)
    try:
        lesson = Lesson.objects.filter(course=course,
                                       status__in=[LESSON_STATUS_NOW, LESSON_STATUS_CHECKIN, LESSON_STATUS_CHECKIN_ADD,
                                                   LESSON_STATUS_CHECKIN_AGAIN]).get()
        return HttpResponseRedirect(reverse('checkin:lesson_data', args=[lesson.id]))
    except ObjectDoesNotExist:
        return render(request, 'error.html',
                      {'message': '没有课程开启',
                       'submessage': '请在课程详情中开启课程',
                       'jumpurl': str(
                           reverse('course:information', args=[courseid]))})
