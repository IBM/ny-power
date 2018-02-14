#!/usr/bin/env python3

import os
import subprocess

PASSWORD=os.environ.get("MQTT_PASS", "")

OLD_TOPICS = [
    "ny-power/updated/fuel-mix",
    "ny-power/fuel-mix/Dual Fuel",
    "ny-power/fuel-mix/Natural Gas",
    "ny-power/fuel-mix/Nuclear",
    "ny-power/fuel-mix/Other Fossil Fuels",
    "ny-power/fuel-mix/Other Renewables",
    "ny-power/fuel-mix/Wind",
    "ny-power/fuel-mix/Hydro",
    "ny-power/co2",
    "ny-power/archive/co2_24h"
]

for topic in OLD_TOPICS:
    cmd = ["/usr/bin/mosquitto_pub", "-u", "pump", "-P", PASSWORD,
           "-h", "mqtt.ny-power.org",
           "-t", topic,
           "-m", "",
           "-r"]
    print(cmd)
    subprocess.run(cmd)
