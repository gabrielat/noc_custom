# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DLink.DxS.get_local_users
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlocalusers import IGetLocalUsers


class Script(BaseScript):
    name = "DLink.DxS.get_local_users"
    interface = IGetLocalUsers
    rx_line = re.compile(
        r"^\s*(?P<username>\S+)\s+(?P<privilege>Admin|Operator|User|Power_User)\s*$", re.MULTILINE
    )

    def execute(self):
        r = []
        for match in self.rx_line.finditer(self.cli("show account")):
            r += [
                {
                    "username": match.group("username"),
                    "class": {
                        "Admin": "superuser",
                        "Operator": "operator",
                        "User": "operator",
                        "Power_User": "operator",
                    }[match.group("privilege")],
                    "is_active": True,
                }
            ]
        return r
