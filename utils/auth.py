from functools import wraps
from flask_jwt_extended import current_user

def require_permission(permission: str):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not getattr(current_user.role, permission, False):
                return {"msg": "Not authorized!"}, 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator