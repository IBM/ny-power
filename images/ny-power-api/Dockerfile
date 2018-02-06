FROM ubuntu:xenial

ENV DEBIAN_FRONTEND noninteractive

USER root

RUN apt-get update && apt-get install -y python3 python3-pip

RUN pip3 install -U flask
RUN pip3 install -U influxdb

COPY app.py /root/app.py
COPY templates/ /root/templates/

CMD FLASK_APP=app.py flask run
