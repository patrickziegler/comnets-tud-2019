#!/bin/sh

set -x

echo Create namespaces and switches
for i in `seq 3`; do
    for j in `seq 3`; do
        for k in `seq 3`; do
            host=h$i$j$k
            switch=s$i$j$k
            ip netns del $host
            ovs-vsctl del-br $switch
            ip link delete ${switch}-$host
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
            ip link delete ${here}-$there

            # front-back
            here=s$i$k$j
            there=s$i$kn$j
            ip link delete ${here}-$there

            # up-down
            here=s$k$i$j
            there=s$kn$i$j
            ip link delete ${here}-$there
        done
    done
done
