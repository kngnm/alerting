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

influxdb_data = "cups_queue_size,printer={0} value={1}"

while True:
    try:
        jobs_page = requests.get("http://{0}:{1}/jobs".format(
            os.environ["CUPS_HOST"],
            os.environ["CUPS_PORT"]
        ))
        if jobs_page.status_code < 300:
            jobs_page = jobs_page.text
            jobs = re.findall('<TR VALIGN="TOP">\n<TD><A HREF="[^"]*">([^<]+)</A>[^<]*</TD>', jobs_page)
            queues = {}
            for job in jobs:
                if job not in queues:
                    queues[job] = 0
                queues[job] += 1
            for printer, queue_size in queues.items():
                requests.post(influxdb_url, influxdb_data.format(printer, queue_size))
    except:
        pass
    time.sleep(5)
