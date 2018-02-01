MQTT_IMAGE=ny-power-mqtt
PUMP_IMAGE=ny-power-pump
IMAGE_REG=registry.ng.bluemix.net/sdague/

all: mqtt-service mqtt pump

mqtt:
	bx cr build -t $(IMAGE_REG)$(MQTT_IMAGE) images/$(MQTT_IMAGE)
	kubectl delete -f deploy/ny-power-mqtt-deploy.yaml || /bin/true
	kubectl create -f deploy/ny-power-mqtt-deploy.yaml

pump:
	bx cr build -t $(IMAGE_REG)$(PUMP_IMAGE) images/$(PUMP_IMAGE)
	kubectl delete -f deploy/ny-power-pump-deploy.yaml || /bin/true
	kubectl create -f deploy/ny-power-pump-deploy.yaml

mqtt-service: mqtt
	kubectl delete -f deploy/ny-power-svc.yaml || /bin/true
	kubectl create -f deploy/ny-power-svc.yaml

mqtt-secret:
	kubectl create secret generic mqtt-pump-secret --from-literal=password=$(shell pwgen 16 1)

token:
	kubectl config view -o jsonpath='{.users[0].user.auth-provider.config.id-token}'
	@echo
