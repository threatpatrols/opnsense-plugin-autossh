import os
import sys

try:
    from autossh.exceptions import AutosshException
except ModuleNotFoundError:
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    from autossh.exceptions import AutosshException

from autossh.utils.content_helpers import normalize_timestamp


def test_normalize_timestamp_01():

    timezone = "US/Central"
    timestring = "2018-08-04T07:46:37.000Z"
    response = normalize_timestamp(timestring=timestring, target_timezone=timezone)

    assert response == "2018-08-04 02:46:37"


def test_normalize_timestamp_02():

    timezone = "Asia/Manila"
    timestring = "2018-08-14 07:28:05+00:00"
    response = normalize_timestamp(timestring=timestring, target_timezone=timezone)

    assert response == "2018-08-14 15:28:05"


def test_normalize_timestamp_03():

    timezone = "Europe/Berlin"
    timestring = "2018-08-04T07:44:45Z"
    response = normalize_timestamp(timestring=timestring, target_timezone=timezone)

    assert response == "2018-08-04 09:44:45"


def test_normalize_timestamp_04():

    timezone = "Europe/London"
    timestring = "20180802T074245Z"
    response = normalize_timestamp(timestring=timestring, target_timezone=timezone)

    assert response == "2018-08-02 08:42:45"


def test_normalize_timestamp_05():

    timezone = "Australia/Perth"
    timestring = "20180804Z074445"
    response = normalize_timestamp(timestring=timestring, target_timezone=timezone)

    assert response == "2018-08-04 15:44:45"


def test_normalize_timestamp_06():

    timezone = "Asia/Singapore"
    timestring = 1533373930.983988
    response = normalize_timestamp(timestring=timestring, target_timezone=timezone)

    assert response == "2018-08-05 03:12:10"


def test_normalize_timestamp_07():

    timezone = "Asia/Jakarta"
    timestring = 1533378888
    response = normalize_timestamp(timestring=timestring, target_timezone=timezone)

    assert response == "2018-08-05 03:34:48"


def test_normalize_timestamp_08():

    timestring = 1533378888
    response = normalize_timestamp(timestring=timestring)

    assert response == "2018-08-04 20:34:48"


def test_normalize_timestamp_09():

    timestring = "2018-08-04T20:34:48Z"
    response = normalize_timestamp(timestring=timestring)

    assert response == "2018-08-04 20:34:48"
