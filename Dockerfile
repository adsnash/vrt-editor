# use 18.04 base because ubuntugis ppa is currently broken for 20.04
FROM ubuntu:18.04

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV TERM=linux

# use app as working directory
WORKDIR /app

# ask no questions
ENV DEBIAN_FRONTEND=noninteractive

# update
RUN apt-get update && apt-get upgrade -y

# install deps
RUN apt-get install -y \
    software-properties-common \
    vim \
    wget \
    git \
    python3-dev \
    python3-pip

# install gdal the easy way
RUN add-apt-repository ppa:ubuntugis/ppa && \
    apt-get update && \
    apt-get install -y \
        gdal-bin \
        libgdal-dev \
        python3-gdal
ARG CPLUS_INCLUDE_PATH=/usr/include/gdal
ARG C_INCLUDE_PATH=/usr/include/gdal
RUN pip3 install GDAL

# copy everything over
COPY . .

# install the repo
RUN python3 setup.py install

# run the tests
RUN pytest
