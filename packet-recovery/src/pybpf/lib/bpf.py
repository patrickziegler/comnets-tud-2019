import ctypes, ast
from socket import SOL_SOCKET

ETH_P_ALL = 0x0003 # as defined in if_ether.h
SO_ATTACH_FILTER = 26 # as defined in socket.h

class __sock_filter__(ctypes.Structure):
    _fields_ = [
        ('code', ctypes.c_uint16),
        ('jt', ctypes.c_uint8),
        ('jf', ctypes.c_uint8),
        ('k', ctypes.c_uint32),
    ]

class __sock_fprog__(ctypes.Structure):
    _fields_ = [
        ('len', ctypes.c_int),
        ('filter', ctypes.c_void_p),
    ]

def sock_attach_bpf(sock, bpf_opcode):
    """Attach Berkley Packet Filter to socket

    Example:
    > from socket import socket, AF_PACKET, SOCK_RAW, ntohs
    > from lib.bpf import ETH_P_ALL, sock_attach_bpf
    > # tcpdump -dd arp
    > bpf_opcode = '''[
    >     { 0x28, 0, 0, 0x0000000c },
    >     { 0x15, 0, 1, 0x00000806 },
    >     { 0x6, 0, 0, 0x00040000 },
    >     { 0x6, 0, 0, 0x00000000 },
    > ]'''
    > sock = socket(AF_PACKET, SOCK_RAW, ntohs(ETH_P_ALL))
    > sock_attach_bpf(sock, bpf_opcode) % this function

    Implementation as described in:
    [1] https://www.kernel.org/doc/Documentation/networking/filter.txt
    [2] http://pythonsweetness.tumblr.com/post/125005930662/
        fun-with-bpf-or-shutting-down-a-tcp-listening
    """
    bpf_opcode = bpf_opcode.replace("\n"," ")
    bpf_opcode = bpf_opcode.replace("{","[")
    bpf_opcode = bpf_opcode.replace("}","]")
    bpf_opcode = ast.literal_eval(bpf_opcode)

    bpf_instns = (__sock_filter__ * len(bpf_opcode))()
    for i, (code, jt, jf, k) in enumerate(bpf_opcode):
        bpf_instns[i].code = code
        bpf_instns[i].jt = jt
        bpf_instns[i].jf = jf
        bpf_instns[i].k = k

    bpf_prog = __sock_fprog__()
    bpf_prog.len = len(bpf_opcode)
    bpf_prog.filter = ctypes.addressof(bpf_instns)

    sock.setsockopt(SOL_SOCKET, SO_ATTACH_FILTER, buffer(bpf_prog))

