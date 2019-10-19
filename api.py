from datetime import datetime

import pytz
from firebase_admin import auth
from flask import Blueprint, abort, jsonify, request
from flask_login import login_user

from app import db, firebase_app
from models import User
from utils import generate_random_string, require_authentication

api = Blueprint("api", __name__)


@api.route("/update_location", methods=["POST"])
@require_authentication
def update_location(user: User):
    if not request.is_json():
        abort(400, "Not JSON")
    data = request.json

    lat = data.get("lat")
    lon = data.get("lon")

    if not (lat or lon):
        abort(400, "No lat/lon")

    time = datetime.now(tz=pytz.UTC)

    user.last_seen_lat = lat
    user.last_seen_lon = lon
    user.last_seen_time = time

    db.session.add(user)
    db.session.commit()

    return jsonify(msg="success"), 200


@api.route("/register", methods=["POST"])
def register():
    if not request.is_json():
        abort(400, "Not JSON")
    data = request.json

    user = User()

    password = data.get("password")
    email = data.get("email")

    if not (password and email):
        abort(400, "Password and email not given")

    token = generate_random_string(64)

    firebase_user = auth.create_user(
        email=email, email_verified=False, password=password, disabled=False
    )

    user.password = password
    user.email = email
    user.token = token
    user.firebase_uid = firebase_user.uid

    db.session.add(user)
    db.session.commit()

    login_user(user)

    return jsonify(token=token), 200


@api.route("/login", methods=["POST"])
def login():
    if not request.is_json():
        abort(400, "Not JSON")
    data = request.json

    password = data.get("password")
    email = data.get("email")

    if not (password and email):
        abort(400, "Password and email not given")

    user = User.query.filter(User.email == email).one_or_none()
    if user and user.verify_password(password):
        login_user(user)
        return jsonify(token=user.token)
    abort(400, "Incorrect username or password")


@api.route("/get_firebase_token")
@require_authentication
def get_firebase_token(user: User):
    uid = user.firebase_uid

    custom_token = auth.create_custom_token(uid)

    return jsonify(firebase_token=custom_token), 200
