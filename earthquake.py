import datetime
import requests
import pytz
import urllib


def get_earthquake_data():
    now = datetime.datetime.now(tz=pytz.UTC)
    earlier = (now - datetime.timedelta(minutes=10)).isoformat()

    url = "https://earthquake.usgs.gov/fdsnws/event/1/query?" + urllib.parse.urlencode(
        {"format": "csv", "starttime": earlier, "endtime": now}
    )

    response = requests.get(url)
    data = response.content
    return data
