import os

from flask import Flask, jsonify
from influxdb import InfluxDBClient

app = Flask(__name__)

INFLUXDB_HOST = os.environ.get("INFLUXDB_HOST")
MQTT_HOST = os.environ.get("MQTT_HOST")

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
