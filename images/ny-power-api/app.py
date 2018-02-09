import logging
import os

from flask import Flask, jsonify, render_template
from influxdb import InfluxDBClient
import paho.mqtt.publish as publish


_LOGGER = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    level=logging.DEBUG)

app = Flask(__name__)

INFLUXDB_HOST = os.environ.get("INFLUXDB_HOST")
MQTT_HOST = os.environ.get("MQTT_HOST")
MQTT_PUMP_PASS = os.environ.get("MQTT_PUMP_PASS")

# This signals that we've loaded new code, which means maybe the
# client apps should reload
_LOGGER.info("Try to send mqtt packet")
publish.single("ny-power/application/webui", "reload", hostname=MQTT_HOST,
               auth={"username": "pump", "password": MQTT_PUMP_PASS})
_LOGGER.info("Should have been sent")

@app.route("/")
def index():
    return render_template("index.html", mqtt_host=MQTT_HOST)

@app.route("/current/co2")
def current_co2():
    client = InfluxDBClient(HOST, 8086, 'root', 'root', 'fuel-mix')
    results = client.query("select last(value) from co2_current")
    points = results.get_points()
    val = next(points)
    return jsonify({"value": val["last"], "time": val["time"], "units": "kg / kWh"})

@app.route("/range/co2")
def range_co2():
    client = InfluxDBClient(HOST, 8086, 'root', 'root', 'fuel-mix')
    results = client.query("select value from co2_current")
    points = results.get_points()

    rval = []
    for point in points:
        point["units"] = "kg / kWh"
        rval.append(point)
    return jsonify(rval)
