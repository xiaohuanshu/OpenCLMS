from rbac.auth import is_user_has_resourcejurisdiction
from school.models import Teacher
from django.db.models import ObjectDoesNotExist


def has_course_permission(user, course):
    if is_user_has_resourcejurisdiction(user, 'control_course'):
        return True
    try:
        teacher = Teacher.objects.get(user=user)
    except ObjectDoesNotExist:
        return False
    if course.teacher == teacher:
        return True
    else:
        return False
