from flask import request
from functools import wraps


def require_authentication(func):
    @wraps(func)
    def decorator():
        pass

    return decorator
