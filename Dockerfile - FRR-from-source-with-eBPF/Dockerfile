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

# UPDATE THE BASE AND INSTALL REQUIRED PACKAGES (ALSO eBPF)
RUN apt-get update && apt-get upgrade -y && apt-get install -y \
    git autoconf automake libtool make \
    libprotobuf-c-dev protobuf-c-compiler build-essential \
    python3-dev python3-pytest python3-sphinx libjson-c-dev \
    libelf-dev libreadline-dev cmake libcap-dev bison flex \
    pkg-config texinfo gdb libgrpc-dev python3-grpc-tools \
    libpcre2-dev iproute2 linux-perf tcpdump bpftool \
    clang llvm gcc linux-headers-generic bpfcc-tools libpcap-dev libc6-dev-i386

# INSTALL libbpf (SOURCE INSTALL)
RUN apt-get update && apt-get upgrade -y
RUN git clone https://github.com/libbpf/libbpf.git \
    && cd libbpf/src \
    && make \
    && make install

# UPDATE THE BASE AND INSTALL SOME BINARY libyang PACKAGES (SOURCE INSTALL)
RUN apt-get update && apt-get upgrade -y
RUN git clone https://github.com/CESNET/libyang.git \
    && cd libyang \
    && git checkout v2.1.128 \
    && mkdir build; cd build \
    && cmake --install-prefix /usr -D CMAKE_BUILD_TYPE:String="Release" .. \
    && make \
    && make install 

# ADD FRR GROUPS AND USER
RUN addgroup --system --gid 92 frr
RUN addgroup --system --gid 85 frrvty
RUN adduser --system --ingroup frr --home /var/opt/frr/ --gecos "FRR suite" --shell /bin/false frr
RUN usermod -a -G frrvty frr

# DOWNLOAD SOURCE, CONFIGURE AND COMPILE IT
RUN git clone https://github.com/frrouting/frr.git frr 
COPY script/zebra_nhg.c /frr/zebra/zebra_nhg.c
RUN cd frr \
    && ./bootstrap.sh \
    && ./configure \
       --sysconfdir=/etc \
       --localstatedir=/var \
       --sbindir=/usr/lib/frr \
       --enable-multipath=64 \
       --enable-user=frr \
       --enable-group=frr \
       --enable-vty-group=frrvty \
       --enable-configfile-mask=0640 \
       --enable-logfile-mask=0640 \
       --enable-fpm \
       --with-pkg-git-version \
    && make \
    && make check \
    && make install \
    # CREATE EMPTY FRR CONFIGURATION FILES
    && mkdir -p /etc/frr \
    && install -m 640 -o frr -g frr /dev/null /etc/frr/frr.conf \
    && install -m 640 -o frr -g frr tools/etc/frr/daemons /etc/frr/daemons \
    && install -m 775 -o frr -g frr -d /var/log/frr \
    && install -m 640 -o frr -g frrvty tools/etc/frr/vtysh.conf /etc/frr/vtysh.conf \
    # COPY FRR.SERVICE FILE 
    && cp tools/frr.service /etc/systemd/system/ 

# SHARED LIBRARY ERROR
RUN echo include /usr/local/lib >> /etc/ld.so.conf
RUN ldconfig

# ENABLE PROTOCOLS DAEMONS
RUN sed -i "s/bgpd=no/bgpd=yes/g" /etc/frr/daemons
RUN sed -i "s/ospfd=no/ospfd=yes/g" /etc/frr/daemons
RUN sed -i "s/ospf6d=no/ospf6d=yes/g" /etc/frr/daemons
RUN sed -i "s/isisd=no/isisd=yes/g" /etc/frr/daemons
RUN sed -i "s/bfdd=no/bfdd=yes/g" /etc/frr/daemons

# COPY SCRIPTS
COPY script/create_vrf_client.sh /etc/frr/create_vrf_client.sh
COPY script/create_vrf_dc.sh /etc/frr/create_vrf_dc.sh
COPY script/init.sh /etc/frr/init.sh
COPY script/create_dummy_interface.sh /etc/frr/create_dummy_interface.sh
COPY script/marker.c /etc/frr/marker.c
COPY script/load_bpf.sh /etc/frr/load_bpf.sh

# PERMISSIONS
RUN chmod a+x /etc/frr/*.sh

# CREATE LOG FILE
RUN touch /etc/frr/frr.log

# PERMISSIONS
RUN chmod a+w /etc/frr/frr.log
