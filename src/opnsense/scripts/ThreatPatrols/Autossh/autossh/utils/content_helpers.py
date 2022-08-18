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

import re
import logging
import datetime
import pytz
from typing import Tuple

from autossh.exceptions import AutosshException
from autossh.vars import __title__


logger = logging.getLogger(__title__)


def normalize_timestamp(timestring: Tuple[str, int, float], target_timezone=None) -> str:
    """
    Takes the supplied timestring and normalizes it into format %Y-%m-%d %H:%M:%S optionally
    adjusted into the requested target_timezone

    NB: Handles a limited set of possible input timestring formats only.

    :param timestring:
    :param target_timezone:
    :return:
    """

    def datetime_from_timestring(ts):

        # 2018-08-14 07:28:05+00:00
        # 2022-06-20 22:50:49.347000+00:00
        t = re.compile("^(\\d\\d\\d\\d)-(\\d\\d)-(\\d\\d)[T| ](\\d\\d):(\\d\\d):(\\d+).*?\\+00:00").findall(ts)
        if t:
            std = f"{t[0][0]}-{t[0][1]}-{t[0][2]} {t[0][3]}:{t[0][4]}:{t[0][5]} +0000"
            return datetime.datetime.strptime(std, "%Y-%m-%d %H:%M:%S %z")

        # 2018-08-04T07:46:37.000Z
        # 2018-08-04T07:44:45Z
        t = re.compile("^(\\d\\d\\d\\d)-(\\d\\d)-(\\d\\d)[T| ](\\d\\d):(\\d\\d):(\\d+).*?Z").findall(ts)
        if t:
            std = f"{t[0][0]}-{t[0][1]}-{t[0][2]} {t[0][3]}:{t[0][4]}:{t[0][5]} +0000"
            return datetime.datetime.strptime(std, "%Y-%m-%d %H:%M:%S %z")

        # 20180804T074445Z
        # 20180804Z074445
        t = re.compile("^(\\d\\d\\d\\d)(\\d\\d)(\\d\\d)[T|Z](\\d\\d)(\\d\\d)(\\d+)[Z]?").findall(ts)
        if t:
            std = f"{t[0][0]}-{t[0][1]}-{t[0][2]} {t[0][3]}:{t[0][4]}:{t[0][5]} +0000"
            return datetime.datetime.strptime(std, "%Y-%m-%d %H:%M:%S %z")

        # 1533378888
        # 1533373930.983988
        t = re.compile("^(\\d+)(\\.\\d+)?").findall(ts)
        if t:
            std = datetime.datetime.fromtimestamp(float(f"{t[0][0]}{t[0][1]}"))
            return pytz.timezone("UTC").localize(std)

        return None

    datetime_obj = datetime_from_timestring(ts=str(timestring))

    if not datetime_obj:
        raise AutosshException("Unknown timestamp format supplied, unable to normalize", timestring)

    if target_timezone:
        datetime_obj = datetime_obj.astimezone(pytz.timezone(target_timezone))

    return datetime_obj.strftime("%Y-%m-%d %H:%M:%S")
