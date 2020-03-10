# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Alstec.5440.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Alstec.5440.get_version"
    interface = IGetVersion
    cache = True

    def execute(self):
        v = self.cli("swversion", cached=True)
        return {"vendor": "Alstec", "platform": "ALS-5440", "version": v.strip()}
