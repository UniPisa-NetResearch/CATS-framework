#!/bin/bash
# add static route to reach kubernetes metric service
/sbin/ip -6 route add d:ffff:4:24::4 via d:0:4:52::2 dev eth0
/sbin/ip -6 route add d:ffff:6:26::6 via d:0:5:52::2 dev eth1
/sbin/ip -6 route add d:ffff:5:25::5 via d:0:6:52::2 dev eth2

# start metric agents
python3 /etc/frr/c-sma/PE-5/rest_client.py /etc/frr/c-sma/PE-5/config_near_dc.yaml > /etc/frr/c-sma/PE-5/near_dc.log 2>&1 &
sleep 1
python3 /etc/frr/c-sma/PE-5/rest_client.py /etc/frr/c-sma/PE-5/config_far_dc.yaml > /etc/frr/c-sma/PE-5/far_dc.log 2>&1 &
sleep 1
python3 /etc/frr/c-sma/PE-5/rest_client.py /etc/frr/c-sma/PE-5/config_cloud_dc.yaml > cloud_dc.log 2>&1 &
