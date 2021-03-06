FROM python:3.6-slim-stretch

RUN apt-get -y update
RUN apt-get install -y --fix-missing \
    build-essential \
    cmake \
    gfortran \
    libmagic1 \
    git \
    wget \
    curl \
    graphicsmagick \
    libgraphicsmagick1-dev \
    libatlas-base-dev \
    libavcodec-dev \
    libavformat-dev \
    libgtk2.0-dev \
    libjpeg-dev \
    liblapack-dev \
    libswscale-dev \
    pkg-config \
    python3-dev \
    python3-numpy \
    software-properties-common \
    zip \
    && apt-get clean && rm -rf /tmp/* /var/tmp/*

COPY . /root/user-mgmt
RUN cd /root/user-mgmt && \
    pip3 install Flask-RESTful Flask bcrypt python-magic Flask-JWT-Extended redis flask_cors uwsgi pymongo 
EXPOSE 5000
CMD cd /root/user-mgmt && \
    uwsgi --ini deployment/uwsgi.ini 