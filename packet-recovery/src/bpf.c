static int rawsocket_arp(struct interface *interface)
{
	struct sockaddr_ll sll;
	int sock;
	/* tcpdump -dd 'arp' */
	struct sock_filter BPF_code[] = {
		{ 0x28, 0, 0, 0x0000000c },
		{ 0x15, 0, 1, 0x00000806 },
		{ 0x6, 0, 0, 0x0000ffff },
		{ 0x6, 0, 0, 0x00000000 },
	};
	struct sock_fprog filter;

	sock = socket(PF_PACKET, SOCK_RAW, htons(ETH_P_ARP));

	if (sock < 0) {
		printf("socket() failed\n");
		return -1;
	}

	strncpy(interface->ifr.ifr_name, interface->dev, IFNAMSIZ);
	if (ioctl(sock, SIOCGIFINDEX, &interface->ifr) == -1) {
		printf("ioctl() failed\n");
		return -1;
	}

	memset(&sll, 0, sizeof(sll));
	sll.sll_family = AF_PACKET;
	sll.sll_ifindex = interface->ifr.ifr_ifindex;
	/* unfortunately, ETH_P_ARP does not work on bridge port interfaces
	 * - use a BPF filter instead (see below) */
	sll.sll_protocol = htons(ETH_P_ALL);
	sll.sll_pkttype = PACKET_HOST;

	if (bind(sock, (struct sockaddr *)&sll, sizeof(sll)) == -1) {
		printf("bind() failed: %s\n", strerror(errno));
		return -1;
	}

	/* get the MAC address of the bridge or the dev */
	strncpy(interface->ifr.ifr_name, interface->addrdev, IFNAMSIZ);
	if (ioctl(sock, SIOCGIFHWADDR, &interface->ifr) < 0) {
		printf("ioctl() failed: %s\n", strerror(errno));
		return -1;
	}

	filter.len = sizeof(BPF_code)/sizeof(struct sock_filter);
	filter.filter = BPF_code;

	if (setsockopt(sock, SOL_SOCKET, SO_ATTACH_FILTER, &filter,
		       sizeof(filter))) {
		printf("Can't attach filter\n");
		return -1;
	}

	return sock;
}



