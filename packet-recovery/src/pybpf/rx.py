import sys, argparse, socket, netifaces, re

def __hexdump__(msg):
    dump = list(' '.join(re.findall("." * 2, msg.encode("hex"))))
    for i in range(47, len(dump), 48):
        dump[i] = "\n"
    return ''.join(dump)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(sys.argv[0])
    parser.add_argument(dest="iface", type=str, default="wlp7s0", help="Network interface")
    parser.add_argument("-p", "--port",  dest="port", type=int, default=5005)
    parser.add_argument("-b", "--buffer", dest="rcvbuf", type=int, default=1024)
    parser.add_argument("-t", "--timeout", dest="timeout", type=float, default=None)
    parser.add_argument("-m", "--mode", dest="mode", type=str, default="udp")
    args = parser.parse_args(sys.argv[1:])

    if args.mode.lower() == "tcp":
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if args.timeout is not None:
            sock.settimeout(args.timeout)

        ownaddr = netifaces.ifaddresses(args.iface)[netifaces.AF_INET][0]["addr"]
        sock.bind((ownaddr, args.port))
        sock.listen(1)

        print "Listening on " + ownaddr + ":" + str(args.port) + " (" + args.mode + ") ..."

        conn, addr = sock.accept()

        print "Connection established with " + addr[0] + ":" + str(addr[1])

        try:
            while True:
                try:
                    msg = conn.recv(args.rcvbuf)
                    print addr[0] + ":" + str(addr[1]) + "\t" + msg
                except socket.timeout:
                    pass

        except (KeyboardInterrupt, SystemExit):
            conn.close()
            sock.close()

    elif args.mode.lower() == "udp":
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if args.timeout is not None:
            sock.settimeout(args.timeout)

        ownaddr = netifaces.ifaddresses(args.iface)[netifaces.AF_INET][0]["addr"]
        sock.bind((ownaddr, args.port))

        print "Listening on " + ownaddr + ":" + str(args.port) + " (" + args.mode + ") ..."

        try:
            while True:
                try:
                    msg, addr = sock.recvfrom(args.rcvbuf)
                    print addr[0] + ":" + str(addr[1]) + "\t" + msg
                except socket.timeout:
                    pass

        except (KeyboardInterrupt, SystemExit):
            sock.close()

    elif args.mode.lower() == "raw":
        """Raw socket for UDP/IP,
        received packets will only contain IP frames,
        therefore neither L2 headers nor FCS are available!
        """

        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
        if args.timeout is not None:
            sock.settimeout(args.timeout)

        # ownaddr = netifaces.ifaddresses(args.iface)[netifaces.AF_INET][0]["addr"]
        # sock.bind((ownaddr, args.port))

        print "Listening on " + args.iface + " (" + args.mode + ") ..."

        try:
            while True:
                try:
                    msg, addr = sock.recvfrom(args.rcvbuf)
                    print "\nReceived at " + addr[0] + ":"
                    print __hexdump__(msg)

                except socket.timeout:
                    pass

        except (KeyboardInterrupt, SystemExit):
            sock.close()

    elif args.mode.lower() == "bpf":
        """Raw socket for all incoming traffic,
        received packets contain L2 layers and FCS (depending on driver),
        socket will be bound to interface instead of ip adress,
        filtering with BPF is applied to restrict incoming traffic
        """

        from lib.bpf import ETH_P_ALL, sock_attach_bpf

        sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(ETH_P_ALL))
        if args.timeout is not None:
            sock.settimeout(args.timeout)

        sock.bind((args.iface, ETH_P_ALL))

        # tcpdump -dd -i mon0 -y IEEE802_11_RADIO ether host 00:24:d7:b3:db:d0
        bpf_opcode = """[
            { 0x30, 0, 0, 0x00000003 },
            { 0x64, 0, 0, 0x00000008 },
            { 0x7, 0, 0, 0x00000000 },
            { 0x30, 0, 0, 0x00000002 },
            { 0x4c, 0, 0, 0x00000000 },
            { 0x2, 0, 0, 0x00000000 },
            { 0x7, 0, 0, 0x00000000 },
            { 0x50, 0, 0, 0x00000000 },
            { 0x45, 31, 0, 0x00000004 },
            { 0x45, 0, 21, 0x00000008 },
            { 0x50, 0, 0, 0x00000001 },
            { 0x45, 0, 9, 0x00000002 },
            { 0x45, 0, 4, 0x00000001 },
            { 0x40, 0, 0, 0x0000001a },
            { 0x15, 0, 12, 0xd7b3dbd0 },
            { 0x48, 0, 0, 0x00000018 },
            { 0x15, 22, 10, 0x00000024 },
            { 0x40, 0, 0, 0x00000012 },
            { 0x15, 0, 16, 0xd7b3dbd0 },
            { 0x48, 0, 0, 0x00000010 },
            { 0x15, 18, 14, 0x00000024 },
            { 0x40, 0, 0, 0x0000000c },
            { 0x15, 0, 2, 0xd7b3dbd0 },
            { 0x48, 0, 0, 0x0000000a },
            { 0x15, 14, 0, 0x00000024 },
            { 0x50, 0, 0, 0x00000001 },
            { 0x45, 0, 8, 0x00000001 },
            { 0x40, 0, 0, 0x00000012 },
            { 0x15, 0, 11, 0xd7b3dbd0 },
            { 0x48, 0, 0, 0x00000010 },
            { 0x15, 8, 9, 0x00000024 },
            { 0x40, 0, 0, 0x0000000c },
            { 0x15, 0, 2, 0xd7b3dbd0 },
            { 0x48, 0, 0, 0x0000000a },
            { 0x15, 4, 0, 0x00000024 },
            { 0x40, 0, 0, 0x00000006 },
            { 0x15, 0, 3, 0xd7b3dbd0 },
            { 0x48, 0, 0, 0x00000004 },
            { 0x15, 0, 1, 0x00000024 },
            { 0x6, 0, 0, 0x00040000 },
            { 0x6, 0, 0, 0x00000000 },
        ]"""

        sock_attach_bpf(sock, bpf_opcode)

        print "Listening on " + args.iface + " (" + args.mode + ") ..."

        try:
            while True:
                try:
                    msg, addr = sock.recvfrom(args.rcvbuf)

                    try:
                        bad_fcs = ord(msg[24]) & 64 != 0 # radiotap flags bit 6 (bad_fcs)
                    except IndexError:
                        bad_fcs = "None"

                    print "\nReceived at " + addr[0] + " (bad_fcs: " + str(bad_fcs) + "):"
                    print __hexdump__(msg)

                    # tried to compute fcs myself but failed...
                    # from binascii import crc32
                    # fcsc = crc32(msg[39:-4])
                    # if fcsc < 0:
                    #     fcsc ^= 0xFFFFFFFF
                    # print hex(fcsc)

                except socket.timeout:
                    pass

        except (KeyboardInterrupt, SystemExit):
            sock.close()

    else:
        print "Unknown mode " + args.mode

