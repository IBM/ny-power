FROM ubuntu:18.04

ENV DEBIAN_FRONTEND noninteractive
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV FLASK_APP /www/app.py

RUN apt-get update && apt-get install -y python3 python3-pip && apt-get clean

RUN pip3 install -U flask
RUN pip3 install -U influxdb
RUN pip3 install -U paho-mqtt
RUN rm -rf /root/.cache

RUN groupadd -r www && useradd --no-log-init -r -g www www
RUN mkdir -p /www/ && chown -R www /www

COPY app.py /www/
COPY templates/ /www/templates/
COPY static/ /www/static/

EXPOSE 5000

USER www

CMD flask run --host=0.0.0.0
