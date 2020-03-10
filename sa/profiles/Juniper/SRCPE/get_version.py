# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Juniper.SRCPE.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion

rx_ver = re.compile(
    r"Product Name\s+(?P<platform>\S+).+Software version\[(?P<version>[^\]]+)\]",
    re.MULTILINE | re.DOTALL,
)


class Script(BaseScript):
    name = "Juniper.SRCPE.get_version"
    cache = True
    interface = IGetVersion

    def execute(self):
        v = self.cli("show version information")
        match = rx_ver.search(v)
        return {
            "vendor": "Juniper",
            "platform": match.group("platform"),
            "version": match.group("version"),
        }
