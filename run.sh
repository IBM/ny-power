#!/bin/bash

bx cr build -t registry.ng.bluemix.net/sdague/ny-power-mosquitto images/ny-power-mqtt
bx cr build -t registry.ng.bluemix.net/sdague/ny-power-pump images/ny-power-pump

kubectl delete -f ny-power-deploy.yaml

kubectl create -f ny-power-deploy.yaml
