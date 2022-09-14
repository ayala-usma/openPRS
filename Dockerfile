## NOTE: Running this container this way  docker run -it <name> bash

## Using the base Debian 11 Bullseye image with python 3.10. This image uses the amd64 architecture for the binaries that is somewhat slower in Mac ARM chips
FROM --platform=linux/amd64 ubuntu:18.04
LABEL org.opencontainers.image.authors=" David Aurelia Ayala Usma <ayala.usma@gmail.com>"

## Copying files into container
RUN mkdir -p /home/gl_test
RUN mkdir -p /home/gl_test/datasets
RUN mkdir -p /home/gl_test/src
COPY datasets/ /home/gl_test/datasets
COPY src/ /home/gl_test/src
COPY prs_workflow_exec.sh /home/gl_test
COPY requirements.txt /home/gl_test

## Installing dependencies
RUN DEBIAN_FRONTEND=noninteractive apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install htop python3.8-minimal python3-pip git
RUN DEBIAN_FRONTEND=noninteractive update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 1
RUN DEBIAN_FRONTEND=noninteractive update-alternatives --config python3
RUN python3 -m pip install --upgrade pip
RUN pip3 install -r /home/gl_test/requirements.txt

## Running the entire workflow
CMD bash /home/gl_test/prs_workflow_exec.sh