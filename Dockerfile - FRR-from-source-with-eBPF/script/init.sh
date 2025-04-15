#!/bin/bash

# ENABLE IP FORWARDING
echo "Enabling IPv6 forwarding..."

sed -i "s/#net.ipv6.conf.all.forwarding=1/net.ipv6.conf.all.forwarding=1/g" /etc/sysctl.conf
sed -i "s/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/g" /etc/sysctl.conf 

sysctl -p

echo "IPv6 forwarding has been enabled."


# START FRR
echo "Starting FRRouting..."

/usr/lib/frr/frrinit.sh start

echo "FRRouting has been started."
