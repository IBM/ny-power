[![Build Status](https://travis-ci.org/IBM/ny-power.svg?branch=master)](https://travis-ci.org/IBM/ny-power)

# Making public data available as an event stream #

We recently bought a Chevy Bolt EV, which we use as our primary
vehicle. We charge at home with a Level 2 charger. When should we
charge the car?

Static time of use billing in our area marks peak at 2pm - 7pm
weekdays. While that's the only time the power company doesn't want
you to charge, the grid varies a lot over the course of the day to
match demand. The New York State Indepdendent System Operator
([NYISO](http://www.nyiso.com/public/index.jsp)) is responsible for
managing the power grid in NY State. They provide near real time data
about what fuel sources are being used to generate electricity in NY
State.

![NY Power Realtime Grid](web/images/screenshot_372.png)

While the data that powers this is public, there is no public API. The
NY ISO does publish a set of 5 minute resolution CSV files on their
servers at http://mis.nyiso.com/public/. These are updated every 5 to
20 minutes.

Instead of having every application parse CSV files directly, we can
do better by making the data into a real time stream. This is done by
polling and parsing the CSV in a micro service and publishing new
events to a public [MQTT](http://mqtt.org/) service. The overhead for
consuming a public MQTT service is very low, and requires just an open
socket. After injesting this data we can also provide "value add"
analysis of it, such as computing the estimated CO<sub>2</sub> emitted
per kWh of electricity generated over the course of the day. This
added value data is also published on the MQTT bus and can be consumed
directly.

A web page which connects directly to the MQTT service over a
websocket shows how you can provide a dyanmic web site with no server
polling, only updating when relevant data is provided.

The entire application is deployed in Kubernetes using Helm. This
makes it possible to bring up new copies of the application with very
few user steps, and work on a development version of the application
while a production version is running.

When the user has completed this Code Pattern they will understand how
to:

* Use an MQTT server to provide real time event stream
* Consume an MQTT stream directly from a web browser
* Deploy an application on Kubernetes with Helm

## Flow

![Architecture Diagram](web/images/arch-diagram.png)

1. The user accesses the website
2. The webrowser directly accesses the MQTT service
3. The applications data pump polls NY ISO every minute looking for
   new data.
4. Data is pushed to MQTT service
5. The archiver is subscribed to the MQTT service sends all new data
   to Influx DB
6. On any new data it computes current CO<sub>2</sub> / kWh, and
   publishes both it, and the recent time series to the MQTT service.

## Included components

* IBM Cloud Container Service

## Featured technologies

* [Kubernetes](https://kubernetes.io/): container orchestration
* [Helm](https://docs.helm.sh/): application packaging and deployment
  for Kubernetes
* [MQTT](http://mqtt.org/): light weight publish / subscribe protocol
* [Mosquitto](https://mosquitto.org/): open source MQTT broker
* [Influxdb](https://www.influxdata.com/): time series database
* [Python](https://www.python.org/): main programming language used for all logic

# Watch the video

# Steps

## 1. Install and configure Helm

Install Helm. Full instructions are
at [docs.helm.sh](https://docs.helm.sh/using_helm/#installing-helm)

Create a new cluster in IBM Cloud and initialize helm for it:

```
# Create cluster
$ bx cs cluster-create <clustername>

# Set kubectl config for it
$ $(bx cs cluster-config <clusternam> | grep export)

# Initialize helm
$ helm init
```

## 2. Configure Container Registry

The ny-power application needs to upload a number of custom
images. You need to create a custom container registry to upload into.

```
$ bx cr namespace-add ny-power
```

## 3. Build required images

5 images are needed for the application to run. In order to simplify
this there are 2 makefile targets that exist to generate and display
versions of the 5 images. When build images is called the version
number for the image is incremented every time to allow for rolling
upgrades.

```
# generate all images
$ make build-images
```

The image versions can be displayed with

```
$ make image-versions
```

## 4. Update Helm values.yaml

Open up `ny-power/values.yaml` and edit the image versions in the
yaml.

You can optionally change the shared secret under `mqtt.secret` as
well. This is a shared secret needed to provide write access to the
mqtt stream.

## 5. Install with Helm

```
$ heml install ny-power
```

This will autogenerate a unique name such as laughing-frog. Helm
allows you to have more than one version of an application running at
the same time in the same cluster for developent, qa, or A/B testing
purposes.

You can see the status of deployment with:

```
$ heml status <laughing-frog>
```

## 6. Make changes and experiment

As you make changes to the application, either in the helm
configuration, or make changes to the applications and images, you can
do a live upgrade of the cluster.

Set any updated image versions in your `values.yaml` and run:

```
$ helm upgrade <laughing-frog> ny-power
```

# Sample output

## Deployment

A successful deployment looks like the following:

```
$ helm status lovely-sasquatch
LAST DEPLOYED: Mon Apr  9 10:03:51 2018
NAMESPACE: default
STATUS: DEPLOYED

RESOURCES:
==> v1/Secret
NAME                                 TYPE    DATA  AGE
lovely-sasquatch-ny-power-mqtt-pump  Opaque  1     5h

==> v1/PersistentVolumeClaim
NAME                                  STATUS  VOLUME                                    CAPACITY  ACCESS MODES  STORAGECLASS      AGE
lovely-sasquatch-ny-power-influx-nfs  Bound   pvc-47abb773-3bf4-11e8-aca5-da75763193ce  20Gi      RWX           ibmc-file-silver  5h
lovely-sasquatch-ny-power-mqtt-nfs    Bound   pvc-47ac4f95-3bf4-11e8-aca5-da75763193ce  20Gi      RWX           ibmc-file-silver  5h

==> v1/Role
NAME                                       AGE
lovely-sasquatch-ny-power-services-reader  5h

==> v1/RoleBinding
NAME                                     AGE
lovely-sasquatch-ny-power-read-services  5h

==> v1/Service
NAME                              TYPE          CLUSTER-IP      EXTERNAL-IP   PORT(S)                      AGE
lovely-sasquatch-ny-power-influx  ClusterIP     172.21.251.185  <none>        8086/TCP                     5h
lovely-sasquatch-ny-power-mqtt    LoadBalancer  172.21.112.218  169.60.82.10  1883:30350/TCP,80:30403/TCP  5h
lovely-sasquatch-ny-power-web     LoadBalancer  172.21.27.24    169.60.82.12  80:32332/TCP                 4h

==> v1/Deployment
NAME                               DESIRED  CURRENT  UP-TO-DATE  AVAILABLE  AGE
lovely-sasquatch-ny-power-archive  1        1        1           1          5h
lovely-sasquatch-ny-power-pump     1        1        1           1          5h
lovely-sasquatch-ny-power-influx   1        1        1           1          5h
lovely-sasquatch-ny-power-mqtt     1        1        1           1          5h
lovely-sasquatch-ny-power-web      2        2        2           2          4h

==> v1/Pod(related)
NAME                                                READY  STATUS   RESTARTS  AGE
lovely-sasquatch-ny-power-archive-7c4fb447f7-vxhf7  1/1    Running  0         5h
lovely-sasquatch-ny-power-pump-86dd6fd597-77dtp     1/1    Running  1         5h
lovely-sasquatch-ny-power-influx-687bbffbc5-z586j   1/1    Running  0         5h
lovely-sasquatch-ny-power-mqtt-5c4d7744b5-pp77l     1/1    Running  0         5h
lovely-sasquatch-ny-power-web-764dd7797c-95wsl      1/1    Running  0         4h
lovely-sasquatch-ny-power-web-764dd7797c-x9dfv      1/1    Running  0         4h

```

## Application

A successful deployment of the application will look as follows:

![NY Power intensity](/web/images/ny-power-web.png)

This visualizes a number of things:

1. The current carbon intensity of the NY ISO grid
2. A historical view of carbon intensity over the last 20 hours to
   visualize trends
3. The current mix of fuels in the NY ISO grid

All of these will be updated everytime there is new information
published on the MQTT bus with no user interaction or polling needed.

# Links

# Learn more

* **Container Orchestration Code Patterns**: Enjoyed this Code Pattern? Check out our other [Container Orchestration Code Patterns](https://developer.ibm.com/code/technologies/container-orchestration/).
* **Kubernetes on IBM Cloud**: Deliver your apps with the combined power of [Kubernetes and Docker on IBM Cloud](https://www.ibm.com/cloud-computing/bluemix/containers)

# License
[Apache 2.0](LICENSE)
