#!/bin/sh

set -x

controller=tcp:127.0.0.1:6633

echo Create namespaces and switches
for i in `seq 3`; do
    for j in `seq 3`; do
        for k in `seq 3`; do
            host=h$i$j$k
            switch=s$i$j$k
            ip netns add $host
            ovs-vsctl add-br $switch
            ovs-vsctl set-fail-mode $switch secure
            ovs-vsctl set-controller $switch $controller
            ip link add ${host}-$switch type veth peer name ${switch}-$host
            ip link set ${host}-$switch netns $host
            ovs-vsctl add-port $switch ${switch}-$host
            ip netns exec $host ip addr add dev ${host}-$switch 10.$i.$j.$k/8
            ip netns exec $host ip link set ${host}-$switch up
            ip link set ${switch}-$host up

            ip link set $switch up
        done
    done
done

for i in `seq 3`; do
    for j in `seq 3`; do
        for k in `seq 2`; do
            kn=`expr $k + 1`

            # left-right
            here=s$i$j$k
            there=s$i$j$kn
            ip link add ${here}-$there type veth peer name ${there}-$here
            ovs-vsctl add-port $here ${here}-$there
            ovs-vsctl add-port $there ${there}-$here
            ip link set ${here}-$there up
            ip link set ${there}-$here up

            # front-back
            here=s$i$k$j
            there=s$i$kn$j
            ip link add ${here}-$there type veth peer name ${there}-$here
            ovs-vsctl add-port $here ${here}-$there
            ovs-vsctl add-port $there ${there}-$here
            ip link set ${here}-$there up
            ip link set ${there}-$here up

            # up-down
            here=s$k$i$j
            there=s$kn$i$j
            ip link add ${here}-$there type veth peer name ${there}-$here
            ovs-vsctl add-port $here ${here}-$there
            ovs-vsctl add-port $there ${there}-$here
            ip link set ${here}-$there up
            ip link set ${there}-$here up
        done
    done
done
