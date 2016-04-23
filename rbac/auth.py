# -*- coding: utf-8 -*-
from functools import wraps
from django.shortcuts import render_to_response, RequestContext
from user.models import User
from rbac.models import Resourcejurisdiction, Roletoresourcejurisdiction


def resourcejurisdiction_view_auth(func=None, jurisdiction=None):
    def decorator(func):
        @wraps(func)
        def returned_wrapper(request, *args, **kwargs):
            userid = request.session.get('userid')
            user = User.objects.get(id=userid)
            if is_user_has_resourcejurisdiction(user, jurisdiction):
                return func(request, *args, **kwargs)
            else:
                if request.is_ajax():
                    return {'error': 101, 'message': '没有权限'}
                else:
                    return render_to_response('error.html',
                                          {'message': '没有权限'},
                                          context_instance=RequestContext(request))

        return returned_wrapper

    if not func:
        def foo(func):
            return decorator(func)

        return foo

    else:
        return decorator(func)


def is_user_has_resourcejurisdiction(user, jurisdiction):
    role = user.role.values_list('id', flat=True)
    jurisdictionid = Resourcejurisdiction.objects.get(name=jurisdiction)
    return Roletoresourcejurisdiction.objects.filter(role__in=role, resourcejurisdiction=jurisdictionid).exists()
