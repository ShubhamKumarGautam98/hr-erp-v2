"""
rbac.py
=======
Role-Based Access Control decorators.

Usage:
    from app.utils.rbac import roles_required

    @roles_required('admin', 'hr_manager')
    def my_route():
        ...
"""
from functools import wraps
from flask import abort, render_template
from flask_login import current_user

# ── Role hierarchy ────────────────────────────────────────────────────────────
HR_ROLES   = ('admin', 'hr_manager')
BD_ROLES   = ('admin', 'bd_manager', 'bd_executive')
ADMIN_ONLY = ('admin',)
ALL_STAFF  = ('admin', 'hr_manager', 'bd_manager', 'bd_executive', 'employee')


def roles_required(*roles):
    """
    Decorator — aborts with 403 if the logged-in user's role
    is not in the allowed list.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.role not in roles:
                return render_template('errors/403.html'), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def hr_only(f):
    return roles_required(*HR_ROLES)(f)

def bd_only(f):
    return roles_required(*BD_ROLES)(f)

def admin_only(f):
    return roles_required(*ADMIN_ONLY)(f)
