FROM debian:12

# ENV
ENV CONTAINER_IMAGE_VERSION="v1.0.0"
ENV TZ="Europe/Rome"
ENV USER_NAME="frruser"
ENV USER_PASSWORD="frruser"
ENV ROOT_PASSWORD="root"

RUN echo $CONTAINER_IMAGE_VERSION
RUN echo $TZ
RUN echo $USER_NAME
RUN echo $USER_PASSWORD
RUN echo $ROOT_PASSWORD

# ADD USERS
RUN echo 'root:${ROOT_PASSWORD}' | chpasswd
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN adduser --quiet --disabled-password --shell /bin/zsh --home /home/$USER_NAME --gecos "User" $USER_NAME
RUN echo "${USER_NAME}:${USER_PASSWORD}" | chpasswd && usermod -aG sudo $USER_NAME

# UPDATE THE BASE AND INSTALL REQUIRED PACKAGES
RUN apt-get update && apt-get upgrade -y && apt-get install -y \
  curl \
  sudo \
  gnupg2 \
  lsb-release

# FRR SOURCES
RUN curl -s https://deb.frrouting.org/frr/keys.gpg | sudo tee /usr/share/keyrings/frrouting.gpg > /dev/null
ENV FRRVER="frr-stable"
RUN echo deb '[signed-by=/usr/share/keyrings/frrouting.gpg]' https://deb.frrouting.org/frr $(lsb_release -s -c) $FRRVER | sudo tee -a /etc/apt/sources.list.d/frr.list

RUN apt-get update && apt-get upgrade -y && apt-get install -y \
    nftables \
    conntrack \
    apt-utils \
    openssh-server \
    vim \
    dnsutils \
    whois \
    mtr-tiny \
    wget \
    python3-pip \
    oping \
    zsh \
    git \
    iputils-ping \
    tcpdump \
    net-tools \
    kitty \
    kitty-terminfo \
    traceroute \
    iproute2 \
    bridge-utils \
    ifupdown \
    ifupdown-extra \
    lldpd \
    atop \
    htop \
    nmap \
    iperf3 \
    frr \
    frr-pythontools \
    frr-rpki-rtrlib \
 && rm -rf /var/lib/apt/lists/*
 
# PERMIT CONNTRACK TO USERs
RUN setcap cap_net_admin=eip /usr/sbin/conntrack

# ADD SERVICE USER TO THE GROUPS OF INTEREST
RUN usermod -aG frr,frrvty $USER_NAME

RUN sed -i "s/bgpd=no/bgpd=yes/g" /etc/frr/daemons
RUN sed -i "s/ospfd=no/ospfd=yes/g" /etc/frr/daemons
RUN sed -i "s/ospf6d=no/ospf6d=yes/g" /etc/frr/daemons
RUN sed -i "s/isisd=no/isisd=yes/g" /etc/frr/daemons
RUN sed -i "s/bfdd=no/bfdd=yes/g" /etc/frr/daemons

# COPY SCRIPTS
COPY script/create_vrf.sh /etc/frr/create_vrf.sh 
COPY script/init.sh /etc/frr/init.sh
COPY script/create_dummy_interface.sh /etc/frr/create_dummy_interface.sh

COPY c-sma/PE-3/c-sma.sh /etc/frr/c-sma/PE-3/c-sma.sh
COPY c-sma/PE-3/rest_client.py /etc/frr/c-sma/PE-3/rest_client.py
COPY c-sma/PE-3/config_cloud_dc.yaml /etc/frr/c-sma/PE-3/config_cloud_dc.yaml
COPY c-sma/PE-3/config_far_dc.yaml /etc/frr/c-sma/PE-3/config_far_dc.yaml
COPY c-sma/PE-3/config_near_dc.yaml /etc/frr/c-sma/PE-3/config_near_dc.yaml

COPY c-sma/PE-5/c-sma.sh /etc/frr/c-sma/PE-5/c-sma.sh
COPY c-sma/PE-5/rest_client.py /etc/frr/c-sma/PE-5/rest_client.py
COPY c-sma/PE-5/config_cloud_dc.yaml /etc/frr/c-sma/PE-5/config_cloud_dc.yaml
COPY c-sma/PE-5/config_far_dc.yaml /etc/frr/c-sma/PE-5/config_far_dc.yaml
COPY c-sma/PE-5/config_near_dc.yaml /etc/frr/c-sma/PE-5/config_near_dc.yaml

# PERMISSIONS
RUN chmod a+x /etc/frr/*.sh
RUN chmod a+x /etc/frr/c-sma/PE-3/*.sh
RUN chmod a+x /etc/frr/c-sma/PE-5/*.sh

RUN pip3 install flask --break-system-packages
RUN pip3 install pandas --break-system-packages
RUN pip3 install kubernetes --break-system-packages
