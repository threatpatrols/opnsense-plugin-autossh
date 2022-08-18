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

from .exec_helpers import exec_command

from autossh.exceptions import AutosshException
from autossh.vars import __title__


logger = logging.getLogger(__title__)


def secure_delete(filename: str) -> True:
    """
    Deletes a file by overwriting the first {bytes_overwrite} bytes with
    data from /dev/urandom, then performing a regular file unlink
    """
    logger.debug(f"secure_delete(filename={filename})")

    if not os.path.isfile(filename):
        raise AutosshException("Unable to find file for secure_delete()", filename)

    bytes_to_overwrite = int(os.path.getsize(filename)) + (4096 * 32)  # 128K == default ZFS record size

    command_line = f"head -c{bytes_to_overwrite} /dev/urandom > {filename}"
    stdout, stderr, rc = exec_command(command_line)
    if stderr or rc > 0:
        raise AutosshException("Unable to overwrite file for secure_delete()", stderr)

    os.unlink(filename)
    if os.path.isfile(filename):
        raise AutosshException("File still remains after being unlinked")

    return True
