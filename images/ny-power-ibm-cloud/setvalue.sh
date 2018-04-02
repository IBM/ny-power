#!/bin/bash

set -x

for i in {1..300}; do
    MQTT_HOST=$(kubectl get svc ${MQTT_CONTAINER_NAME}  -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
    if [[ -z "$MQTT_HOST" ]]; then
        sleep 2
    else
        kubectl create secret generic ${MQTT_SECRET_NAME} --from-literal=host=${MQTT_HOST}
        exit 0
    fi
done

exit 1
