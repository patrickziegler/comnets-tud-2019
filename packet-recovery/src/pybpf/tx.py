import sys, argparse, socket, time

if __name__ == "__main__":
    parser = argparse.ArgumentParser(sys.argv[0])
    parser.add_argument(dest="ip", type=str, default="127.0.0.1", help="Destination IP-Adress")
    parser.add_argument("-p", "--port", dest="port", type=int, default=5005)
    parser.add_argument("-m", "--mode", dest="mode", type=str, default="udp")
    parser.add_argument("-d", "--delay", dest="delay", type=float, default=1.0)
    args = parser.parse_args(sys.argv[1:])

    if args.mode.lower() == "tcp":
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((args.ip, args.port))

        try:
            i = 0
            while True:
                i += 1
                msg = "pkt" + str(i)
                sock.send(msg)
                print "Sent '" + msg + "' to " + args.ip
                time.sleep(args.delay)

        except (KeyboardInterrupt, SystemExit):
            sock.close()

    elif args.mode.lower() == "udp":
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            i = 0
            while True:
                i += 1
                msg = "pkt" + str(i)
                sock.sendto(msg, (args.ip, args.port))
                print "Sent '" + msg + "' to " + args.ip
                time.sleep(args.delay)

        except (KeyboardInterrupt, SystemExit):
            sock.close()

    else:
        print "Unknown mode " + args.mode

