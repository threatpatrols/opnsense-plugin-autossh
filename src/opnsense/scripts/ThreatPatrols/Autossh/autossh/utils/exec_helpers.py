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

import logging
import subprocess

from autossh.vars import __title__
from autossh.exceptions import AutosshException


logger = logging.getLogger(__title__)


def get_pid_command(pid: int) -> str:
    logger.debug(f"get_pid_command(pid={pid})")
    stdout, stderr, rc = exec_command("ps -o command= -p {}".format(int(pid)))

    if stderr:
        raise AutosshException(stderr)

    return stdout.decode("utf8")


def exec_command(command_line: str, timeout=10) -> tuple:
    """
    Execute a shell command and return the stdout, stderr and exit-code

    :param command_line: str
    :param timeout: int
    :return:
    """
    logger.debug(f"exec_command(command_line={command_line}, timeout={timeout})")
    try:
        sp = subprocess.run(command_line, shell=True, capture_output=True, timeout=timeout, check=False)
    except subprocess.TimeoutExpired as e:
        raise AutosshException(e) from e

    logger.debug(
        f"exec_command() -> stdout=<stdout:len={len(sp.stdout)}> "
        f"stderr=<stderr:len={len(sp.stderr)}> returncode={sp.returncode}"
    )
    return sp.stdout, sp.stderr, sp.returncode
