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
        return self.user.hasresourcejurisdiction(jurisdiction)


class NonePermWrapper(object):
    def __init__(self):
        pass

    def __getitem__(self, jurisdiction):
        return None
