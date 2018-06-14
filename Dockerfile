FROM ubuntu:16.04

RUN apt-get update
RUN apt-get install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa -y
RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        build-essential \
        python3.6 \
        python3.6-dev \
        python3-pip \
        python-setuptools \
        cmake \
        wget \
        curl \
        libsm6 \
        libxext6 \ 
        libxrender-dev

RUN curl https://bootstrap.pypa.io/get-pip.py | python3.6

COPY requirements.txt /tmp

WORKDIR /tmp

RUN python3.6 -m pip install -r requirements.txt

COPY . /emotion-recognition-service

WORKDIR /emotion-recognition-service

# EXPOSES the port where jsonrpc is being heard.
EXPOSE 8001

CMD ['python3.6', 'run-snet-service.py']
