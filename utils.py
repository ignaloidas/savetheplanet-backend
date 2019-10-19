# fmt:off
import random
import string
from functools import wraps

from flask import request
from flask_login import current_user

from models import User


def require_authentication(func):
    @wraps(func)
    def decorator():
        if current_user.is_authenticated:
            return func(current_user)
        if (auth := request.headers.get("Authentication")) is not None and (
            user := User.query.filter(User.token == auth).one_or_none()
        ) is not None:
            return func(user)
        else:
            abort(403, "Unauthorized")

    return decorator


def generate_random_string(stringLength):
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(stringLength))
