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

influxdb_data = "link_connectivity,link={0} value=".format(
    os.environ["LINK_TO"]
)+"{0}"

while True:
    ping_output = os.popen("ping -f -q -c 100 -W 1 {0}".format(
            os.environ["LINK_TO"]
        )
    ).read()
    try:
        total_time = int(re.findall("time (\\d+)ms", ping_output)[0])
        recvd = int(re.findall("([0-9]+) received", ping_output)[0])
        requests.post(influxdb_url, influxdb_data.format(0.0056 * recvd / (total_time / 1000)))
    except:
        assert False, sys.exc_info()
        requests.post(influxdb_url, influxdb_data.format(0))
    time.sleep(5)
