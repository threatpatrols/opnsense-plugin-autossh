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

import sys
import json
import logging
import argparse
from signal import signal, SIGINT

from autossh.utils.logger_helpers import init_logger
from autossh.utils.key_gen import key_gen as autossh_key_gen
from autossh.utils.config_helper import AutosshConfigHelper
from autossh.utils.host_keys import host_keys as autossh_host_keys
from autossh.utils.connection_status import connection_status as autossh_connection_status
from autossh.exceptions import AutosshException

from autossh.__version__ import __version__

from autossh.vars import __title__
from autossh.vars import __logging_console_level__
from autossh.vars import __logging_syslog_level__
from autossh.vars import __system_config_file__
from autossh.vars import __autossh_config_file__
from autossh.vars import __autossh_data_model_file__


logger = logging.getLogger(__title__)


def sigint_handler(__signal_received, __frame):
    print("SIGINT received, exiting.")
    sys.exit(1)


def autossh_cli():

    # args
    args = __argparse()

    # action - version
    if args.action == "version":
        return {"version": __version__}

    if args.action == "key_gen":
        return autossh_key_gen(key_type=args.key_type)

    elif args.action == "config_helper":
        return AutosshConfigHelper(
            system_config_filename=args.system_config,
            ssh_config_filename=args.ssh_config,
            data_model_filename=args.data_model,
        ).process()

    elif args.action == "host_keys" and args.connection_uuid:
        return autossh_host_keys(connection_uuid=args.connection_uuid)

    elif args.action == "connection_status" and args.connection_uuid:
        return autossh_connection_status(connection_uuid=args.connection_uuid, ssh_config_file=args.ssh_config)

    raise AutosshException("Unknown <action> or incomplete <action> arguments")


def __argparse():

    parser = argparse.ArgumentParser(add_help=True, description="Autossh tunnel management interface")

    parser.add_argument("--debug", action="store_true", help="Set logging to DEBUG level")

    parser.add_argument(
        "action",
        type=str,
        metavar="<action>",
        choices=["version", "key_gen", "config_helper", "host_keys", "connection_status"],
        help="Autossh action request",
    )

    # Actions: key_gen
    parser.add_argument("--key_type", type=str, help="Type of SSH key to generate")

    # Actions: host_keys, connection_status
    parser.add_argument("--connection_uuid", type=str, help="UUID of the Autossh tunnel connection to use")

    # Actions: config_helper
    parser.add_argument(
        "--ssh_config",
        default=__autossh_config_file__,
        type=str,
        help="Overwrites the default ssh_config file (autossh.conf) file location",
    )
    parser.add_argument(
        "--system_config",
        default=__system_config_file__,
        type=str,
        help="Overwrites the default system config file (config.xml) file location",
    )
    parser.add_argument(
        "--data_model",
        default=__autossh_data_model_file__,
        type=str,
        help="Overwrites the default autossh data model file (Autossh.xml) file location",
    )

    parsed_args = parser.parse_args()

    for arg_name in vars(parsed_args):
        value = getattr(parsed_args, arg_name)
        if len(str(value)) == 0:
            setattr(parsed_args, arg_name, None)

    return parsed_args


if __name__ == "__main__":
    signal(SIGINT, sigint_handler)

    if "--debug" in sys.argv:
        debug = True
        init_logger(console_level="debug", syslog_level="debug")
    else:
        debug = False
        init_logger(console_level=__logging_console_level__, syslog_level=__logging_syslog_level__)

    try:
        response = autossh_cli()

    except AutosshException as e:
        message = str(e).strip()
        logger.error(message)
        response = {
            "status": "fail",
            "message": message,
        }

    except Exception as e:  # noqa pylint:disable=broad-except
        message = str(e).strip()
        logger.critical(msg=message, exc_info=debug)  # provides stacktrace if debug mode
        response = {
            "status": "fail",
            "message": message,
        }

    print(json.dumps(response, default=str, sort_keys=True, indent="  "))
