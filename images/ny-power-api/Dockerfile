FROM ubuntu:xenial

ENV DEBIAN_FRONTEND noninteractive
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV FLASK_APP /root/app.py

USER root

RUN apt-get update && apt-get install -y python3 python3-pip && apt-get clean

RUN pip3 install -U flask
RUN pip3 install -U influxdb
RUN pip3 install -U paho-mqtt
RUN rm -rf /root/.cache

COPY app.py /root/app.py
COPY templates/ /root/templates/
COPY static/ /root/static/

EXPOSE 5000

CMD flask run --host=0.0.0.0
