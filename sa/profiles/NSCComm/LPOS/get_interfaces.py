# - coding: utf-8 -*-
# ---------------------------------------------------------------------
# NSCComm.LPOS.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4
import re


class Script(BaseScript):
    name = "NSCComm.LPOS.get_interfaces"
    interface = IGetInterfaces

    rx_ip = re.compile(
        r"^\s+Physical Address.+: (?P<mac>\S+)\s*\n"
        r"^\s+IP Address.+: (?P<ip_address>\S+)\s*\n"
        r"^\s+Subnet Mask.+: (?P<ip_subnet>\S+)\s*\n"
        r"^\s+Default Gateway.+: \S+\s*\n"
        r"^\s+VLAN ID,PRI.+: (?P<vlan_id>\d+),\d+\s*\n",
        re.MULTILINE,
    )
    rx_eth = re.compile(r"^\s+(?P<name>\d+)", re.MULTILINE)
    rx_vlan = re.compile(
        r"^vlan id (?P<vlan_id>\d+).*\n"
        r"^name\s*: (?P<vlan_name>.+)\s*\n"
        r"^member of ports\s*: (?P<ports>.+)\s*",
        re.MULTILINE,
    )
    rx_vlan2 = re.compile(
        r"^vlan id (?P<vlan_id>\d+).*\n"
        r"^name\s*: (?P<vlan_name>.+)\s*\n"
        r"^untagged on ports:\s+(?P<uport>.+)\s*"
        r"^tagged on ports\s*:\s+(?P<tports>.+)\s*",
        re.MULTILINE,
    )

    def execute(self):
        interfaces = []
        v = self.cli("ethstat")
        for match in self.rx_eth.finditer(v):
            iface = {
                "name": match.group("name"),
                "type": "physical",
                "enabled_protocols": [],
                "subinterfaces": [
                    {"name": match.group("name"), "enabled_afi": ["BRIDGE"], "tagged_vlans": []}
                ],
            }
            interfaces += [iface]
        for v in self.scripts.get_vlans():
            vlan_id = v["vlan_id"]
            c = self.cli("vlan %s -s" % vlan_id)
            match = self.rx_vlan.search(c)
            if match:
                for port in match.group("ports").split(","):
                    for i in interfaces:
                        if port == i["name"]:
                            i["subinterfaces"][0]["tagged_vlans"] += [vlan_id]
                            break
            else:
                match = self.rx_vlan2.search(c)
                for uport in match.group("uport").split(","):
                    for i in interfaces:
                        if uport and uport == i["name"]:
                            i["subinterfaces"][0]["untagged_vlan"] = vlan_id
                for tports in match.group("tports").split(","):
                    for i in interfaces:
                        if tports == i["name"]:
                            i["subinterfaces"][0]["tagged_vlans"] += [vlan_id]
                            break
        v = self.cli("ipconfig")
        match = self.rx_ip.search(v)
        ip_address = match.group("ip_address")
        ip_subnet = match.group("ip_subnet")
        ip_address = "%s/%s" % (ip_address, IPv4.netmask_to_len(ip_subnet))
        iface = {
            "name": "MGMT",
            "type": "SVI",
            "admin_status": True,
            "oper_status": True,
            "mac": match.group("mac"),
            "enabled_protocols": [],
            "subinterfaces": [
                {
                    "name": "MGMT",
                    "admin_status": True,
                    "oper_status": True,
                    "mac": match.group("mac"),
                    "enabled_afi": ["IPv4"],
                    "ipv4_addresses": [ip_address],
                    "vlan_ids": [int(match.group("vlan_id"))],
                }
            ],
        }
        interfaces += [iface]
        return [{"interfaces": interfaces}]
