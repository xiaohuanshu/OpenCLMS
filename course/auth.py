from django.db.models import ObjectDoesNotExist

from school.models import Teacher, Student
from course.models import Studentcourse


def has_course_permission(user, course):
    if user.has_perm('course_control'):
        return True
    try:
        teacher = Teacher.objects.get(user=user)
    except ObjectDoesNotExist:
        return False
    if teacher in course.teachers.all():
        return True
    else:
        return False


def is_course_student(course, user):
    try:
        student = Student.objects.get(user=user)
    except ObjectDoesNotExist:
        return False
    if Studentcourse.objects.filter(course=course, student=student).exists():
        return student
    else:
        return False
