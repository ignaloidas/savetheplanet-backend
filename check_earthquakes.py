import json
from app import create_app
from celery_factory import make_celery
from earthquake import get_important_earthquakes
from models import Earthquake, User
from notifications import send_firebase_notifications, send_twilio_notifications
from utils import circle_to_polygon

app = create_app()

celery = make_celery(app)


@celery.task
def check_earthquakes():
    to_save = []
    users = User.query.all()
    earthquakes = get_important_earthquakes(10)
    for earthquake in earthquakes:
        if Earthquake.query.filter(Earthquake.occurred_at == earthquake.occurred_at).count() > 0:
            continue  # we already have this one
        else:
            to_save.append(earthquake)
        affected_users = earthquake.users_in_danger(users)
        if affected_users:
            data = {
                "json": json.dumps(
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": circle_to_polygon(
                                [earthquake.position_lat, earthquake.position_lon],
                                earthquake.strain_radius,
                            ),
                        },
                        "properties": {
                            "type": "earthquake",
                            "occurred_at": earthquake.occurred_at.timestamp(),
                            "magnitude": earthquake.magnitude,
                        },
                    }
                )
            }
            print(data)
            failed_users = send_firebase_notifications(users, data)
            # SMS fallback
            send_twilio_notifications(failed_users, data)  # TODO probably change
    return earthquakes
