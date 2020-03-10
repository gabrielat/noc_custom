# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# HP.iLO2.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "HP.iLO2.get_config"
    interface = IGetConfig

    EXCLUDE_TARGETS = {"/map1/firmware1", "/map1/log1"}

    def walk(self, dir):
        r = self.cli("show %s" % dir).split("\n")
        if r[0] != "status=0" and r[1] != "status_tag=COMMAND COMPLETED":
            return []
        r = r[5:]

        state = None
        targets = []
        properties = []
        for line in r:
            line = line.strip()
            if line in ["Targets", "Properties", "Verbs"]:
                state = line
                continue
            if not line:
                continue
            if state == "Targets":
                targets += [line]
            elif state == "Properties":
                properties += [line]
        result = [(dir, [p.split("=", 1) for p in properties if "=" in p])]
        for t in targets:
            path = "%s/%s" % (dir, t)
            if path in self.EXCLUDE_TARGETS:
                continue
            result += self.walk(path)
        return result

    def execute_cli(self, **kwargs):
        r = []
        for dir, args in self.walk("/map1"):
            if not args:
                continue
            r += ["set %s %s" % (dir, " ".join(["%s=%s" % (k, v) for k, v in args]))]
        config = "\n".join(sorted(r))
        return self.cleaned_config(config)
