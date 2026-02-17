#!/bin/bash

set -x

ip netns delete ns0
ip netns delete ns1
ip link delete B0
ip link delete B1
ip link delete br0

echo "Cleanup complete"
#exit
# ----------------------------------------------------

ip netns add ns0
ip netns add ns1

ip link add A1 type veth peer name B1
ip link add A0 type veth peer name B0

ip link set A0 netns ns0
ip link set A1 netns ns1

ip netns exec ns0 ip addr add 192.168.1.1/16 dev A0
ip netns exec ns1 ip addr add 192.168.1.2/16 dev A1

ip netns exec ns0 ip link set A0 up
ip netns exec ns1 ip link set A1 up

ip netns exec ns0 ip route add default via 192.168.0.1
ip netns exec ns1 ip route add default via 192.168.0.1

#ip addr add 192.168.1.3/16 dev B0
#ip addr add 192.168.1.4/16 dev B1

ip link set B0 up
ip link set B1 up

brctl addbr br0
brctl addif br0 B0
brctl addif br0 B1

ip addr add 192.168.0.1/16 dev br0
ip link set br0 up

echo 1 > /proc/sys/net/ipv4/ip_forward
iptables -P FORWARD DROP
iptables -F FORWARD
iptables -t nat -F
iptables -t nat -A POSTROUTING -s 192.168.0.0/16 -o wlp7s0 -j MASQUERADE
iptables -A FORWARD -i wlp7s0 -o br0 -j ACCEPT
iptables -A FORWARD -o wlp7s0 -i br0 -j ACCEPT
