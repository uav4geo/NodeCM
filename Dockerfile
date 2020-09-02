FROM nvidia/cuda:10.2-devel-ubuntu16.04

# Install Node.js
RUN apt-get -qq update && apt-get -qq install -y --no-install-recommends wget
RUN wget --no-check-certificate https://deb.nodesource.com/setup_10.x -O /tmp/node.sh && bash /tmp/node.sh
RUN apt-get -qq update && apt-get -qq install -y nodejs

#Install dependencies and required requisites
RUN apt-get update && apt-get install -y software-properties-common && \
    add-apt-repository -y ppa:ubuntugis/ubuntugis-unstable && \
    apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    libboost-program-options-dev \
    libboost-filesystem-dev \
    libboost-graph-dev \
    libboost-regex-dev \
    libboost-system-dev \
    libboost-test-dev \
    libeigen3-dev \
    libsuitesparse-dev \
    libfreeimage-dev \
    libgoogle-glog-dev \
    libgflags-dev \
    libglew-dev \
    qtbase5-dev \
    libqt5opengl5-dev \
    libatlas-base-dev \
    libsuitesparse-dev \
    libtiff-dev \
    libpng-dev \
    libjpeg-dev \
    libvtk6-dev \
    python-dev \
    python-gdal \
    python-pip \
    python-wheel \
    python-setuptools \
    gdal-bin \
    libgdal-dev \
    libtbb2 \
    libtbb-dev \
    libeigen3-dev \
    libflann-dev \
    libboost-date-time-dev \
    libboost-filesystem-dev \
    libboost-iostreams-dev \
    libboost-log-dev \
    libboost-python-dev \
    libboost-regex-dev \
    libboost-thread-dev \
    wget \
    exiftool \
    p7zip-full

# Install latest cmake
RUN wget -O /tmp/cmake.sh https://github.com/Kitware/CMake/releases/download/v3.18.0/cmake-3.18.0-Linux-x86_64.sh && sh /tmp/cmake.sh --prefix=/usr --skip-license

ADD . /app
WORKDIR /app

RUN ldconfig && mkdir build && cd build && cmake .. && make -j$(nproc)
RUN mkdir modules/build && cd modules/build && cmake .. && make -j$(nproc) && make install && ldconfig

RUN pip install -r requirements.txt 

RUN (rm -r NodeODM || true) && git submodule update --init && cd NodeODM && npm install --quiet

# Cleanup APT
RUN apt-get clean \
  && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
  && rm -fr /app/build /app/modules/build

WORKDIR /app/NodeODM

ENTRYPOINT ["/usr/bin/nodejs", "/app/NodeODM/index.js", "--odm_path", "/app"]