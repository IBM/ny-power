MQTT_IMAGE=ny-power-mqtt
API_IMAGE=ny-power-api
ARCHIVE_IMAGE=ny-power-archive
PUMP_IMAGE=ny-power-pump
INFLUXDB_IMAGE=ny-power-influxdb
BACKLOG_IMAGE=ny-power-backlog
IMAGE_REG=registry.ng.bluemix.net/sdague/
BASE_IMAGE=ny-power-base

all: mqtt pump


mqtt:
	bx cr build -t $(IMAGE_REG)$(MQTT_IMAGE) images/$(MQTT_IMAGE)
	kubectl apply -f deploy/ny-power-mqtt-deploy.yaml

api:
	bx cr build -t $(IMAGE_REG)$(API_IMAGE) images/$(API_IMAGE)
	kubectl delete -f deploy/ny-power-api-deploy.yaml || /bin/true
	kubectl apply -f deploy/ny-power-api-deploy.yaml


archive:
	bx cr build -t $(IMAGE_REG)$(ARCHIVE_IMAGE) images/$(ARCHIVE_IMAGE)
	kubectl delete -f deploy/ny-power-archive-deploy.yaml || /bin/true
	kubectl apply -f deploy/ny-power-archive-deploy.yaml

mqtt-delete:
	kubectl delete -f deploy/ny-power-mqtt-deploy.yaml

influxdb:
	bx cr build -t $(IMAGE_REG)$(INFLUXDB_IMAGE) images/$(INFLUXDB_IMAGE)
	kubectl apply -f deploy/ny-power-influxdb-deploy.yaml

images/$(BASE_IMAGE)/nypower:
	git clone https://github.com/sdague/nypower images/$(BASE_IMAGE)/nypower

base-image: images/$(BASE_IMAGE)/nypower
	cd images/$(BASE_IMAGE)/nypower && git pull
	bx cr build -t $(IMAGE_REG)$(BASE_IMAGE) images/$(BASE_IMAGE)

backlog:
	bx cr build -t $(IMAGE_REG)$(BACKLOG_IMAGE) images/$(BACKLOG_IMAGE)
	kubectl delete -f deploy/ny-power-backlog-job.yaml
	kubectl create -f deploy/ny-power-backlog-job.yaml

pump-delete:
	kubectl delete -f deploy/ny-power-pump-deploy.yaml

pump:
	bx cr build -t $(IMAGE_REG)$(PUMP_IMAGE) images/$(PUMP_IMAGE)
	kubectl delete -f deploy/ny-power-pump-deploy.yaml
	kubectl apply -f deploy/ny-power-pump-deploy.yaml

mqtt-service: mqtt
	kubectl apply -f deploy/ny-power-svc.yaml

mqtt-secret:
	kubectl create secret generic mqtt-pump-secret --from-literal=password=$(shell pwgen 16 1)

token:
	kubectl config view -o jsonpath='{.users[0].user.auth-provider.config.id-token}'
	@echo
	@echo
	@echo Run \"kubectl proxy\" and use the above token
