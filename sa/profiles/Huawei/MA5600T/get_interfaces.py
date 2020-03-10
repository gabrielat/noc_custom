# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Huawei.MA5600T.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
import six

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "Huawei.MA5600T.get_interfaces"
    interface = IGetInterfaces
    TIMEOUT = 240

    rx_if1 = re.compile(
        r"^\s*(?P<ifname>[a-zA-Z]+)(?P<ifnum>\d+) current state :\s*(?P<admin_status>UP|DOWN)\s*\n"
        r"^\s*Line protocol current state :\s*(?P<oper_status>UP|UP \(spoofing\)|DOWN)\s*\n"
        r"^\s*Description :\s*(?P<descr>.*)\n"
        r"^\s*The Maximum Transmit Unit is (?P<mtu>\d+) bytes(, Hold timer is \d+\(sec\))?\s*\n"
        r"(^\s*Forward plane MTU: \S+\n)?"
        r"(^\s*Internet Address is (?P<ip>\S+)\s*\n)?"
        r"(^\s*IP Sending Frames' Format is PKTFMT_ETHNT_2, Hardware address is (?P<mac>\S+)\s*\n)?",
        re.MULTILINE,
    )
    rx_if2 = re.compile(
        r"^Description : (?P<descr>HUAWEI, SmartAX Series), (?P<ifname>[a-zA-Z]+)(?P<ifnum>\d+) Interface\s*\n"
        r"^The Maximum Transmit Unit is (?P<mtu>\d+) bytes\s*\n"
        r"(^Internet Address is (?P<ip>\S+)\s*\n)?"
        r"(^IP Sending Frames' Format is PKTFMT_ETHNT_2, Hardware address is (?P<mac>\S+)\s*\n)?"
        r"(^MEth port is (?P<ifparent>\S+)\s*\n)?",
        re.MULTILINE,
    )
    rx_vlan = re.compile(
        r"^\s*\-+\s*\n"
        r"(?P<tagged>.+)"
        r"^\s*\-+\s*\n"
        r"^\s*Total:\s+\d+\s+(Native VLAN:\s+(?P<untagged>\d+|-)\s*)?\n",
        re.MULTILINE | re.DOTALL,
    )
    rx_vlan2 = re.compile(
        r"^\s+\d+\s+eth\s+(?:down|up)\s+(?P<ifname>\d+/\s*\d+/\s*\d+)\s+"
        r"(?:(?P<vpi>\d+|-)\s+(?P<vci>\d+|-)\s+)?"
        r"vlan\s+(?P<type>\S+)\s*\n",
        re.MULTILINE,
    )
    rx_tagged = re.compile(r"(?P<tagged>\d+)", re.MULTILINE)
    rx_ether = re.compile(
        r"^\s*(?P<port>\d+)\s+(?:10)?[GF]E(?:-Optic|-Elec)?\s+"
        r"(\S+\s+)?(\d+\s+)?(\S+\s+)?\S+\s+\S+\s+\S+\s+"
        r"\S+\s+(?P<admin_status>\S+)\s+(?P<oper_status>\S+)\s*\n",
        re.MULTILINE,
    )
    rx_adsl_state = re.compile(r"^\s*(?P<port>\d+)\s+(?P<oper_state>\S+)", re.MULTILINE)
    rx_pvc = re.compile(
        r"^\s*\d+\s+p2p\s+lan\s+[0\*]/(?:\d+|\*)\s*/(?P<vlan>(?:\d+|\*))\s+\S*\s+\S+\s+\S+\s+"
        r"adl\s+0/\d+\s*/(?P<port>\d+)\s+(?P<vpi>\d+)\s+(?P<vci>\d+)\s+\d+\s+"
        r"(?P<admin_status>\S+)\s*\n",
        re.MULTILINE,
    )
    rx_sp = re.compile(
        r"^\s*\d+\s+(?P<vlan>\d+)\s+\S+\s+(:?adl|vdl||gpon)\s+0/\d+\s*/(?P<port>\d+)\s+"
        r"(?P<vpi>\d+)\s+(?P<vci>\d+)\s+\S+\s+\S+\s+(?:\d+|\-)\s+(?:\d+|\-)\s+"
        r"(?P<admin_status>up|down)\s*$",
        re.MULTILINE,
    )
    rx_stp = re.compile(
        r"^\s*\d+\s+(?P<port>0/\s*\d+/\s*\d+)\s+\d+\s+\d+\s+Enabled\s+", re.MULTILINE
    )
    rx_ports = re.compile(
        r"^\s*(?P<port>\d+)\s+(?P<type>ADSL|VDSL|GPON|10GE|GE|FE|GE-Optic|GE-Elec|FE-Elec)\s+.+?"
        r"(?P<state>[Oo]nline|[Oo]ffline|Activating|Activated|Registered)?",
        re.MULTILINE,
    )

    # SmartAX MA5600T&MA5603T Multi-Service Access Module
    # ifIndex MIB Encoding Rules
    type = {
        "other": 1,
        "ATM": 4,
        "ADSL": 6,
        "Eth": 7,
        "IMA": 39,
        "SHDSL": 44,
        "Vlan": 48,
        "IMALink": 51,
        "Trunk": 54,
        "DOCSISup": 59,
        "DOCSISdown": 60,
        "DOCSISport": 61,
        "BITS": 96,
        "TDME1": 97,
        "VDSL": 124,
        "VDSL2": 124,
        "xDSLchan": 123,
        "GPON": 125,
        "EPON": 126,
        # Dummy rule, needed in MA5626
        # IF-MIB::ifName.4261413120 = STRING: GPONNNI
        "XG-PON": 127,
    }

    def snmp_index(self, int_type, shelfID, slotID, intNum):
        """
        Huawei MA5600T&MA5603T port -> ifindex converter
        """

        type_id = self.type[int_type]
        index = type_id << 25
        index += shelfID << 19
        index += slotID << 13
        if int_type in ["Vlan"]:
            index += intNum
        elif int_type in ["xDSLchan", "DOCSISup", "DOCSISdown"]:
            index += intNum << 5
        # https://gpon.kou.li/huawei/olt/snmp
        elif int_type in ["GPON", "XG-PON"]:
            index += intNum << 8
        else:
            index += intNum << 6

        return index

    def get_stp(self):
        """
        Getting stp status on port
        :return:
        """
        try:
            v = self.cli("display stp")
        except self.CLISyntaxError:
            return []
        r = set()
        for match in self.rx_stp.finditer(v):
            port = match.group("port").replace(" ", "")
            if port not in r:
                r.add(port)
        return r

    def get_ports(self, v, slot_n=0):
        """
        Parse output like:
          -------------------------------------------------------------
            Port   Port   min-distance   max-distance   Optical-module
                   type       (km)           (km)           status
          -------------------------------------------------------------
            0     GPON        0              20             Online
            1     GPON        0              20             Online
            2     GPON        0              20             Online
            3     GPON        0              20             Online
        on old version column "Optical-module status" not exists, that state is True.
        :param v:
        :param slot_n:
        :return:
        """
        ports = {}
        for match in self.rx_ports.finditer(v):
            state = match.group("state")
            ports["0/%d/%s" % (slot_n, match.group("port"))] = {
                "num": match.group("port"),
                "state": state.lower() in {"online", "activated", "registered"} if state else True,
                "type": match.group("type"),
            }
        return ports

    def get_pvc(self, interfaces, slot_n):
        try:
            v = self.cli("display pvc 0/%d" % slot_n)
        except self.CLISyntaxError:
            return self.get_svc(interfaces, slot_n)
        for match in self.rx_pvc.finditer(v):
            port = int(match.group("port"))
            ifname = "0/%d/%d" % (slot_n, port)
            sub = {
                "name": "%s-%d.%d" % (ifname, int(match.group("vpi")), int(match.group("vci"))),
                "admin_status": match.group("admin_status") == "up",
                "enabled_afi": ["BRIDGE", "ATM"],
                "vpi": int(match.group("vpi")),
                "vci": int(match.group("vci")),
            }
            if match.group("vlan") != "*":
                sub["vlan_ids"] = int(match.group("vlan"))
            if ifname in interfaces:
                interfaces[ifname]["subinterfaces"] += [sub]

    def get_svc(self, interfaces, slot_n):
        """
        service-port board command. Use on GPON board
        :param interfaces:
        :param slot_n:
        :return:
        """
        try:
            v = self.cli("display service-port board 0/%d" % slot_n)
        except self.CLISyntaxError:
            self.logger.error("[Huawei.MA5600T] Not supported service-port board command")
            return
        if "No service virtual port can be operated" in v:
            # return self.get_pvc(interfaces, slot_n)
            return
        # @todo ES
        for match in self.rx_sp.finditer(v):
            port = int(match.group("port"))
            ifname = "0/%d/%d" % (slot_n, port)
            sub = {
                "name": "%s-%d.%d" % (ifname, int(match.group("vpi")), int(match.group("vci"))),
                "admin_status": match.group("admin_status") == "up",
                "enabled_afi": ["BRIDGE"],
                "vpi": int(match.group("vpi")),
                "vci": int(match.group("vci")),
            }
            if match.group("vlan") != "*":
                sub["vlan_ids"] = int(match.group("vlan"))
            if ifname in interfaces:
                interfaces[ifname]["subinterfaces"] += [sub]

    def get_l3_interfaces(self, interfaces):
        """
        Getting L3 interfaces by "display interface" command
        :param interfaces:
        :return:
        """
        v = self.cli("display interface")
        rx = self.find_re([self.rx_if1, self.rx_if2], v)
        for match in rx.finditer(v):
            ifname = "%s%s" % (match.group("ifname"), match.group("ifnum"))
            iftype = self.profile.get_interface_type(ifname)
            interfaces[ifname] = {"name": ifname, "type": iftype, "subinterfaces": []}
            sub = {"name": ifname, "mtu": int(match.group("mtu"))}
            if "admin_status" in match.groupdict():
                interfaces[ifname]["admin_status"] = match.group("admin_status") != "DOWN"
                sub["admin_status"] = match.group("admin_status") != "DOWN"
            if "oper_status" in match.groupdict():
                interfaces[ifname]["oper_status"] = match.group("oper_status") != "DOWN"
                sub["oper_status"] = match.group("oper_status") != "DOWN"
            if match.group("descr"):
                if match.group("descr") != "HUAWEI, SmartAX Series":
                    interfaces[ifname]["description"] = match.group("descr")
                    sub["description"] = match.group("descr")
            if match.group("ip"):
                sub["ipv4_addresses"] = [match.group("ip")]
                sub["enabled_afi"] = ["IPv4"]
            if match.group("mac"):
                interfaces[ifname]["mac"] = match.group("mac")
                sub["mac"] = match.group("mac")
            if match.group("ifname") == "vlanif":
                sub["vlan_ids"] = int(match.group("ifnum"))
            if "ifparent" in match.groupdict() and match.group("ifparent"):
                if match.group("ifparent") in interfaces:
                    interfaces[match.group("ifparent")]["subinterfaces"] += [sub]
                else:
                    self.logger.info("Not find ifparen sub")
            else:
                interfaces[ifname]["subinterfaces"] += [sub]

    def get_port_vlans(self, ifname):
        untagged, tagged = 0, []
        v = self.cli("display port vlan %s" % ifname)
        m = self.rx_vlan.search(v)
        if m:
            if m.group("untagged") and m.group("untagged") != "-":
                untagged = int(m.group("untagged"))
            for t in self.rx_tagged.finditer(m.group("tagged")):
                if int(t.group("tagged")) != untagged:
                    tagged += [int(t.group("tagged"))]
        return untagged, tagged

    def execute_cli(self, **kwargs):
        interfaces = {}
        stp_ports = self.get_stp()

        # Get portchannels
        portchannel_members = {}
        for pc in self.scripts.get_portchannel():
            i = pc["interface"]
            t = pc["type"] == "L"
            for m in pc["members"]:
                portchannel_members[m] = (i, t)
            interfaces[pc["interface"]] = {
                "name": pc["interface"],
                "type": "aggregated",
                "admin_status": True,
                "oper_status": True,
                "subinterfaces": [
                    {
                        "name": pc["interface"],
                        "admin_status": True,
                        "oper_status": True,
                        "enabled_afi": ["BRIDGE"],
                    }
                ],
            }
        # ports = self.profile.fill_ports(self)
        _, boards = self.profile.get_board(self)

        for b in boards:
            slot = int(b["num"])
            try:
                v = self.cli("display board 0/%d" % slot)
            except self.CLISyntaxError:
                self.logger.error("Unsupported display board command")
                continue
            # If getting ports
            # ports.update(self.get_ports(v, slot))
            ports = self.get_ports(v, slot)
            # Detect board_type!
            # Check board ports
            # display board 0/17
            #   --------------------------------------------------------
            #   Board Name        : H601TSSB
            #   Board Status      : Normal
            #   Online state      : -
            #   Board has ports   : 0
            #   --------------------------------------------------------
            b_type = {p["type"] for p in six.itervalues(ports)}
            b_type = b_type.pop() if b_type else b["type"]
            if b_type in {"10GE", "GE", "FE", "GE-Optic", "GE-Elec", "FE-Elec"}:
                for match in self.rx_ether.finditer(v):
                    ifname = "0/%d/%d" % (slot, int(match.group("port")))
                    admin_status = match.group("admin_status") == "active"
                    oper_status = match.group("oper_status") == "online"
                    ifindex = self.snmp_index("Eth", 0, slot, int(match.group("port")))
                    untagged, tagged = self.get_port_vlans(ifname)
                    interfaces[ifname] = {
                        "name": ifname,
                        "type": "physical",
                        "admin_status": admin_status,
                        "oper_status": oper_status,
                        "snmp_ifindex": ifindex,
                        "enabled_protocols": [],
                        "subinterfaces": [
                            {
                                "name": ifname,
                                "admin_status": admin_status,
                                "oper_status": oper_status,
                                "tagged_vlans": tagged,
                                "enabled_afi": ["BRIDGE"],
                            }
                        ],
                    }
                    if untagged:
                        interfaces[ifname]["subinterfaces"][0]["untagged_vlan"] = untagged
                    if ifname in stp_ports:
                        interfaces[ifname]["enabled_protocols"] += ["STP"]
                    if ifname in portchannel_members:
                        ai, is_lacp = portchannel_members[ifname]
                        interfaces[ifname]["aggregated_interface"] = ai
                        interfaces[ifname]["enabled_protocols"] += ["LACP"]

            if b_type in {"ADSL", "VDSL"}:
                for p_name, p in six.iteritems(ports):
                    if p["type"] == "VDSL":
                        ifindex = self.snmp_index("VDSL2", 0, slot, int(p["num"]))
                    else:
                        ifindex = self.snmp_index(p["type"], 0, slot, int(p["num"]))
                    interfaces[p_name] = {
                        "name": p_name,
                        "type": "physical",
                        "admin_status": True,
                        "oper_status": p["state"],
                        "snmp_ifindex": ifindex,
                        "enabled_protocols": [],
                        "subinterfaces": [],
                    }

                self.get_pvc(interfaces, slot)

            if b_type in {"GPON"}:  # For feature use
                for p_name, p in six.iteritems(ports):
                    if self.is_gpon_uplink:
                        ifindex = self.snmp_index("XG-PON", 0, slot, int(p["num"]))
                    else:
                        ifindex = self.snmp_index("GPON", 0, slot, int(p["num"]))
                    # ifname = "0/%d/%d" % (i, int(p["num"]))
                    interfaces[p_name] = {
                        "name": p_name,
                        "type": "physical",
                        "snmp_ifindex": ifindex,
                        "admin_status": True,
                        "oper_status": p["state"],
                        "subinterfaces": [
                            {
                                "name": p_name,
                                "admin_status": True,
                                "oper_status": p["state"],
                                "enabled_afi": ["BRIDGE"],
                            }
                        ],
                    }
                self.get_svc(interfaces, slot)
        self.get_l3_interfaces(interfaces)
        return [{"interfaces": sorted(interfaces.values(), key=lambda x: x["name"])}]