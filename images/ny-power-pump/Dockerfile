FROM ubuntu:xenial

ENV DEBIAN_FRONTEND noninteractive

USER root

RUN apt-get update && apt-get install -y python3 python3-pip git

# RUN pip3 install -U git+git://github.com/sdague/nypower.git

COPY nypower/ /root/nypower/

RUN pip3 install -U /root/nypower/

CMD LC_ALL=C.UTF-8 LANG=C.UTF-8 /usr/local/bin/ny-power-pump
