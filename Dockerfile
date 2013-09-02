FROM ubuntu
MAINTAINER jerome.petazzoni@dotcloud.com
RUN apt-get install -qy python
ADD . /
CMD python /gunsub.py
