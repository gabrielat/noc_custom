# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Cisco.SMB.remove_vlan
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iremovevlan import IRemoveVlan


class Script(BaseScript):
    name = "Cisco.SMB.remove_vlan"
    interface = IRemoveVlan

    def execute_cli(self, vlan_id):
        if not self.scripts.has_vlan(vlan_id=vlan_id):
            return False
        with self.configure():
            self.cli("no vlan %d" % vlan_id)
        self.save_config()
        return True
