# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Linksys.SPS2xx.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error


class Script(BaseScript):
    name = "Linksys.SPS2xx.get_capabilities"

    @false_on_cli_error
    def has_stp_cli(self):
        """
        Check box has STP enabled
        """
        cmd = self.cli("show spanning-tree active")
        return "  enabled  " in cmd
