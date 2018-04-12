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

```mustache

{{/* vim: set filetype=mustache: */}}
{{/*
Expand the name of the chart.
*/}}
{{- define "ny-power.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "ny-power.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- if contains $name .Release.Name -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}
{{- end -}}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "ny-power.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" -}}
{{- end -}}

```

Everytime you do a `helm install` a uniq release name is generated
(which you can provide if you want). The default `_helpers` file
creates some utility variables that can be used in
templates. `ny-power.fullname` being the critical one, as that will be
different between two different installations of the ny-power app.

The other default templates can be deleted, they aren't very useful if
you already have your application specified in kubernetes yaml.


# A Helmified Example: MQTT #

The following is the definition to bring up the MQTT server:

```yaml

apiVersion: v1
kind: Secret
metadata:
  name: {{ template "ny-power.fullname" . }}-mqtt-pump
type: Opaque
data:
  password: {{ .Values.mqtt.secret | trim | b64enc }}
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: {{ template "ny-power.fullname" . }}-mqtt-nfs
  annotations:
    volume.beta.kubernetes.io/storage-class: {{ .Values.mqtt.storage.class }}
  labels:
    app: {{ template "ny-power.name" . }}-mqtt
    chart: {{ template "ny-power.chart" . }}
    release: {{ .Release.Name }}
    heritage: {{ .Release.Service }}
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: {{ .Values.mqtt.storage.size }}
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ template "ny-power.fullname" . }}-mqtt
  labels:
    app: {{ template "ny-power.name" . }}-mqtt
    chart: {{ template "ny-power.chart" . }}
    release: {{ .Release.Name }}
    heritage: {{ .Release.Service }}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: {{ template "ny-power.name" . }}-mqtt
      release: {{ .Release.Name }}
  template:
    metadata:
      labels:
        app: {{ template "ny-power.name" . }}-mqtt
        release: {{ .Release.Name }}
    spec:
      volumes:
        - name: {{ template "ny-power.fullname" . }}-mqtt-volume
          persistentVolumeClaim:
            claimName: {{ template "ny-power.fullname" . }}-mqtt-nfs
      containers:
        - name: {{ template "ny-power.fullname" . }}-mqtt
          image: "{{ .Values.image.repository }}/{{.Values.mqtt.image.name }}:{{.Values.mqtt.image.version }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          env:
            - name: MQTT_PUMP_PASS
              valueFrom:
                secretKeyRef:
                  name: {{ template "ny-power.fullname" . }}-mqtt-pump
                  key: password
          volumeMounts:
            - name: {{ template "ny-power.fullname" . }}-mqtt-volume
              mountPath: "/shared"
          ports:
            - containerPort: 80
            - containerPort: 1883
---
apiVersion: v1
kind: Service
metadata:
  name: {{ template "ny-power.fullname" . }}-mqtt
  labels:
    app: {{ template "ny-power.name" . }}-mqtt
    chart: {{ template "ny-power.chart" . }}
    release: {{ .Release.Name }}
    heritage: {{ .Release.Service }}
spec:
  type: LoadBalancer
  ports:
  - port: 1883
    targetPort: 1883
    name: mqtt
    protocol: TCP
  - port: 80
    targetPort: 80
    name: http
    protocol: TCP
  selector:
    app: {{ template "ny-power.name" . }}-mqtt
    release: {{ .Release.Name }}

```

This includes 4 resources, a Secret, Persistent Volume Claim,
Deployment, and Service in a single file. The MQTT server needs
persistent storage to provide retain messages, especially in the event
the pod crashes.

The important things to highlight are the following. The name for
every resource is based on `{{ template "ny-power.fullname" . }}`,
which means that it might be something like
`lovely-sasquatch-ny-power` if left to autogeneration, or
`prod-ny-power` if you set it manually.

Every resource has a set of labels which include the `app`, `chart`,
and `release`. As you can see, the Service selector needs to use both
`app` and `release` to correctly bind to the right container. Without
this it couldn't distinguish between different installed versions.

And lastly you'll see `.Values` references. These are references to
the values.yaml we looked at previously. It means there is one single
place to update these.
