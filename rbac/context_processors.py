def auth(request):
    if hasattr(request, 'user'):
        user = request.user
        return {
            'perms': PermWrapper(user),
        }
    else:
        return {
            'perms': NonePermWrapper(),
        }


class PermWrapper(object):
    def __init__(self, user):
        self.user = user

    def __getitem__(self, jurisdiction):
        if hasattr(self, '%s_cacle' % jurisdiction):
            return getattr(self, '%s_cacle' % jurisdiction)
        else:
            data = self.user.hasresourcejurisdiction(jurisdiction)
            setattr(self, '%s_cacle' % jurisdiction, data)
            return data


class NonePermWrapper(object):
    def __init__(self):
        pass

    def __getitem__(self, jurisdiction):
        return None
