def auth(request):
    if hasattr(request, 'user'):
        user = request.user
        return {
            'perms': PermWrapper(user),
            'piwik_identity': user.academiccode  # for Piwik identity
        }
    else:
        return {
            'perms': NonePermWrapper(),
            'piwik_identity': None
        }


class PermWrapper(object):
    def __init__(self, user):
        self.user = user

    def __getitem__(self, permission):
        if hasattr(self, '%s_cache' % permission):
            return getattr(self, '%s_cache' % permission)
        else:
            data = self.user.has_perm(permission)
            setattr(self, '%s_cache' % permission, data)
            return data


class NonePermWrapper(object):
    def __init__(self):
        pass

    def __getitem__(self, jurisdiction):
        return None
