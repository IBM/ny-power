FROM ubuntu:xenial

ENV DEBIAN_FRONTEND noninteractive

USER root

RUN apt-get update && apt-get dist-upgrade -y && apt-get install -y mosquitto && apt-get clean

COPY mqtt_acl.conf /etc/mqtt_acl.conf

COPY run.sh /root/run.sh

COPY acl_file.conf /etc/mosquitto/conf.d/acl_file.conf
COPY mosquitto.conf /etc/mosquitto/mosquitto.conf

EXPOSE 1883
EXPOSE 80

CMD ["/root/run.sh"]
