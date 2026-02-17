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

from comnetsemu.net import Containernet
from mininet.node import OVSBridge
from mininet.cli import CLI


if __name__ == "__main__":
    net = Containernet(controller=None)

    print("Adding hosts...")

    h1 = net.addDockerHost("h1", ip="10.0.0.101/8", dimage="alpine", dcmd="/bin/sh")
    h2 = net.addDockerHost("h2", ip="10.0.0.102/8", dimage="alpine", dcmd="/bin/sh")
    h3 = net.addDockerHost("h3", ip="10.0.0.103/8", dimage="alpine", dcmd="/bin/sh")

    print("Adding switch...")

    s1 = net.addSwitch("s1", cls=OVSBridge)

    print("Adding links...")

    net.addLink(h1, s1)
    net.addLink(h2, s1)
    net.addLink(h3, s1)

    print("Starting emulation...")

    net.start()

    CLI(net)

    net.stop()
