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

from autossh.exceptions import AutosshException
from autossh.vars import __title__


logger = logging.getLogger(__title__)


def host_keys(connection_uuid, filemask="/var/db/autossh/{}.known_hosts") -> dict:
    logger.debug(f"host_keys(connection_uuid={connection_uuid}, filemask={filemask})")

    filename = filemask.format(connection_uuid)
    if not os.path.isfile(filename):
        raise AutosshException(f"No known_hosts file found for {connection_uuid}; is this a new connection?")

    with open(filename, "r") as f:
        known_host_lines = f.readlines()

    known_host_keys = []
    for known_host_line in known_host_lines:
        values = known_host_line.rstrip().split(" ")
        values.pop(0)
        known_host_keys.append(" ".join(values))

    return {
        "status": "success",
        "message": f"Found {len(known_host_keys)} host keys found for {connection_uuid}",
        "data": known_host_keys,
    }
