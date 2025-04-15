#!/bin/bash

# ENABLE IP FORWARDING
echo "Enabling IP forwarding..."

if grep -q "^#net.ipv6.conf.all.forwarding=1" /etc/sysctl.conf; then
    sed -i "s/#net.ipv6.conf.all.forwarding=1/net.ipv6.conf.all.forwarding=1/g" /etc/sysctl.conf
elif ! grep -q "^net.ipv6.conf.all.forwarding=1" /etc/sysctl.conf; then
    echo "net.ipv6.conf.all.forwarding=1" >> /etc/sysctl.conf
fi

if grep -q "^#net.ipv4.ip_forward=1" /etc/sysctl.conf; then
    sed -i "s/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/g" /etc/sysctl.conf
elif ! grep -q "^net.ipv4.ip_forward=1" /etc/sysctl.conf; then
    echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
fi

# tcp_l3mdev_accept e udp_l3mdev_accept
if ! grep -q "^net.ipv4.tcp_l3mdev_accept=1" /etc/sysctl.conf; then
    echo "net.ipv4.tcp_l3mdev_accept=1" >> /etc/sysctl.conf
fi

if ! grep -q "^net.ipv4.udp_l3mdev_accept=1" /etc/sysctl.conf; then
    echo "net.ipv4.udp_l3mdev_accept=1" >> /etc/sysctl.conf
fi

sysctl -p

echo "IPv6 forwarding has been enabled."


# START FRR
echo "Starting FRRouting..."

service frr start

echo "FRRouting has been started."
