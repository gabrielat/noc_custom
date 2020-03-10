# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Cisco.WLC.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error, false_on_snmp_error
from noc.core.mib import mib


class Script(BaseScript):
    name = "Cisco.WLC.get_capabilities"

    @false_on_snmp_error
    def has_cdp_snmp(self):
        """
        Check box has cdp enabled
        """
        # ciscoCdpMIB::cdpGlobalRun
        r = self.snmp.get(mib["CISCO-CDP-MIB::cdpGlobalRun", "0"])
        return r == 1

    @false_on_cli_error
    def has_cdp_cli(self):
        """
        Check box has cdp enabled
        """
        r = self.cli("show cdp neighbors")
        return "% CDP is not enabled" not in r

    def execute_platform_snmp(self, caps):
        if self.match_version(platform__regex="^AIR-CT"):
            caps["CPE | Controller"] = True

    def execute_platform_cli(self, caps):
        if self.match_version(platform__regex="^AIR-CT5"):
            caps["CPE | Controller"] = True
