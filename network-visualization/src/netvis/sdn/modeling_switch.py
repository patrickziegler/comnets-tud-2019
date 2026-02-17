from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import set_ev_cls, CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.lib.packet import packet, ethernet, ether_types
from ryu.ofproto import ofproto_v1_3
from ryu.topology import event
from ryu.topology.api import get_switch, get_link
import networkx as nx


class ModelingSwitch(app_manager.RyuApp):

    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.network_model = nx.Graph()

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath

        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser

        match = ofp_parser.OFPMatch()
        actions = [ofp_parser.OFPActionOutput(ofp.OFPP_CONTROLLER)]

        self.add_flow(datapath, 0, match, actions)

    @set_ev_cls(event.EventSwitchEnter)
    def get_topology_data(self, ev):
        self.network_model = nx.Graph()

        for switch in get_switch(self):
            self.network_model.add_node(switch.dp.id)

        for link in get_link(self):
            self.network_model.add_edge(
                link.src.dpid,
                link.dst.dpid,
                src_port=link.src.port_no,
                dst_port=link.dst.port_no,
                cost=10,
            )

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.debug("packet truncated: only %s of %s bytes", ev.msg.msg_len, ev.msg.total_len)

        msg = ev.msg

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            return

        dst = eth.dst
        src = eth.src

        in_port = msg.match["in_port"]

        datapath = msg.datapath
        datapath_id = datapath.id

        self.logger.debug("packet in %s %s %s %s", datapath_id, src, dst, in_port)

        self.mac_to_port.setdefault(datapath_id, {})
        self.mac_to_port[datapath_id][src] = in_port

        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser

        if dst in self.mac_to_port[datapath_id]:
            out_port = self.mac_to_port[datapath_id][dst]
        else:
            out_port = ofp.OFPP_FLOOD

        actions = [ofp_parser.OFPActionOutput(out_port)]

        if out_port != ofp.OFPP_FLOOD:
            match = ofp_parser.OFPMatch(in_port=in_port, eth_src=src, eth_dst=dst)
            if msg.buffer_id == ofp.OFP_NO_BUFFER:
                self.add_flow(datapath, 1, match, actions)
            else:
                self.add_flow(datapath, 1, match, actions, msg.buffer_id)
                return

        out = ofp_parser.OFPPacketOut(
            datapath=datapath,
            buffer_id=msg.buffer_id,
            in_port=in_port,
            actions=actions,
            data=msg.data if msg.buffer_id == ofp.OFP_NO_BUFFER else None
        )

        datapath.send_msg(out)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser

        if not buffer_id:
            buffer_id = ofp.OFP_NO_BUFFER

        instructions = [ofp_parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]

        mod = ofp_parser.OFPFlowMod(
            datapath=datapath,
            buffer_id=buffer_id,
            priority=priority,
            match=match,
            instructions=instructions,
        )

        datapath.send_msg(mod)


if __name__ == '__main__':
    import os, sys
    from ryu.cmd import manager

    # sys.argv.append("--verbose")
    sys.argv.append("--observe-links")
    sys.argv.append(os.path.realpath(__file__))

    manager.main()
