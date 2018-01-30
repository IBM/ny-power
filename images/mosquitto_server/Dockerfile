FROM ubuntu:xenial

ENV DEBIAN_FRONTEND noninteractive

USER root

RUN apt-get update && apt-get install -y mosquitto

RUN echo "port 1883" > /etc/mosquitto/conf.d/mqtt_port.conf

EXPOSE 1883

CMD ["/usr/sbin/mosquitto"]