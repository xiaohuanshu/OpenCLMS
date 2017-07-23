from models import Studentcourse, Lesson
from school.function import getnowlessontime


def todaylesson(request):
    if hasattr(request, 'user'):
        nowlessontime = getnowlessontime()
        if request.user.isteacher:
            data = Lesson.objects.filter(course__in=request.user.teacher_set.get().course_set.all(), term=nowlessontime['term'],
                                         day=nowlessontime['day'], week=nowlessontime['week']).select_related(
                'course').all()
        else:
            studentcourse = Studentcourse.objects.filter(student__user=request.user).values_list('course', flat=True)
            lesson = Lesson.objects.filter(course__in=studentcourse, term=nowlessontime['term'],
                                           day=nowlessontime['day'], week=nowlessontime['week'])
            data = lesson.select_related('course').all()
        return {'todaylesson': data}
    else:
        return {}
