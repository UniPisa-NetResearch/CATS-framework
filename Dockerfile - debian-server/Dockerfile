FROM debian

RUN apt-get update && apt-get upgrade -y && apt-get install -y \
  curl \
  sudo \
  nftables \
  apt-utils \
  openssh-server \
  vim \
  dnsutils \
  wget \
  iputils-ping \
  tcpdump \
  net-tools \
  traceroute \
  iproute2 \
  ifupdown \
  ifupdown-extra \
  python3 \
  python3-pip \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*
  
RUN apt install -y netcat

RUN pip3 install pandas --break-system-packages
RUN pip3 install flask --break-system-packages
RUN pip3 install kubernetes --break-system-packages

# COPY SCRIPTS
COPY ClientServerApp/TCP/server.py /home/TCP/server.py
COPY c-sma/rest_server.py /home/c-sma/rest_server.py
COPY c-sma/config.json /home/c-sma/config.json