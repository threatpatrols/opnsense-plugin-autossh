import os
import sys

try:
    from autossh.exceptions import AutosshException
except ModuleNotFoundError:
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    from autossh.exceptions import AutosshException

from autossh.utils.system_helpers import get_system_hostid
from autossh.utils.system_helpers import get_system_hostname
from autossh.utils.random_helpers import random_chars


def test_get_system_hostname():

    response = get_system_hostname()
    assert response is not None
    assert len(response) > 1
    assert isinstance(response, str)


def test_get_system_hostid01(monkeypatch):

    filename = "/tmp/autossh_test.hostid"
    monkeypatch.setattr("autossh.vars.__system_hostid_file__", filename)

    faux_hostid = random_chars(length=20)

    with open(filename, "w") as f:
        f.write(faux_hostid)

    hostid = get_system_hostid()
    assert hostid == "00000000-0000-0000-0000-000000000000"  # occurs because length of hostid is not 36

    os.unlink(filename)


def test_get_system_hostid02(monkeypatch):

    filename = "/tmp/autossh_test.hostid"
    monkeypatch.setattr("autossh.utils.system_helpers.__system_hostid_file__", filename)

    faux_hostid = random_chars(length=36)

    with open(filename, "w") as f:
        f.write(faux_hostid)

    hostid = get_system_hostid()
    assert hostid == faux_hostid

    os.unlink(filename)
