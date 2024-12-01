from . import check_perm


class PermsChecker():
    def __init__(self, user, resource):
        self.user, self.resource = user, resource

    def __getitem__(self, perm_name):
        return check_perm(self.user, self.resource, perm_name)


class CasbinPerms():
    def __init__(self, user):
        self.user = user

    def __getitem__(self, perm_name):
        return PermsChecker(self.user, perm_name)


def casbin_perms(request):
    return { 'check_perm': CasbinPerms(request.user) }