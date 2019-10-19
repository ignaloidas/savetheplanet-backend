from typing import List

from firebase_admin import messaging

from models import FirebaseSubscription, User
from utils import chunks


def send_firebase_notifications(users: List[User], data_to_send):
    failed_users = []
    for user in users:
        for subscription in user.firebase_subscriptions:
            message = messaging.MulticastMessage(tokens=token_group, data=data_to_send)
            try:
                response = messaging.send_multicast(message)
            except:
                response = None

            if response and response.success:
                break
        else:
            failed_users.append(user)
    return failed_users


def send_twilio_notifications(users: List[User], data_to_send):
    pass  # TODO