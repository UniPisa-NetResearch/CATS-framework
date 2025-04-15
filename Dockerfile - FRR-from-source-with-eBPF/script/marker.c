#include <linux/bpf.h>
#include <linux/pkt_cls.h>
#include <linux/if_ether.h>
#include <linux/ipv6.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_endian.h>

SEC("tc")
int mark_packet(struct __sk_buff *skb) {
    struct ethhdr eth;
    struct ipv6hdr ip6h;

    // Carica l'header Ethernet
    bpf_skb_load_bytes(skb, 0, &eth, sizeof(eth));

    // Verifica che il pacchetto sia IPv6
    if (eth.h_proto != __constant_htons(ETH_P_IPV6))
        return TC_ACT_OK;

    // Carica l'header IPv6
    bpf_skb_load_bytes(skb, sizeof(eth), &ip6h, sizeof(ip6h));

    __u32 traffic_class = (ip6h.priority << 4) | (ip6h.flow_lbl[0] >> 4);

    if (traffic_class == 0x10) { 
        skb->mark = 100; // VRF 1 (near-edge)
    } else if (traffic_class == 0x20) { 
        skb->mark = 200; // VRF 2 (far-edge)
    } else if (traffic_class == 0x30) { 
        skb->mark = 300; // VRF 3 (cloud)
    } else {
        return TC_ACT_OK; // Nessuna azione per altri pacchetti
    }
    
    return TC_ACT_OK; // Continua con il processing
}

char _license[] SEC("license") = "GPL";
