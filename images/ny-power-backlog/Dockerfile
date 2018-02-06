FROM ubuntu:xenial

ENV DEBIAN_FRONTEND noninteractive

USER root

RUN apt-get update && apt-get install -y python3 python3-pip

RUN pip3 install -U influxdb

COPY process.py /root/process.py

CMD /usr/bin/python3 /root/process.py
