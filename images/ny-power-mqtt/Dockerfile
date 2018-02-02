FROM ubuntu:xenial

ENV DEBIAN_FRONTEND noninteractive

USER root

RUN apt-get update && apt-get install -y mosquitto

COPY mqtt_acl.conf /etc/mqtt_acl.conf

COPY run.sh /root/run.sh

COPY acl_file.conf /etc/mosquitto/conf.d/acl_file.conf
COPY mosquitto.conf /etc/mosquitto/mosquitto.conf

RUN echo "port 1883" > /etc/mosquitto/conf.d/mqtt_port.conf

EXPOSE 1883

CMD ["/root/run.sh"]
