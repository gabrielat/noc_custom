# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ZTE.ZXDSL531.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
from noc.core.text import strip_html_tags

rx_html_ver = re.compile(r"Firmware Version\s+\S+\s+(?P<version>\S+)")


class Script(BaseScript):
    name = "ZTE.ZXDSL531.get_version"
    cache = True
    interface = IGetVersion

    def execute(self):
        if self.access_profile.scheme == self.TELNET:
            v = self.cli("swversion show")
            platform, version = v.split()
        elif self.access_profile.scheme == self.HTTP:
            v = self.http.get("/info.html")
            v = strip_html_tags(v)
            match = rx_html_ver.search(v)
            version = match.group("version")
        else:
            raise Exception("Unsupported access scheme")
        return {"vendor": "ZTE", "platform": "ZXDSL531", "version": version}
