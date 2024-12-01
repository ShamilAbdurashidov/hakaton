from pathlib import Path
import os
import casbin


DIR = Path(__file__).resolve().parent


enforcer = casbin.Enforcer(
    os.path.join(DIR, "model.conf"), 
    os.path.join(DIR, "policy.csv")
    )


def user_get_role(user) -> str:
    if user.is_anonymous:
        return 'anonymous'
    if user.is_employee:
        return user.employee.role
    if user.is_superuser:
        return 'django-superuser'
    return 'django-user'


def check_perm(user, resource, perm=None, action='*') -> bool:
    if not perm:
        return enforcer.enforce(user_get_role(user), resource, action)
    return enforcer.enforce(user_get_role(user), "%s.%s" % (resource, perm), action)


def check_str_perm(user, perm) -> bool:
    parts = perm.split('.', 3)
    resource = parts[0]
    perm = None
    action = '*'
    if len(parts) > 1:
        perm = parts[1]
        if len(parts) > 2:
            action = parts[2]
    return check_perm(user, resource, perm, action)
