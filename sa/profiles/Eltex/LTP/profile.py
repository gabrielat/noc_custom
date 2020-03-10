# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Eltex
# OS:     LTP
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Eltex.LTP"
    pattern_username = r"(?<!Last>)([Uu]ser ?[Nn]ame|[Ll]ogin): ?"
    pattern_more = [(r"--More-- ", " "), (r"\[Yes/press any key for no\]", "Y")]
    pattern_unprivileged_prompt = r"^\S+>"
    pattern_syntax_error = (
        r"(Command not found. Use '?' to view available commands|"
        r"Incomplete command\s+|Invalid argument\s+|Unknown command)"
    )

    #    command_disable_pager = "terminal datadump"
    #    command_super = "enable"
    username_submit = "\r"
    password_submit = "\r"
    command_submit = "\r"

    command_enter_config = "configure"
    command_leave_config = "exit"
    command_save_config = "save"
    pattern_prompt = r"^\S+#"

    class switch(object):
        """Switch context manager to use with "with" statement"""

        def __init__(self, script):
            self.script = script

        def __enter__(self):
            """Enter switch context"""
            self.script.cli("switch")

        def __exit__(self, exc_type, exc_val, exc_tb):
            """Leave switch context"""
            if exc_type is None:
                self.script.cli("exit\r")

    rx_interface_name = re.compile(r"^(?P<ifname>\S.+)\s+(?P<number>\d+)", re.MULTILINE)

    def convert_interface_name(self, s):
        match = self.rx_interface_name.match(s)
        if not match:
            return s
        if "PON channel" in match.group("ifname"):
            return "pon-port %s" % match.group("number")
        elif "Uplink" in match.group("ifname") and int(match.group("number")) <= 7:
            return "front-port %s" % match.group("number")
        elif "Uplink" in match.group("ifname") and int(match.group("number")) > 7:
            return "10G-front-port %s" % (int(match.group("number")) - 8)
        else:
            return s
