import os

MQTT_HOST = os.environ.get("MQTT_HOST")
TOPIC_UPSTREAM = "ny-power/upstream/"
TOPIC_COMPUTED = "ny-power/computed/"
TOPIC_STATUS = "ny-power/status/"
TOPIC_FUEL_UPDATED = "ny-power/status/fuel-mix/updated"


def get_pass():
    with open("/etc/secret-volume/password") as f:
        return f.read()
