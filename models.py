from app import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from typing import List


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    last_seen_lat = db.Column(db.Float())
    last_seen_lon = db.Column(db.Float())
    last_seen_time = db.Column(db.DateTime())
    token = db.Column(db.String(64), unique=True, nullable=False)
    firebase_uid = db.Column(db.String(128))
    firebase_subscriptions = db.relationship("FirebaseSubscription", backref="user", lazy=True)

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class FirebaseSubscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    firebase_token = db.Column(db.String(4096), nullable=False)


class Earthquake(db.Model):
    position_lat = db.Column(db.Float(), nullable=False)
    position_lon = db.Column(db.Float(), nullable=False)
    magnitude = db.Column(db.Float(), nullable=False)
    occurred_at = db.Column(db.DateTime(), nullable=False)

    @property
    def strain_radius(self):
        return 10 ** (0.43 * self.magnitude)

    def users_in_danger(self, users: List[User]):
        users_in_danger = []
        for user in users:
            if distance_between_points(
                self.position_lon, user.last_seen_lon, self.position_lat, user.last_seen_lat
            ):
                users_in_danger.append(user)
        return users_in_danger
