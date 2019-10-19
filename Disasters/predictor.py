import pandas as pd
import datetime
import requests
import pytz
import urllib
import pandas as pd
import io
from math import sin, cos, sqrt, atan2, radians, sqrt


class Earthquake:
    def __init__(self, longitude, latitude, magnitude, time):
        self.longitude = longitude
        self.latitude = latitude
        self.magnitude = magnitude
        self.time = time
        self.strain_radius = 10 ** (0.43 * magnitude)

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

    def debug_message(self):
        print(
            f"Longitude: {self.longitude}\nLatitude: {self.latitude}\nTimestamp: {self.time}\nMagnitude: {self.magnitude}\nImpact radius: {self.strain_radius}"
        )

    def user_in_danger(self, users):
        users_in_danger = []
        for user in users:
            if distance_between_points(
                self.longitude, user.longitude, self.latitude, user.latitude
            ):
                users_in_danger.append(user)
        return users_in_danger


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
        earthquake = Earthquake(longitude, latitude, mag, time)
        disasters.append(earthquake)

    return disasters


def explain_list(disasters):
    print(f"There was a total of: {len(disasters)}")
    important_earthquake = []
    for earthquake in disasters:
        if earthquake.magnitude >= 3:
            important_earthquake.append(earthquake)

    print(f"There was a total of: {len(important_earthquake)} with magnitude >= 3")
    print(disasters[0].debug_message())


disasters = get_clean_data(1440)
explain_list(disasters)
