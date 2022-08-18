#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Copyright (c) 2022 Threat Patrols Pty Ltd <contact@threatpatrols.com>
    Copyright (c) 2018 Verb Networks Pty Ltd <contact@verbnetworks.com>
    Copyright (c) 2018 Nicholas de Jong <me@nicholasdejong.com>
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
import io
import sys
import base64
import logging
import configparser

from autossh.exceptions import AutosshException
from autossh.vars import __title__

sys.path.insert(0, "/usr/local/opnsense/service/modules")
from config import Config as OpnsenseConfig  # OPNsense Config class


logger = logging.getLogger(__title__)


class AutosshConfigHelper:
    """
    AutosshConfigHelper provides autossh configuration file helper processing
    """

    ssh_config_filename = None

    __ssh_config = None
    __system_config = None
    __data_model = None

    def __init__(self, system_config_filename, ssh_config_filename, data_model_filename):
        self.ssh_config_filename = ssh_config_filename
        self.__system_config = self.__load_system_config(system_config_filename)
        self.__ssh_config = self.__load_ssh_config(self.ssh_config_filename)
        self.__data_model = self.__load_data_model(data_model_filename)

    def process(self):
        logger.debug(f"process()")

        host_section_count = 0
        for host_section in self.get_ssh_config_host_sections():
            self.do_write_identity_file(host_section)
            self.do_touch_known_hosts(host_section)
            self.do_replace_bind_interface(host_section)
            self.do_replace_by_data_model(host_section, "Ciphers", "items.tunnels.tunnel.ciphers.optionvalues")
            self.do_replace_by_data_model(
                host_section, "HostKeyAlgorithms", "items.tunnels.tunnel.host_key_algorithms.optionvalues"
            )
            self.do_replace_by_data_model(
                host_section, "KexAlgorithms", "items.tunnels.tunnel.kex_algorithms.optionvalues"
            )
            self.do_replace_by_data_model(host_section, "MACs", "items.tunnels.tunnel.macs.optionvalues")
            self.do_replace_by_data_model(
                host_section, "PubkeyAcceptedKeyTypes", "items.tunnels.tunnel.pubkey_accepted_key_types.optionvalues"
            )
            self.do_replace_by_data_model(host_section, "RekeyLimit", "items.tunnels.tunnel.rekey_limit.optionvalues")
            host_section_count += 1

        return {"status": "success", "message": f"Updated {host_section_count} configuration host sections"}

    def get_ssh_config_host_sections(self) -> list:
        logger.debug(f"get_ssh_config_host_sections()")
        return list(self.__ssh_config.keys())

    def do_write_identity_file(self, host_section) -> True:
        logger.debug(f"do_write_identity_file(host_section={host_section})")

        ssh_config_keypath = "{}.IdentityFile".format(host_section)
        identity_file = self.__get_by_keypath(ssh_config_keypath, self.__ssh_config)
        if identity_file is None:
            raise AutosshException("Could not locate required ssh_config option", ssh_config_keypath)

        ssh_key_uuid_keypath = "__uuid__.{}.ssh_key".format(host_section)
        ssh_key_uuid = self.__get_by_keypath(ssh_key_uuid_keypath, self.__system_config)
        if not ssh_key_uuid:
            raise AutosshException("Could not locate required system_config option", ssh_key_uuid_keypath)

        ssh_key_private_keypath = "__uuid__.{}.key_private".format(ssh_key_uuid)
        ssh_key_private_b64 = self.__get_by_keypath(ssh_key_private_keypath, self.__system_config)
        if not ssh_key_private_b64:
            raise AutosshException("Could not locate required system_config option", ssh_key_private_keypath)

        if not os.path.isdir(os.path.dirname(identity_file)):
            os.makedirs(os.path.dirname(identity_file), 0o700)

        with os.fdopen(os.open(identity_file, os.O_CREAT | os.O_WRONLY, 0o600), "w") as f:
            f.write(base64.b64decode(ssh_key_private_b64).decode("utf8"))

        return True

    def do_touch_known_hosts(self, host_section):
        logger.debug(f"do_touch_known_hosts(host_section={host_section})")

        ssh_config_keypath = "{}.UserKnownHostsFile".format(host_section)
        known_hosts_file = self.__get_by_keypath(ssh_config_keypath, self.__ssh_config)
        if known_hosts_file is None:
            raise AutosshException("Could not locate required ssh_config option", ssh_config_keypath)

        if not os.path.isdir(os.path.dirname(known_hosts_file)):
            os.makedirs(os.path.dirname(known_hosts_file), 0o700)

        with os.fdopen(os.open(known_hosts_file, os.O_CREAT | os.O_APPEND, 0o600)):
            os.utime(known_hosts_file, None)

        return True

    def do_replace_bind_interface(self, host_section) -> bool:
        logger.debug(f"do_replace_bind_interface(host_section={host_section})")

        ssh_config_keypath = "{}.BindInterface".format(host_section)
        interface_by_name = self.__get_by_keypath(ssh_config_keypath, self.__ssh_config)
        if interface_by_name is None:
            raise AutosshException("Could not locate required ssh_config section and option", ssh_config_keypath)

        system_config_keypath = "interfaces.{}.if".format(interface_by_name)
        interface_by_config = self.__get_by_keypath(system_config_keypath, self.__system_config)
        if not interface_by_config:
            return False  # can occur in edge-case when re-run and this replacement has already been performed

        self.__replace_ssh_config_item(ssh_config_keypath, str(interface_by_config))
        return True

    def do_replace_by_data_model(self, host_section, config_item, keypath) -> True:
        logger.debug(
            f"do_replace_by_data_model(host_section={host_section}, config_item={config_item}, keypath={keypath})"
        )

        ssh_config_keypath = "{}.{}".format(host_section, config_item)
        ssh_config_item = self.__get_by_keypath(ssh_config_keypath, self.__ssh_config)
        if not ssh_config_item:
            raise AutosshException("Could not locate required ssh_config option", ssh_config_keypath)

        data_model_items = self.__get_by_keypath(keypath, self.__data_model)
        if not data_model_items:
            raise AutosshException("Could not locate required data_model option", data_model_items)

        for data_model_item_k in data_model_items:
            ssh_config_item = ssh_config_item.replace(data_model_item_k, data_model_items[data_model_item_k])

        self.__replace_ssh_config_item(ssh_config_keypath, ssh_config_item)
        return True

    def __replace_ssh_config_item(self, keypath, replacement_string) -> True:
        host_uuid, ssh_option = keypath.split(".")
        current_string = self.__get_by_keypath(keypath, self.__ssh_config)

        with open(self.ssh_config_filename, "r") as f:
            ssh_config_lines = f.readlines()

        in_section = False
        ssh_config_content = ""
        for ssh_config_line in ssh_config_lines:
            if ssh_config_line.startswith("Host "):
                if host_uuid in ssh_config_line:
                    in_section = True
                else:
                    in_section = False
            if in_section is True and ssh_option in ssh_config_line and current_string in ssh_config_line:
                ssh_config_line = ssh_config_line.replace(current_string, replacement_string)
            ssh_config_content += ssh_config_line

        with open(self.ssh_config_filename, "w") as f:
            f.write(ssh_config_content)

        return True

    def __get_by_keypath(self, keypath, data):
        for item in keypath.split("."):
            if item in data:
                data = data[item]
            else:
                return None
        return data

    def __load_ssh_config(self, ssh_config_file) -> dict:
        if not os.path.isfile(ssh_config_file):
            raise AutosshException("Could not find ssh_config_file", ssh_config_file)
        with open(ssh_config_file, "r") as f:
            ssh_config_raw_lines = f.readlines()

        # Munge ssh_config_raw_lines into a format compatible with Python configparser
        ssh_config_raw = ""
        for ssh_config_raw_line in ssh_config_raw_lines:
            ssh_config_raw_line = ssh_config_raw_line.lstrip(" ")
            if ssh_config_raw_line.startswith("Host "):
                parts = ssh_config_raw_line.split(" ")
                ssh_config_raw += "[{}]\n".format(parts[1].strip())
            elif not ssh_config_raw_line.startswith("#") and len(ssh_config_raw_line.strip()) > 0:
                parts = ssh_config_raw_line.split(" ")
                ssh_config_raw += parts.pop(0) + ": " + " ".join(parts)
            else:
                ssh_config_raw += ssh_config_raw_line

        cp = configparser.ConfigParser(allow_no_value=True, interpolation=None)
        cp.optionxform = str  # preserve upper/lower case
        cp.read_file(io.StringIO(ssh_config_raw))

        ssh_config = {}
        for section in cp.sections():
            for option in cp.options(section):
                if section not in ssh_config:
                    ssh_config[section] = {}
                ssh_config[section][option] = cp.get(section, option)

        return ssh_config

    def __load_system_config(self, system_config_file) -> dict:
        if not os.path.isfile(system_config_file):
            raise AutosshException("Could not find system_config_file", system_config_file)
        return OpnsenseConfig(system_config_file).get()

    def __load_data_model(self, data_model_file) -> dict:
        if not os.path.isfile(data_model_file):
            raise AutosshException("Could not find data_model_file", data_model_file)
        return OpnsenseConfig(data_model_file).get()
