## NOTE: Running this container this way  docker run -it <name> bash

## Using the base Ubuntu 18.04 image
FROM ubuntu:18.04
LABEL org.opencontainers.image.authors=" David Aurelia Ayala Usma <ayala.usma@gmail.com>"

## Making source files available
RUN mkdir /home/gl_test
COPY . /home/gl_test

## Installing dependencies
RUN DEBIAN_FRONTEND=noninteractive apt update
RUN DEBIAN_FRONTEND=noninteractive apt -y install htop python3.8 python3-pip git
RUN DEBIAN_FRONTEND=noninteractive update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 1
RUN DEBIAN_FRONTEND=noninteractive update-alternatives --config python3
RUN python3 -m pip install --upgrade pip
RUN pip3 install -r /home/gl_test/requirements.txt