# Practical Helm #

When you first get started with Kubernetes, it's exciting. You create
deployment yaml files, they create pods which auto restart when things
go wrong, and life is good. All of this is done with `kubectl`, which
is straight forward once you learn the verbs and resource types it can
support. But as the complexity of what you are doing with Kubernetes
moves beyond trivial examples, managing that via kubectl gets
challenging... fast.

What if you need to test a tweak to a resource, but keep the existing
production one deployed? How do you upgrade the production one once
you have changes you like? Helm helps with these.

## Helm Key Features ##

Helm calls itself the package manager for Kubernetes. As someone
steeped in decades of Linux package management, this explaination was
actually confusing to me. Because Helm does nothing to help you manage
images, which is a key part of Linux package management.

The thing that made Helm click for me was thinking of it as 3 things:

* Templating for `kubectl` files
* A set of conventions for those templates which allow multiple
  simultaneous deployments
* A state engine running in the kubernetes cluster that helps with
  upgrading an application

While there are other things Helm can do, taking this practical view
made it easier for me to start using Helm effectively.

# Example Application: ny-power.org #

Let's look at a medium complexity
application: [ny-power.org](http://ny-power.org). This provides an
MQTT event stream of the current fuel sources used to generate
electricity in the State of New York, as well as current, and recent
carbon intensitity of that fuel mix. It also provides a web dashboard
to see that data.

It works through having 5 different microservices; 5 different
container images; 2 pods with persistent storage; 2 services with
external IP addresses; and 1 custom role to expose MQTT external
address to other services; and 1 shared secret for writing to the MQTT
service. It's enough complexity to start to show where helm becomes
more useful than managing eveything yourself.


## helm create ##

Helm's unit of operation is a `chart`. There will be a single chart
for this application, it makes it a single unit to understand.

```bash
$ helm create ny-power
Creating ny-power
```

When you create a new chart it creates boiler plate files, some which
are more useful than others.

```bash
$ ls -lR ny-power
ny-power:
total 16
drwxr-xr-x 2 sdague sdague 4096 Apr 12 15:01 charts/
-rw-r--r-- 1 sdague sdague  104 Apr 12 15:01 Chart.yaml
drwxr-xr-x 2 sdague sdague 4096 Apr 12 15:01 templates/
-rw-r--r-- 1 sdague sdague 1023 Apr 12 15:01 values.yaml

ny-power/charts:
total 0

ny-power/templates:
total 20
-rw-r--r-- 1 sdague sdague 1371 Apr 12 15:01 deployment.yaml
-rw-r--r-- 1 sdague sdague 1048 Apr 12 15:01 _helpers.tpl
-rw-r--r-- 1 sdague sdague  976 Apr 12 15:01 ingress.yaml
-rw-r--r-- 1 sdague sdague 1411 Apr 12 15:01 NOTES.txt
-rw-r--r-- 1 sdague sdague  487 Apr 12 15:01 service.yaml
```

### Chart.yaml ###

`Chart.yaml` is metadata for the whole chart:

```yaml

apiVersion: v1
appVersion: "1.0"
description: A Helm chart for Kubernetes
name: ny-power
version: 0.1.0
```

You can adjust `description`, `version` to your liking, the others are
to be left alone. `name` should not be changed after it's initially
set.


### values.yaml ###

`values.yaml` is where you store values that will be used in the
templates later. That should includes image names and versions, and
any tunables in your application. This is the values.yaml file for
ny-power:

```yaml

replicaCount: 2

mqtt:
  secret: AbadSecret
  image:
    name: ny-power-mqtt
    version: 4
  storage:
    size: 1Gi
    class: "ibmc-file-silver"

influx:
  image:
    name: ny-power-influxdb
    version: 3
  storage:
    size: 20Gi
    class: "ibmc-file-silver"

base:
  image:
    name: ny-power-base
    version: 7

ibmCloud:
  image:
    name: ny-power-ibm-cloud
    version: 5

web:
  image:
    name: ny-power-web
    version: 15

image:
  repository: registry.ng.bluemix.net/ny-power
  tag: stable
  pullPolicy: Always

```

Mostly this is about the 5 images in question, however it also
specifies the size and class of storage we need, and a secret.

### _helpers.tpl ###

The `_helpers.tpl` file is part of the convention of making Helm
applications able to deploy more than one copy.
