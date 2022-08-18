"""
    Copyright (c) 2022 Threat Patrols Pty Ltd <contact@threatpatrols.com>
    All rights reserved.

    Redistribution and use in source and binary forms, with or without modification,
    are permitted provided that the following conditions are met:

    1. Redistributions of source code must retain the above copyright notice, this
       list of conditions and the following disclaimer.

    2. Redistributions in binary form must reproduce the above copyright notice,
       this list of conditions and the following disclaimer in the documentation
       and/or other materials provided with the distribution.

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
    ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
    WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
    DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
    ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
    (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
    LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
    ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
    (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
    SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import os
import logging
import platform

from autossh.vars import __title__
from autossh.vars import __system_hostid_file__


logger = logging.getLogger(__title__)


def get_system_hostid() -> str:
    """
    Reads the system hostid file and returns this value if exists, else returns a dummy zero'd value

    :return:
    """
    logger.debug("get_system_hostid()")

    hostid = "00000000-0000-0000-0000-000000000000"
    if os.path.isfile(__system_hostid_file__):
        with open(__system_hostid_file__, "rb") as f:
            data = f.read()
            if len(data) > 30:
                hostid = data.decode("utf8").strip()
    return hostid


def get_system_hostname() -> str:
    """
    Acquires the system hostname via the Python platform.node() function

    :return:
    """
    logger.debug("get_system_hostname()")

    return str(platform.node()).split(".", maxsplit=1)[0]
