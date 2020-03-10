# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.MES5448.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory
from noc.core.text import parse_table


class Script(BaseScript):
    name = "Eltex.MES5448.get_inventory"
    interface = IGetInventory

    def execute_cli(self, **kwargs):
        v = self.scripts.get_version()
        res = [
            {
                "type": "CHASSIS",
                "vendor": "ELTEX",
                "part_no": v["platform"],
                "serial": v["attributes"]["Serial Number"],
            }
        ]

        try:
            v = self.cli("show fiber-ports optical-transceiver-info all")
            for i in parse_table(v):
                r = {
                    "type": "XCVR",
                    "number": i[0].split("/")[-1],
                    "vendor": i[2],
                    "serial": i[5],
                    "part_no": i[6],
                }
                if i[2] == "OEM":
                    if i[9] == "1000LX":
                        r["part_no"] = "NoName | Transceiver | 1G | SFP LX"
                    elif i[9] == "10GBase-LR":
                        r["part_no"] = "NoName | Transceiver | 10G | SFP+ LR"
                    else:
                        raise self.NotSupportedError()
                if i[8]:
                    r["revision"] = i[8]
                res += [r]
        except self.CLISyntaxError:
            pass

        return res
