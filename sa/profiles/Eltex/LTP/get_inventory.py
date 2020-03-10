# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.LTP.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "Eltex.LTP.get_inventory"
    interface = IGetInventory
    cache = True

    rx_platform = re.compile(
        r"^\s*TYPE:\s+(?P<part_no>\S+)\s*\n"
        r"^\s*HW_revision:\s+(?P<revision>\S+)\s*\n"
        r"^\s*SN:\s+(?P<serial>\S+)",
        re.MULTILINE,
    )
    rx_pwr = re.compile(r"^\s*Module (?P<num>\d+): (?P<part_no>PM\S+)", re.MULTILINE)

    def execute_snmp(self, **kwargs):
        v = self.scripts.get_version()
        r = [{"type": "CHASSIS", "vendor": "ELTEX", "part_no": v["platform"]}]
        if "attributes" in v:
            r[-1]["serial"] = v["attributes"]["Serial Number"]
            r[-1]["revision"] = v["attributes"]["HW version"]
        pwr_num = self.snmp.get("1.3.6.1.4.1.35265.1.22.1.17.1.2.1")
        pwr_pn = self.snmp.get("1.3.6.1.4.1.35265.1.22.1.17.1.3.1")
        pwr_pn = pwr_pn.split()[0]
        r += [{"type": "PWR", "vendor": "ELTEX", "part_no": pwr_pn, "number": pwr_num}]
        return r

    def execute_cli(self, **kwargs):
        try:
            v = self.cli("show system environment", cached=True)
        except self.CLISyntaxError:
            raise NotImplementedError
        match = self.rx_platform.search(v)

        r = [
            {
                "type": "CHASSIS",
                "vendor": "ELTEX",
                "part_no": match.group("part_no"),
                "serial": match.group("serial"),
                "revision": match.group("revision"),
            }
        ]

        for match in self.rx_pwr.finditer(v):
            r += [
                {
                    "type": "PWR",
                    "vendor": "ELTEX",
                    "part_no": match.group("part_no"),
                    "number": match.group("num"),
                }
            ]
        return r
