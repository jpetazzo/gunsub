FROM ubuntu
MAINTAINER jerome.petazzoni@dotcloud.com
RUN apt-get install -qy python
ADD gunsub.py /gunsub.py
CMD python /gunsub.py
