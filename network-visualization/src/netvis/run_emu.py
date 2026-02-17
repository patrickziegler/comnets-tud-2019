# Copyright (C) 2019 Patrick Ziegler
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


# from comnetsemu.net import Containernet
from mininet.cli import CLI
from mininet.net import Mininet
from mininet.node import RemoteController, OVSBridge, OVSSwitch
from mininet.topo import Topo, LinearTopo


class CubicTopo(Topo):

    def build(self, u=3, v=3, w=3):
        switches = dict()

        for i in range(u):
            for j in range(v):
                for k in range(w):
                    x, y, z = i + 1, j + 1, k + 1
                    key = "%i%i%i" % (x, y, z)

                    host = self.addHost(
                        name="h" + key,
                        ip="10.%i.%i.%i/8" % (x, y, z)
                    )

                    switches[key] = self.addSwitch(
                        name="s" + key
                    )

                    self.addLink(switches[key], host)

        for i in range(u):
            for j in range(v):
                for k in range(w):
                    x, y, z = i + 1, j + 1, k + 1
                    key = "%i%i%i" % (x, y, z)

                    try:
                        self.addLink(
                            switches[key],
                            switches["%i%i%i" % (x + 1, y, z)]
                        )
                    except KeyError:
                        pass

                    try:
                        self.addLink(
                            switches[key],
                            switches["%i%i%i" % (x, y + 1, z)]
                        )
                    except KeyError:
                        pass

                    try:
                        self.addLink(
                            switches[key],
                            switches["%i%i%i" % (x, y, z + 1)]
                        )
                    except KeyError:
                        pass


class CircleTopo(Topo):

    def build(self, n):
        last = None
        first = None

        for i in range(n):
            h = self.addHost("h%i" % i)
            s = self.addSwitch("s%i" % i)
            self.addLink(h, s)

            if first is None:
                first = s

            if last is not None:
                self.addLink(s, last)
            last = s

        self.addLink(first, last)


# def run_emu_cont():
#     net = Containernet(controller=None)
#
#     print("Adding hosts...")
#
#     h1 = net.addDockerHost("h1", ip="10.0.0.101/8", dimage="dev_test")
#     h2 = net.addDockerHost("h2", ip="10.0.0.102/8", dimage="dev_test")
#     h3 = net.addDockerHost("h3", ip="10.0.0.103/8", dimage="dev_test")
#
#     print("Adding switch...")
#
#     s1 = net.addSwitch("s1", cls=OVSBridge)
#
#     print("Adding links...")
#
#     net.addLink(s1, h1)
#     net.addLink(s1, h2)
#     net.addLink(s1, h3)
#
#     print("Starting emulation...")
#
#     net.start()
#
#     CLI(net)
#
#     net.stop()


def run_emu_basic():
    net = Mininet(
        topo=LinearTopo(5),
        controller=RemoteController,
        switch=OVSSwitch,
        # autoSetMacs=True
    )

    net.start()

    CLI(net)

    net.stop()


if __name__ == "__main__":
    run_emu_basic()
