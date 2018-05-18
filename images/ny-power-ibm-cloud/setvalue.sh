#!/bin/bash

set -x

# First set the service IP

function set_external_ip {
    for i in {1..300}; do
        MQTT_HOST=$(kubectl get svc ${MQTT_CONTAINER_NAME}  -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
        if [[ -z "$MQTT_HOST" ]]; then
            echo "Waiting for external ip to be assigned... sleeping"
            sleep 2
        else
            kubectl delete secret ${MQTT_SECRET_NAME}
            kubectl create secret generic ${MQTT_SECRET_NAME} --from-literal=host=${MQTT_HOST}
            rc=$?
            if [[ "$rc" -ne 0 ]]; then
                echo "Failed to set secret"
                exit 1
            else
                return
            fi
        fi
    done

    echo "Time ran out waiting for service ip to be visable"
    exit 1

}

function wait_for_mqtt {
    for i in {1..300}; do
        # Attempt to connect to the MQTT server
        nc ${MQTT_HOST} 1883 -w 3 << EOF
HELLO
EOF
        rc=$?
        if [[ "$rc" -ne 0 ]]; then
            echo "Waiting for MQTT to be ready... sleeping"
            sleep 2
        else
            return
        fi
    done

    echo "Time ran out waiting for mqtt to be visable"
    exit 1
}

set_external_ip
wait_for_mqtt

exit 0
