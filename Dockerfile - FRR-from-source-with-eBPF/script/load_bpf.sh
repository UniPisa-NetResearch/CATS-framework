#!/bin/bash

# Compilo il programma eBPF
clang -O2 -target bpf -c /etc/frr/marker.c -o /etc/frr/marker.o
if [ $? -ne 0 ]; then
    echo "Errore durante la compilazione di /etc/frr/marker.c"
    exit 1
fi

# Carico il programma eBPF e lo attacco all'interfaccia eth0
/sbin/tc qdisc add dev eth0 clsact
if [ $? -ne 0 ]; then
    echo "Errore durante l'aggiunta della qdisc clsact su eth0"
    exit 1
fi

/sbin/tc filter add dev eth0 ingress bpf da obj /etc/frr/marker.o sec tc
if [ $? -ne 0 ]; then
    echo "Errore durante l'aggiunta del filtro BPF su eth0"
    exit 1
fi

# Aggiunge regole di routing IPv6 con fwmark
/sbin/ip -6 rule add fwmark 100 table 1
if [ $? -ne 0 ]; then
    echo "Errore durante l'aggiunta della regola IPv6 con fwmark 100"
    exit 1
fi

/sbin/ip -6 rule add fwmark 200 table 2
if [ $? -ne 0 ]; then
    echo "Errore durante l'aggiunta della regola IPv6 con fwmark 200"
    exit 1
fi

/sbin/ip -6 rule add fwmark 300 table 3
if [ $? -ne 0 ]; then
    echo "Errore durante l'aggiunta della regola IPv6 con fwmark 300"
    exit 1
fi

echo "eBPF program loaded successfully"
