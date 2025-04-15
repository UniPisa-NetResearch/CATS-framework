#!/bin/bash

# add static route to reach kubernetes metric service
/sbin/ip -6 route add d:ffff:1:11::1 via d:0:1:31::1 dev eth0
/sbin/ip -6 route add d:ffff:2:12::2 via d:0:2:31::1 dev eth1
/sbin/ip -6 route add d:ffff:3:13::3 via d:0:3:31::1 dev eth2

# start metric agents
python3 /etc/frr/c-sma/PE-3/rest_client.py /etc/frr/c-sma/PE-3/config_near_dc.yaml > /etc/frr/c-sma/PE-3/near_dc.log 2>&1 &
sleep 1
python3 /etc/frr/c-sma/PE-3/rest_client.py /etc/frr/c-sma/PE-3/config_far_dc.yaml > /etc/frr/c-sma/PE-3/far_dc.log 2>&1 &
sleep 1
python3 /etc/frr/c-sma/PE-3/rest_client.py /etc/frr/c-sma/PE-3/config_cloud_dc.yaml > /etc/frr/c-sma/PE-3/cloud_dc.log 2>&1 &
