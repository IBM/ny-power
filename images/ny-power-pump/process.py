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

# PWR in MWh
# CO2 in Metric Tons

FUEL_2016 = {
    "Petroleum": {
        "Power": 642952,
        "CO2": 623836
    },
    "Natural Gas": {
        "Power": 56793336,
        "CO2": 26865277
    }
}

# assume Dual Fuel systems consume 30% of state NG. That's probably low.
FUEL_2016["Dual Fuel"] = {
    "Power": (FUEL_2016["Petroleum"]["Power"] + (FUEL_2016["Natural Gas"]["Power"] * .3)),
    "CO2": (FUEL_2016["Petroleum"]["CO2"] + (FUEL_2016["Natural Gas"]["CO2"] * .3)),
}

# Calculate CO2 per kWh usage

def co2_for_fuel(fuel):
    if fuel in FUEL_2016:
        hpow = FUEL_2016[fuel]["Power"]
        hco2 = FUEL_2016[fuel]["CO2"]
        co2per = float(hco2) / float(hpow)
        return co2per
    else:
        return 0.0

def get_pass():
    with open("/etc/secret-volume/password") as f:
        return f.read()

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
    client.username_pw_set("pump", get_pass())
    client.connect(HOST)

    last = ""
    for r in data:
        last = r[0]

    retval = None
    kW = 0
    co2 = 0
    for r in data:
        if r[0] == last and r[0] != last_sent:
            _LOGGER.info("Found new data to publish: %s", r)
            client.publish("ny-power/fuel-mix/{0}".format(r[2]),
                           json.dumps(
                               dict(ts=r[0], power=int(float(r[3])), units="kW")),
                           qos=1, retain=True)
            retval = r[0]
            kW += float(r[3])
            co2 += float(r[3]) * co2_for_fuel(r[2])

    _LOGGER.info("Last connect time is %s", retval)

    if kW:
        co2_per_kW = co2 / kW
        client.publish("ny-power/co2",
                       json.dumps(dict(ts=retval, emissions=co2_per_kW, units="kg / kWh")),
                       qos=1, retain=True)

    if retval is not None:
        client.publish("ny-power/updated/fuel-mix",
                       json.dumps(dict(ts=retval)), qos=1, retain=True)
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
