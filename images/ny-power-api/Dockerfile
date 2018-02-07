FROM ubuntu:xenial

ENV DEBIAN_FRONTEND noninteractive

USER root

RUN apt-get update && apt-get install -y python3 python3-pip

RUN pip3 install -U flask
RUN pip3 install -U influxdb

COPY app.py /root/app.py
COPY templates/ /root/templates/

EXPOSE 5000

CMD LANG=C.UTF-8 LC_ALL=C.UTF-8 FLASK_APP=/root/app.py flask run --host=0.0.0.0
