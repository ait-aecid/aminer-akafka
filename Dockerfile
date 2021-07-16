# aminer-akafka Dockerfile
#
# Build:
#    docker build -t aecid/akafka:latest -t aecid/akafka:$(grep '__version__ =' akafka/metadata.py | awk -F '"' '{print $2}') .
#

# Pull base image.
FROM python:3.8
LABEL maintainer="wolfgang.hotwagner@ait.ac.at"

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt
RUN make install

ENTRYPOINT ["/usr/local/bin/akafkad.py"]
