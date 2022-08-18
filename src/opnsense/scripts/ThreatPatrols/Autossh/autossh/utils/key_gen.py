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
import time
import base64
import logging

from .random_helpers import random_chars
from .system_helpers import get_system_hostid
from .exec_helpers import exec_command
from .file_helpers import secure_delete

from autossh.exceptions import AutosshException
from autossh.vars import __title__


logger = logging.getLogger(__title__)


def key_gen(key_type, fingerprint_type="sha256"):
    logger.debug(f"key_gen(key_type={key_type}, fingerprint_type={fingerprint_type})")

    temp_keyfile = os.path.join(
        "/tmp",
        f"autossh-keygen.{random_chars(8)}",
    )

    key_comment = f"host_id:{get_system_hostid()}"

    key_generators = {
        "dsa1024": f'ssh-keygen -t dsa -b 1024 -q -N "" -f "{temp_keyfile}" -C "{key_comment}"',
        "ecdsa256": f'ssh-keygen -t ecdsa -b 256 -q -N "" -f "{temp_keyfile}" -C "{key_comment}"',
        "ecdsa384": f'ssh-keygen -t ecdsa -b 384 -q -N "" -f "{temp_keyfile}" -C "{key_comment}"',
        "ecdsa521": f'ssh-keygen -t ecdsa -b 521 -q -N "" -f "{temp_keyfile}" -C "{key_comment}"',
        "ed25519": f'ssh-keygen -t ed25519 -q -N "" -f "{temp_keyfile}" -C "{key_comment}"',
        "rsa1024": f'ssh-keygen -t rsa -b 1024 -q -N "" -f "{temp_keyfile}" -C "{key_comment}"',
        "rsa2048": f'ssh-keygen -t rsa -b 2048 -q -N "" -f "{temp_keyfile}" -C "{key_comment}"',
        "rsa4096": f'ssh-keygen -t rsa -b 4096 -q -N "" -f "{temp_keyfile}" -C "{key_comment}"',
    }

    if key_type not in key_generators.keys():
        raise AutosshException("key_type not supported", key_type)

    exec_command(key_generators[key_type])
    if not os.path.isfile(temp_keyfile) or not os.path.isfile(temp_keyfile + ".pub"):
        raise AutosshException("unable to correctly generate ssh material")

    fingerprint, stderr, rc = exec_command(
        'ssh-keygen -f "{}" -l -E {}'.format(temp_keyfile + ".pub", fingerprint_type)
    )
    if stderr or rc > 0:
        raise AutosshException("unable to correctly generate ssh key signature", stderr)

    with open(temp_keyfile, "rb") as f:
        private_key_data = f.read()
    secure_delete(temp_keyfile)

    with open(temp_keyfile + ".pub", "rb") as f:
        public_key_data = f.read()
    secure_delete(temp_keyfile + ".pub")

    return {
        "status": "success",
        "message": "SSH keypair successfully created",
        "data": {
            "key_private": base64.b64encode(private_key_data).decode("utf8"),
            "key_public": base64.b64encode(public_key_data).decode("utf8"),
            "key_fingerprint": fingerprint.decode("utf8").strip(),
            "timestamp": time.time(),
        },
    }
