import pandas as pd
import datetime
import requests
import pytz
import urllib
import pandas as pd
import io


class Earthquake:
    def __init__(self, longitude, latitude, magnitude, time):
        self.longitude = longitude
        self.latitude = latitude
        self.magnitude = magnitude
        self.time = time

    def get_radius():  # TODO
        self.radius = 1

    def debug_message():
        print(
            f"Type: {self.type}\nLongitude: {self.longitude}\nLatitude: {self.latitude}\nTimestamp: {self.time}"
        )


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


disasters = get_clean_data()
