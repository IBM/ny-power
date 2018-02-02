#!/bin/bash

set -x -e

PASS=$(cat /etc/secret-volume/password)

touch /etc/mqtt_pass
/usr/bin/mosquitto_passwd -b /etc/mqtt_pass pump ${PASS}

mkdir -p /shared/mqtt || /bin/true
chown -R mosquitto.mosquitto /shared/mqtt

exec /usr/sbin/mosquitto -c /etc/mosquitto/mosquitto.conf
