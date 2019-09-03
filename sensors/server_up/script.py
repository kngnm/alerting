import requests
import time
import os, sys
import re

influxdb_url = "http://{0}:{1}/write?u={2}&p={3}&db={4}".format(
    os.environ["INFLUXDB_HOST"],
    os.environ["INFLUXDB_PORT"],
    os.environ["INFLUXDB_USER"],
    os.environ["INFLUXDB_PASS"],
    os.environ["INFLUXDB_DB"]
)

influxdb_data = "server_up,server={0} value=".format(
    os.environ["SERVER_URL"]
)+"{0}"

while True:
    up = 0
    try:
        assert requests.get(os.environ["SERVER_URL"]).status_code < 300
        up = 1
    except:
        pass
    requests.post(influxdb_url, influxdb_data.format(up))
    time.sleep(5)
