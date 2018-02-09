#!/usr/bin/env python3

import collections
import csv
import datetime
import json
import logging
import io
import os
import time
import urllib.request

import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient

_LOGGER = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    level=logging.DEBUG)

INFLUXDB_HOST = os.environ.get("INFLUXDB_HOST")
MQTT_HOST = os.environ.get("MQTT_HOST")

def get_pass():
    with open("/etc/secret-volume/password") as f:
        return f.read()

def on_connect(client, userdata, flags, rc):
    _LOGGER.info("Connected to mqtt bus")
    client.subscribe("ny-power/#")

# NOTE(sdague): there is a bootstrapping problem here
def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode('utf-8'))
    influxclient = client.influx
    if msg.topic == "ny-power/computed/co2":
        co2_to_influx(influxclient, data)
        co2_archive_to_mqtt(client, influxclient)
    if "ny-power/upstream/fuel-mix" in msg.topic:
        fuel = msg.topic.split("/")[-1]
        fuel_to_influx(influxclient, fuel, data)

def co2_archive_to_mqtt(client, influx):
    res = influx.query("select value*1000 from co2_current where time >= now() - 24h")
    data = []
    ts = []
    for r in res.get_points():
        ts.append(r["time"])
        data.append(r["value"])
    client.publish("ny-power/archive/co2_24h",
                   json.dumps(dict(units="g / kWh", data=data, ts=ts)),
                   qos=2, retain=True)


def co2_to_influx(client, data):
    pkt = [
        {
            "measurement": "co2_current",
            "time": data["ts"],
            "fields": {
                "value": data["emissions"]
            }
        }
    ]
    client.write_points(pkt)

def fuel_to_influx(client, fuel, data):
    pkt = [
        {
            "measurement": "fuel_mix_current",
            "tags": {
                "fuel_type": fuel
            },
            "time": data["ts"],
            "fields": {
                "value": data["power"]
            }
        }
    ]
    client.write_points(pkt)


def mqtt_client(influxclient):
    client = mqtt.Client(clean_session=True)
    client.influx = influxclient
    client.username_pw_set("pump", get_pass())
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_HOST)
    return client

def main():
    client = InfluxDBClient(INFLUXDB_HOST, 8086, 'root', 'root', 'fuel-mix')
    dbs = [x['name'] for x in client.get_list_database()]
    if 'fuel-mix' not in dbs:
        client.create_database('fuel-mix')
    mqtt = mqtt_client(client)
    mqtt.loop_forever()


if __name__ == "__main__":
    main()
