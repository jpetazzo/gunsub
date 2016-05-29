FROM ubuntu
MAINTAINER jerome.petazzoni@dotcloud.com
RUN apt-get install -qy python python-pandas
ADD gunsub.py /gunsub.py
CMD python /gunsub.py
