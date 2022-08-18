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
import logging.handlers
import platform

from autossh.exceptions import AutosshException
from autossh.vars import __title__

CONSOLE_LOGGING_FORMAT = "%(asctime)s %(name)s[%(process)d] %(levelname)s: %(message)s"
SYSLOG_LOGGING_FORMAT = "%(name)s[%(process)d] %(levelname)s: %(message)s"
LOGFILE_LOGGING_FORMAT = "%(asctime)s __hostname__ %(name)s[%(process)d] %(levelname)s: %(message)s"
LOGGING_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"


logger = logging.getLogger(__title__)


def init_logger(console_level=None, syslog_level=None, logfile_level=None, logfile_filepath=None):

    # remove any existing handlers
    for handler in logger.handlers:
        logger.removeHandler(handler)

    console_level = __init_console_handler(console_level)
    syslog_level = __init_syslog_handler(syslog_level)
    logfile_level = __init_logfile_handler(logfile_level, logfile_filepath)

    # set the minimum log level
    logger.setLevel(level=min(console_level, syslog_level, logfile_level))


def __init_console_handler(console_level):

    if not console_level:
        return 100

    log_level = logging.getLevelName(console_level.upper())
    try:
        int(log_level)
    except ValueError:
        raise AutosshException(f"Unknown console_level:{console_level} requested")

    logging_format = logging.Formatter(
        fmt=CONSOLE_LOGGING_FORMAT.replace("__hostname__", str(platform.node()).split(".", maxsplit=1)[0]),
        datefmt=LOGGING_DATE_FORMAT,
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging_format)
    logger.addHandler(console_handler)

    return log_level


def __init_syslog_handler(syslog_level):

    if not syslog_level:
        return 100

    log_level = logging.getLevelName(syslog_level.upper())
    try:
        int(log_level)
    except ValueError:
        raise AutosshException(f"Unknown syslog_level:{syslog_level} requested")

    logging_format = logging.Formatter(
        fmt=SYSLOG_LOGGING_FORMAT.replace("__hostname__", str(platform.node()).split(".", maxsplit=1)[0]),
        datefmt=LOGGING_DATE_FORMAT,
    )

    if platform.system().lower().endswith("bsd"):
        syslog_address = "/var/run/log"
    else:
        syslog_address = "/dev/log"

    syslog_handler = logging.handlers.SysLogHandler(address=syslog_address)
    syslog_handler.setLevel(log_level)
    syslog_handler.setFormatter(logging_format)
    logger.addHandler(syslog_handler)

    return log_level


def __init_logfile_handler(logfile_level, logfile_filepath):

    if not logfile_level or not logfile_filepath:
        return 100

    log_level = logging.getLevelName(logfile_level.upper())
    try:
        int(log_level)
    except ValueError:
        raise AutosshException(f"Unknown logfile_level:{logfile_level} requested")

    logging_format = logging.Formatter(
        fmt=LOGFILE_LOGGING_FORMAT.replace("__hostname__", str(platform.node()).split(".", maxsplit=1)[0]),
        datefmt=LOGGING_DATE_FORMAT,
    )

    try:
        file_handler = logging.FileHandler(filename=logfile_filepath)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(logging_format)
        logger.addHandler(file_handler)
    except Exception:  # noqa
        logger.warning(f"Unable to write to logfile at: {logfile_filepath}")

    return log_level
