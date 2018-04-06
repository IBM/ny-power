MQTT_IMAGE=ny-power-mqtt
WEB_IMAGE=ny-power-api
INFLUXDB_IMAGE=ny-power-influxdb
IMAGE_REG=registry.ng.bluemix.net/sdague/
BASE_IMAGE=ny-power-base
VERSION=1

all:

ibm-cloud-image:
	VERSION=$(shell ./serial.sh ny-power/versions/ibm-cloud); \
	bx cr build -t $(IMAGE_REG)ny-power-ibm-cloud:$$VERSION images/ny-power-ibm-cloud

base-image: images/$(BASE_IMAGE)/nypower
	VERSION=$(shell ./serial.sh ny-power/versions/base); \
	bx cr build -t $(IMAGE_REG)$(BASE_IMAGE):$$VERSION images/$(BASE_IMAGE)

influx-image:
	VERSION=$(shell ./serial.sh ny-power/versions/influx); \
	bx cr build -t $(IMAGE_REG)$(INFLUXDB_IMAGE):$$VERSION images/$(INFLUXDB_IMAGE)

mqtt-image:
	VERSION=$(shell ./serial.sh ny-power/versions/mqtt); \
	bx cr build -t $(IMAGE_REG)$(MQTT_IMAGE):$$VERSION images/$(MQTT_IMAGE)

web-image:
	VERSION=$(shell ./serial.sh ny-power/versions/web); \
	bx cr build -t $(IMAGE_REG)$(WEB_IMAGE):$$VERSION images/$(WEB_IMAGE)

images/$(BASE_IMAGE)/nypower:
	git clone https://github.com/sdague/nypower images/$(BASE_IMAGE)/nypower

build-images: base-image influx-image mqtt-image web-image ibm-cloud-image

token:
	kubectl config view -o jsonpath='{.users[0].user.auth-provider.config.id-token}'
	@echo
	@echo
	@echo Run \"kubectl proxy\" and use the above token
