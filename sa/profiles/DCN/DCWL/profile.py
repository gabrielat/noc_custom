# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: DCN
# OS:     DCWL
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "DCN.DCWL"
    pattern_prompt = r"^(?P<hostname>\S+)\s*#|~ #"
    command_more = "\n"
    command_submit = "\n"
    command_exit = "exit"
    pattern_syntax_error = r"Invalid command\."

    matchers = {"is_wl8200": {"platform": {"$regex": "WL8200-TL3.+"}}}

    class shell(object):
        """Switch context manager to use with "with" statement"""

        def __init__(self, script):
            self.script = script
            self.on_session = False

        def __enter__(self):
            """Enter switch context"""
            try:
                self.script.cli("shell")
                self.on_session = True
            except self.script.CLISyntaxError:
                pass

        def __exit__(self, exc_type, exc_val, exc_tb):
            """Leave switch context"""
            if exc_type is None and self.on_session:
                self.script.cli("exit\r")

    INTERFACE_TYPES = {
        "lo": "loopback",  # Loopback
        "brv": "SVI",  # No comment
        "eth": "physical",  # No comment
        "wla": "physical",  # No comment
    }

    @classmethod
    def get_interface_type(cls, name):
        c = cls.INTERFACE_TYPES.get(name[:3])
        return c

    @staticmethod
    def table_parser(v):
        """
        Parse table
        :param v:
        :return:
        """
        r = {}
        for line in v.splitlines():
            if not line.strip(" -"):
                continue
            value = line.split(" ", 1)
            if len(value) == 2:
                r[value[0].strip()] = value[1].strip()
            else:
                r[value[0]] = None
        return r
