FROM ubuntu:xenial

ENV DEBIAN_FRONTEND noninteractive
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

USER root

RUN apt-get update && apt-get install curl netcat -y && apt-get clean

RUN curl -LO https://storage.googleapis.com/kubernetes-release/release/v1.10.0/bin/linux/amd64/kubectl
RUN install -m 755 kubectl /usr/bin

COPY setvalue.sh /root/setvalue.sh
