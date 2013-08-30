FROM ubuntu
MAINTAINER jerome.petazzoni@dotcloud.com
RUN apt-get install python
ADD . /
CMD python /gunsub.py