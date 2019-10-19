import datetime
import requests
import pytz
import urllib
import pandas as pd
import io


def get_earthquake_data(time_in_minutes=10):
    now = datetime.datetime.now(tz=pytz.UTC)
    earlier = (now - datetime.timedelta(minutes=time_in_minutes)).isoformat()

    url = "https://earthquake.usgs.gov/fdsnws/event/1/query?" + urllib.parse.urlencode(
        {"format": "csv", "starttime": earlier, "endtime": now}
    )

    response = requests.get(url)
    data = response.content
    return data


df = pd.read_csv(io.BytesIO(get_earthquake_data(100)))
df = df[["time", "latitude", "longitude", "mag"]]
print(df.head())
# print(list(df))

# pd.read_csv(get_earthquake_data())

"""
"""
