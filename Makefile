MQTT_IMAGE=ny-power-mqtt
WEB_IMAGE=ny-power-api
INFLUXDB_IMAGE=ny-power-influxdb
IMAGE_REG=registry.ng.bluemix.net/sdague/
BASE_IMAGE=ny-power-base
VERSION=1
VERSION_DIR=.img-versions

all:

$(VERSION_DIR):
	mkdir -p $(VERSION_DIR)

ibm-cloud-image: $(VERSION_DIR)
	VERSION=$(shell ./serial.sh $(VERSION_DIR)/ibm-cloud); \
	bx cr build -t $(IMAGE_REG)ny-power-ibm-cloud:$$VERSION images/ny-power-ibm-cloud

base-image: $(VERSION_DIR)
	VERSION=$(shell ./serial.sh $(VERSION_DIR)/base); \
	bx cr build -t $(IMAGE_REG)$(BASE_IMAGE):$$VERSION src/

influx-image: $(VERSION_DIR)
	VERSION=$(shell ./serial.sh $(VERSION_DIR)/influx); \
	bx cr build -t $(IMAGE_REG)$(INFLUXDB_IMAGE):$$VERSION images/$(INFLUXDB_IMAGE)

mqtt-image: $(VERSION_DIR)
	VERSION=$(shell ./serial.sh $(VERSION_DIR)/mqtt); \
	bx cr build -t $(IMAGE_REG)$(MQTT_IMAGE):$$VERSION images/$(MQTT_IMAGE)

web-image: $(VERSION_DIR)
	VERSION=$(shell ./serial.sh $(VERSION_DIR)/web); \
	bx cr build -t $(IMAGE_REG)$(WEB_IMAGE):$$VERSION images/$(WEB_IMAGE)

build-images: base-image influx-image mqtt-image web-image ibm-cloud-image

image-versions:
	for f in $(VERSION_DIR)/*; do \
		echo $$(basename $$f) $$(cat $$f); \
	done

token:
	kubectl config view -o jsonpath='{.users[0].user.auth-provider.config.id-token}'
	@echo
	@echo
	@echo Run \"kubectl proxy\" and use the above token
