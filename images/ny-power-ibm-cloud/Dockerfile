FROM ubuntu:xenial

ENV DEBIAN_FRONTEND noninteractive
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

USER root

RUN apt-get update && apt-get install curl -y

# IBM Cloud CLI comes from a sudo bash installer
RUN curl -sL https://ibm.biz/idt-installer -o /root/idt-installer
RUN bash /root/idt-installer

COPY setvalue.sh /root/setvalue.sh
