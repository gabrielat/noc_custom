# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: NSN
# OS:     hiX56xx
# sergey.sadovnikov@gmail.com
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "NSN.hiX56xx"
    pattern_more = "^ --More-- "
    pattern_unprivileged_prompt = r"^\S+?>"
    pattern_syntax_error = r"% Invalid input detected at"
    command_disable_pager = "terminal length 0"
    command_super = "enable"
    command_enter_config = "configure terminal"
    command_leave_config = "exit"
    command_save_config = "wr mem\n"
    pattern_prompt = r"^(?P<hostname>\S+?)(?:-\d+)?(?:\((config|bridge)[^\)]*\))?#"

    def shutdown_session(self, script):
        script.cli("terminal no length")

    def convert_interface_name(self, s):
        if s.startswith("adsl2"):
            s = "%s/%s" % (s[5:-2], s[-2:])
        return s
