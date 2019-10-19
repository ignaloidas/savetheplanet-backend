import datetime
import io
import urllib
from math import atan2, cos, radians, sin, sqrt

import pandas as pd
import pytz
import requests

from .models import Earthquake


def get_earthquake_data(time_in_minutes):
    now = datetime.datetime.now(tz=pytz.UTC)
    earlier = (now - datetime.timedelta(minutes=time_in_minutes)).isoformat()

    url = "https://earthquake.usgs.gov/fdsnws/event/1/query?" + urllib.parse.urlencode(
        {"format": "csv", "starttime": earlier, "endtime": now}
    )

    response = requests.get(url)
    data = response.content
    return data


def get_clean_data(time_in_minutes=60):
    disasters = []
    df = pd.read_csv(io.BytesIO(get_earthquake_data(time_in_minutes)))
    df = df[["time", "latitude", "longitude", "mag"]]
    for index, row in df.iterrows():
        time = row["time"]
        latitude = row["latitude"]
        longitude = row["longitude"]
        mag = row["mag"]
        earthquake = Earthquake(
            position_lat=latitude,
            position_lon=longitude,
            magnitude=mag,
            occurred_at=datetime.datetime.utcfromtimestamp(time / 1000),
        )
        disasters.append(earthquake)

    return disasters


def get_important_earthquakes(minutes=60):
    earthquakes = get_clean_data(minutes)
    important_earthquakes = []
    for earthquake in earthquakes:
        if earthquake.magnitude >= 2.5:
            important_earthquakes.append(earthquake)
    return important_earthquakes
