from django.conf import settings


def school_settings(request):
    return {'WEEK_FIRST_DAY': settings.WEEK_FIRST_DAY}
