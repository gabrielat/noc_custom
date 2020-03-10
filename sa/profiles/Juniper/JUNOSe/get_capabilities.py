# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Juniper.JUNOSe.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error


class Script(BaseScript):
    name = "Juniper.JUNOSe.get_capabilities"

    @false_on_cli_error
    def has_oam_cli(self):
        """
        Check box has oam enabled
        """
        r = self.cli("show ethernet oam lfm summary")
        return bool(r)

    @false_on_cli_error
    def has_bfd_cli(self):
        """
        Check box has BFD enabled
        """
        r = self.cli("show bfd session")
        return "not found or down" not in r

    @false_on_cli_error
    def has_pptp(self):
        """
        Check box has PPTP enabled
        """
        v = self.cli("show ppp interface summary oper")
        v = v.splitlines()
        return v[2].split()[1]

    @false_on_cli_error
    def has_pppoe(self):
        """
        Check box has PPoE enabled
        """
        v = self.cli("show pppoe interface summary | include Total")
        return v.split(":")[1].strip()

    def execute_platform_cli(self, caps):
        if self.has_pptp():
            caps["BRAS | PPTP"] = True
        if self.has_pppoe():
            caps["BRAS | PPPoE"] = True
