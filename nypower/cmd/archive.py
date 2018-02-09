import json
import logging
import os

import click
import paho.mqtt.client as mqtt

from nypower.archive import Archiver
from nypower.mqtt import get_pass


_LOGGER = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    level=logging.DEBUG)

INFLUXDB_HOST = os.environ.get("INFLUXDB_HOST")
MQTT_HOST = os.environ.get("MQTT_HOST")


def on_connect(client, userdata, flags, rc):
    _LOGGER.info("Connected to mqtt bus")
    client.subscribe("ny-power/#")


# NOTE(sdague): there is a bootstrapping problem here
def on_message(client, userdata, msg):
    influx = client.influx
    if msg.topic == "ny-power/computed/co2":
        influx.save_computed(msg.topic, msg.payload)
        # and archive
        since = "24h"
        series = influx.get_timeseries("co2_computed", since)
        client.publish("ny-power/archive/co2/%s" % since,
                       json.dumps(series),
                       qos=2, retain=True)
    if "ny-power/upstream/fuel-mix" in msg.topic:
        influx.save_upstream(msg.topic, msg.payload)


def mqtt_client(influxclient):
    client = mqtt.Client(clean_session=True)
    client.influx = influxclient
    client.username_pw_set("pump", get_pass())
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_HOST)
    return client


@click.command()
def main(args=None):
    """Archive power records to influxdb."""
    mqtt = mqtt_client(Archiver())
    mqtt.loop_forever()


if __name__ == "__main__":
    main()
