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
import re
import time
import logging

from autossh.vars import __title__
from autossh.vars import __autossh_logfile__

from autossh.exceptions import AutosshException
from .exec_helpers import get_pid_command
from .exec_helpers import exec_command

logger = logging.getLogger(__title__)


def connection_status(connection_uuid, ssh_config_file, filemask="/var/run/autossh.{}.{}"):
    logger.debug(
        f"connection_status(connection_uuid={connection_uuid}, ssh_config_file={ssh_config_file}, filemask={filemask})"
    )

    if not connection_uuid:
        raise AutosshException("Must provide connection_uuid value")

    status = {
        "enabled": False,
        "pids": {"daemon": None, "autossh": None, "ssh": None},
        "starts": None,
        "uptime": None,
        "last_healthy": None,
        "tunnel_device": None,
    }

    pid_file = filemask.format(connection_uuid, "pid")
    info_file = filemask.format(connection_uuid, "info")

    # enabled
    if os.path.isfile(ssh_config_file):
        with open(ssh_config_file, "r") as f:
            for line in f.readlines():
                if line.startswith("Host ") and connection_uuid in line:
                    status["enabled"] = True
                    break

    # daemon - pid
    daemon_command = None
    if os.path.isfile(pid_file):
        with open(pid_file, "r") as f:
            pid = int(f.read())
            daemon_command = get_pid_command(pid)
            if daemon_command:
                status["pids"]["daemon"] = pid

    # autossh - pid
    autossh_command = None
    if daemon_command:
        result = re.search("\[(\d+)\]", daemon_command)
        if result:
            pid = int(result.group(1))
            autossh_command = get_pid_command(pid)
            if autossh_command:
                status["pids"]["autossh"] = pid

    # ssh - starts + pid
    if autossh_command:
        result = re.search("parent of (\d+) \((\d+)\) ", autossh_command)
        if result:
            pid = int(result.group(1))
            status["starts"] = int(result.group(2))
            ssh_command = get_pid_command(pid)
            if ssh_command:
                status["pids"]["ssh"] = pid

    # uptime & tunnel_device
    if os.path.isfile(info_file):
        with open(info_file, "r") as f:
            for info_line in f.readlines():
                if info_line.startswith("timestamp"):
                    parts = info_line.strip().split(" ")
                    status["uptime"] = int(time.time() - int(parts[1]))
                if info_line.startswith("tunnel_device") and "NONE" not in info_line:
                    parts = info_line.strip().split(" ")
                    status["tunnel_device"] = parts[1]

    if status["pids"]["autossh"]:
        command_line = (
            f'grep "autossh {status["pids"]["autossh"]}" "{__autossh_logfile__}" | grep "autosshd" | '
            f'grep "connection ok" | tail -n1 | cut -d" " -f2'
        )
        stdout, stderr, rc = exec_command(command_line)
        if stdout and len(stdout) > 16:
            status["last_healthy"] = stdout.decode("utf8").strip()

    return {"status": "success", "message": "Connection data collected", "data": status}
