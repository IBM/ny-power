# Practical Helm #

When you first get started with Kubernetes, it's exciting. You create
deployment yaml files, they create pods which auto restart when things
go wrong, and life is good. All of this is done with `kubectl`, which
is straight forward once you learn the verbs and resource types it can
support. But as the complexity of what you are doing with Kubernetes
moves beyond trivial examples, managing that via `kubectl` gets
challenging... fast.

What if you need to test a tweak to a resource, but keep the existing
production one deployed? How do you upgrade the production one once
you have changes you like? Helm helps with these.

## Helm Key Features ##

Helm calls itself the package manager for Kubernetes. As someone
steeped in decades of Linux package management, this explanation was
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
carbon intensity of that fuel mix. It also provides a web dashboard
to see that data.

It works through having 5 different microservices; 5 different
container images; 2 pods with persistent storage; 2 services with
external IP addresses; and 1 custom role to expose MQTT external
address to other services; and 1 shared secret for writing to the MQTT
service. It's enough complexity to start to show where helm becomes
more useful than managing everything yourself.


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
any tunables in your application. This is the `values.yaml` file for
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
the `values.yaml` we looked at previously. It means there is one single
place to update these. As we'll see later, you can also create
additional overrides here for specific deployments.

# Handling Service Dependencies, Kube API, and ACLs #

One of the surprising things I found was that Helm *does not* do
anything around waiting for services to be ready before starting
others. It is just translating all the templates to kubenetes yaml,
submitting them to the API, and considering it done.

In looking around for best practices here, the current community
pattern is using `initContainers` to delay launching certain services
until their dependencies are ready.

In the `ny-power` application we need to have access to the External
IP address of the MQTT service before the web UI starts. That web UI
is connecting directly to the MQTT service from the user's browser. So
we have a web init container that runs in a polling loop before the
web console starts.

```yaml

...
      initContainers:
      - name: {{ template "ny-power.fullname" . }}-web-init
        image: "{{ .Values.image.repository }}/{{.Values.ibmCloud.image.name }}:{{.Values.ibmCloud.image.version }}"
        imagePullPolicy: {{ .Values.image.pullPolicy }}
        command: ["/root/setvalue.sh"]
        env:
          - name: MQTT_CONTAINER_NAME
            value: {{ template "ny-power.fullname" . }}-mqtt
          - name: MQTT_SECRET_NAME
            value: {{ template "ny-power.fullname" . }}-mqtt
...

```

This is running the following code to poll for the loadBalancer IP
address, and once found set a secret with it's value.

```bash

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

```

Starting in Kubernetes 1.9 the API inside the cluster is disabled by
default. So out of the box the above script would fail with a
permissions problem. The following role definition enables just the
getting of service credentials, and the setting of secrets. As secrets
still can't be read this is a relatively low risk set of exposures.

```yaml

kind: Role
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  namespace: default
  name: {{ template "ny-power.fullname" . }}-services-reader
rules:
- apiGroups: [""] # "" indicates the core API group
  resources: ["services"]
  verbs: ["get"]
- apiGroups: [""] # "" indicates the core API group
  resources: ["secrets"]
  verbs: ["create"]
---
kind: RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: {{ template "ny-power.fullname" . }}-read-services
  namespace: default
subjects:
- kind: Group
  name: system:serviceaccounts
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: {{ template "ny-power.fullname" . }}-services-reader
  apiGroup: rbac.authorization.k8s.io
```

Together these allow us to use an initContainer to wait for, and
discover a derived value (an external IP address) of the application,
and hand it off to the deploy container as a secret.


# Installing with helm #

Because we've been careful in using these templated names everywhere,
installation of the application much simpler.

```
$ helm install ny-power/

NAME:   calling-stingray
LAST DEPLOYED: Thu Apr 12 16:12:56 2018
NAMESPACE: default
STATUS: DEPLOYED

RESOURCES:
==> v1/PersistentVolumeClaim
NAME                                  STATUS   VOLUME            CAPACITY  ACCESS MODES  STORAGECLASS  AGE
calling-stingray-ny-power-influx-nfs  Pending  ibmc-file-silver  0s
calling-stingray-ny-power-mqtt-nfs    Pending  ibmc-file-silver  0s

==> v1/Role
NAME                                       AGE
calling-stingray-ny-power-services-reader  0s

==> v1/RoleBinding
NAME                                     AGE
calling-stingray-ny-power-read-services  0s

==> v1/Service
NAME                              TYPE          CLUSTER-IP     EXTERNAL-IP   PORT(S)                      AGE
calling-stingray-ny-power-influx  ClusterIP     172.21.151.78  <none>        8086/TCP                     0s
calling-stingray-ny-power-mqtt    LoadBalancer  172.21.84.221  169.60.82.11  1883:30865/TCP,80:30111/TCP  0s
calling-stingray-ny-power-web     LoadBalancer  172.21.65.246  <pending>     80:32431/TCP                 0s

==> v1/Deployment
NAME                               DESIRED  CURRENT  UP-TO-DATE  AVAILABLE  AGE
calling-stingray-ny-power-pump     1        1        1           0          0s
calling-stingray-ny-power-archive  1        1        1           0          0s
calling-stingray-ny-power-influx   1        1        1           0          0s
calling-stingray-ny-power-mqtt     1        1        1           0          0s
calling-stingray-ny-power-web      2        0        0           0          0s

==> v1/Pod(related)
NAME                                                READY  STATUS             RESTARTS  AGE
calling-stingray-ny-power-archive-5bf4546d67-vss6d  0/1    ContainerCreating  0         0s
calling-stingray-ny-power-pump-7cd4f6b558-8p8z4     0/1    ContainerCreating  0         0s
calling-stingray-ny-power-influx-7d54ccc6db-bkdls   0/1    Pending            0         0s
calling-stingray-ny-power-mqtt-dbd85777c-h76dk      0/1    Pending            0         0s
calling-stingray-ny-power-web-6b9ffc644b-4ts2w      0/1    Init:0/1           0         0s
calling-stingray-ny-power-web-6b9ffc644b-dhh52      0/1    Init:0/1           0         0s

==> v1/Secret
NAME                                 TYPE    DATA  AGE
calling-stingray-ny-power-mqtt-pump  Opaque  1     0s

```

... that's it. The automatically generated name (calling-stingray in
this case) will be shown as well as the initial `helm status` output.

The ny-power application takes about 5 minutes to fully provision,
largely because of it's two persistent storage backends.

# Upgrading with helm #

After your initial install, every other operation on the application
should be an upgrade. You can change any of the templates, rebuild
images and change their version numbers in `values.yaml`, or any other
change to the application. After that, a `helm upgrade
calling-stingray` will upgrade the application. Helm is stateful
enough to understand both changes to existing resources, and that some
resources may no longer exist after your changes (and delete them).

# Dev, Qa, Prod #

One of the values of the templating and the conventions is that it
becomes quite reasonable to spin up different versions of the
application for development.

```
$ helm install -n prod ny-power/ -f prod-values.yaml
$ helm install -n dev ny-power/
$ helm install -n my-odd-feature ny-power/
```

All of these will safely coexist within a single Kubernetes cluster,
and not interfere with each other. In the prod case we can even give
it a more secure mqtt password in an overlay `values.yaml` file, or give
new image versions to the dev cluster.

Many of these instances of the application might be long running, in
which case `upgrade` is the right way to move them forward. Some might
be single use to test a patch manually or via continuous integration,
in this case `helm delete` does a good job completely cleaning up
after the installation afterwards.

# Being Practical with Helm #

My experiences with Helm thus far is that it's extremely useful when
you focus on those three key features:

* Templating for `kubectl` files
* A set of conventions for those templates which allow multiple
  simultaneous deployments
* A state engine running in the kubernetes cluster that helps with
  upgrading an application

With that it makes it much easier to iterate on your deployment
architecture, try out new ideas, and rollback when required. It also
makes it much easier to hand off to other people in a way that they
can install it. This process drastically simplified the ny-power
application, which had gotten pretty unwieldly as a set of 15 kubectl
files. The stateful upgrade also means you can evolve naming in your
deployment without having to worry about cleaning up old bad
resources.

If you are spending time with Kubernetes, Helm is definitely worth
investing time to get comfortable with, and put into your
toolbox. Hopefully this practical introduction is helpful in starting
that journey.
