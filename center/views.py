from django.shortcuts import render

from course.models import Studentcourse, Lesson, Course
from school.function import getCurrentSchoolYearTerm, getnowlessontime
from school.models import Student, Teacher


# Create your views here.
# @resourcejurisdiction_view_auth(jurisdiction='school')
def home(request):
    if request.user.isteacher():
        teacher = Teacher.objects.get(user=request.user)
        termcourse = Course.objects.filter(teacher=teacher, schoolterm=getCurrentSchoolYearTerm()['term'])
    else:
        student = Student.objects.get(user=request.user)
        # alreadycount = Checkin.objects.filter(studentid=student)
        # alreadycount.query.group_by = ['lessonruntimeid__lessonid__id']
        termcourse = Studentcourse.objects.filter(student=student, course__schoolterm=getCurrentSchoolYearTerm()[
            'term']).values_list('course', flat=True)
        termcourse = Course.objects.filter(id__in=termcourse)

    nowlessontime = getnowlessontime()
    lesson = Lesson.objects.filter(course__in=termcourse, week=nowlessontime['week'])

    return render(request, 'home.html',
                  {'term': getCurrentSchoolYearTerm(), 'alreadycount': 0,
                   'termcourse': termcourse.all(),
                   'weeklesson': lesson.select_related('course').all(),
                   })


def seat(request):
    return render(request, 'seat.html')
