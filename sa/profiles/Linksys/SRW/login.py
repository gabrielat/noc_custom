# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Linksys.SWR.login
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.core.error import NOCError
from noc.sa.interfaces.ilogin import ILogin


class Script(BaseScript):
    """
    Try to log in
    """

    name = "Linksys.SRW.login"
    interface = ILogin
    requires = []

    def execute(self):
        try:
            self.cli("\x1A")
            return {"result": True, "message": ""}
        except NOCError as e:
            return {"result": False, "message": "Error: %s (%s)" % (e.default_msg, e.message)}
        except Exception as e:
            return {"result": False, "message": "Exception: %s" % repr(e)}
