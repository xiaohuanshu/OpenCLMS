from django.db.models import ObjectDoesNotExist

from school.models import Teacher


def has_course_permission(user, course):
    if user.has_perm('course_control'):
        return True
    try:
        teacher = Teacher.objects.get(user=user)
    except ObjectDoesNotExist:
        return False
    if course.teacher == teacher:
        return True
    else:
        return False
