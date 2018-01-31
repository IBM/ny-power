#!/usr/bin/env python3

import csv
import datetime
import json
import logging
import io
import os
import time
import urllib.request

import paho.mqtt.client as mqtt

FUEL_MIX="http://mis.nyiso.com/public/csv/rtfuelmix/{0}rtfuelmix.csv"

_LOGGER = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    level=logging.DEBUG)

HOST = os.environ.get("MQTT_HOST")

def collect_data():
    now = datetime.datetime.now()
    url = FUEL_MIX.format(now.strftime("%Y%m%d"))

    # unfortunately we can't quite connect urllib to csv
    with urllib.request.urlopen(url) as response:
        out = io.StringIO()
        out.write(response.read().decode('utf-8'))

    # We have to rewind the output stream so it can be read by
    # csv.reader
    out.seek(0)
    reader = csv.reader(out, quoting=csv.QUOTE_NONE)
    data = []
    last = ""
    for row in reader:
        last = row[0]
        data.append(row)

    return data

def send_last_to_mqtt(data, last_sent=""):
    client = mqtt.Client(clean_session=True)
    client.connect(HOST)

    last = ""
    for r in data:
        last = r[0]

    retval = None
    for r in data:
        if r[0] == last and r[0] != last_sent:
            _LOGGER.info("Found new data to publish: %s", r)
            client.publish("ny-power/fuel-mix/{0}".format(r[2]),
                           json.dumps(dict(ts=r[0], power=r[3], units="kW")),
                           qos=1)
            retval = r[0]
    if retval is not None:
        client.publish("ny-power/updated/fuel-mix",
                       json.dumps(dict(ts=r[0])), qos=1, retain=True)
    client.disconnect()
    return retval


def main():
    last = ""
    while(True):
        _LOGGER.info("Starting main loop!")
        data = collect_data()
        ret_last = send_last_to_mqtt(data, last)
        if ret_last is not None:
            last = ret_last
        _LOGGER.info("Sleeping")
        time.sleep(60)


if __name__ == "__main__":
    main()
