# -*- coding: utf-8 -*-

"""Console script for nypower."""

import json
import logging
import time

import click
import paho.mqtt.client as mqtt

from nypower.collector import timestamp2epoch, get_fuel_mix
from nypower import mqtt as mq

_LOGGER = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    level=logging.DEBUG)

LAST = 0


def on_connect(client, userdata, flags, rc):
    _LOGGER.info("Connected to mqtt bus")
    client.subscribe(mq.TOPIC_FUEL_UPDATED)


# NOTE(sdague): there is a bootstrapping problem here
def on_message(client, userdata, msg):
    if msg.topic == mq.TOPIC_FUEL_UPDATED:
        global LAST
        data = json.loads(msg.payload.decode('utf-8'))
        LAST = timestamp2epoch(data["ts"])


def mqtt_client():
    client = mqtt.Client(clean_session=True)
    client.username_pw_set("pump", mq.get_pass())
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(mq.MQTT_HOST)
    client.loop_start()
    return client


def catchup_mqtt(client, data):
    global LAST
    now = LAST

    for timestamp, reading in data.items():
        strtime = reading.time
        if reading.epoch <= now:
            continue

        for fuel_name, kW in reading.fuels.items():
            topic = "{0}fuel-mix/{1}".format(mq.TOPIC_UPSTREAM, fuel_name)
            _LOGGER.info("%s => %s" % (topic, strtime))

            client.publish(topic,
                           json.dumps(
                               dict(ts=strtime, power=kW, units="kW")),
                           qos=1, retain=True)

        client.publish("{0}co2".format(mq.TOPIC_COMPUTED),
                       json.dumps(
                           dict(ts=strtime,
                                emissions=reading.co2_g_per_kW / 1000,
                                units="kg / kWh")),
                       qos=1, retain=True)

        client.publish(mq.TOPIC_FUEL_UPDATED,
                       json.dumps(dict(ts=strtime)), qos=1, retain=True)


@click.command()
def main(args=None):
    """Console script for nypower."""
    global LAST

    client = mqtt_client()
    while True:

        for x in range(60):
            if LAST > 0:
                break
            _LOGGER.info("Waiting for LAST to increase!")
            time.sleep(1)
        else:
            LAST = 1

        data = get_fuel_mix()
        catchup_mqtt(client, data)

        _LOGGER.info("Sleeping for the next cycle")
        time.sleep(60)

    click.echo("Replace this message by putting your code into "
               "nypower.cli.main")
    click.echo("See click documentation at http://click.pocoo.org/")


if __name__ == "__main__":
    main()
