import random
import string
from functools import wraps
from math import atan2, cos, radians, sin, sqrt

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


def chunks(iter, size):
    for i in range(0, len(iter), size):
        yield iter[i : i + size]


def distance_between_points(lon1, lon2, lat1, lat2):
    lon1 = radians(lon1)
    lon1 = radians(lon2)
    lat1 = radians(lat1)
    lat2 = radians(lat2)
    R = 6373.0
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance
