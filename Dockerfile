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
    cmake \
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

ADD . /app
WORKDIR /app

RUN cd NodeODM && npm install --quiet

RUN mkdir build && cd build && cmake .. && make -j$(nproc)
RUN mkdir modules/build && cd modules/build && cmake .. && make -j$(nproc) && make install && ldconfig

RUN pip install -r requirements.txt 

# Cleanup APT
RUN apt-get clean \
  && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
  && rm -fr /app/build /app/modules/build

# Entry point
ENTRYPOINT ["bash"]