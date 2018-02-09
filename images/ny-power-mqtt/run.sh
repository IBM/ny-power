#!/bin/bash

set -x -e

touch /etc/mqtt_pass
/usr/bin/mosquitto_passwd -b /etc/mqtt_pass pump ${MQTT_PUMP_PASS}

mkdir -p /shared/mqtt || /bin/true
chown -R mosquitto.mosquitto /shared/mqtt

exec /usr/sbin/mosquitto -c /etc/mosquitto/mosquitto.conf
