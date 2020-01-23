from unittest import mock
from viper import Host
from viper import meta

import json
import pytest


def test_from_func():
    with pytest.raises(ValueError) as e:
        Host.from_func("foo")

    assert "could not resolve" in str(e.__dict__)

    with pytest.raises(ValueError) as e:
        Host.from_func("viper.demo.tasks.ping")

    assert "does not produce a valid" in str(e.__dict__)


def test_host_to_json():
    assert (
        Host("1.1.1.1").to_json()
        == json.dumps(
            {
                "ip": "1.1.1.1",
                "hostname": None,
                "domain": None,
                "port": 22,
                "login_name": None,
                "identity_file": None,
                "meta": {},
            }
        )
        == str(Host("1.1.1.1"))
    )


def test_from_json():
    assert Host.from_json(
        json.dumps(
            {
                "ip": "1.1.1.1",
                "hostname": None,
                "domain": None,
                "port": 22,
                "login_name": None,
                "identity_file": None,
                "meta": {"foo": "bar"},
            }
        )
    ) == Host("1.1.1.1", meta=meta(foo="bar"))

    with pytest.raises(ValueError) as e:
        Host.from_json("{}")

    assert "value is required" in str(e.__dict__)


def test_getitem():
    assert Host("1.1.1.1")["ip"] == "1.1.1.1"
    with pytest.raises(KeyError):
        Host("1.1.1.1")["foo"]


def test_fqdn():
    with pytest.raises(AttributeError) as e:
        Host("1.1.1.1").fqdn()
    assert "hostname and domain" in str(vars(e))

    with pytest.raises(AttributeError) as e:
        Host("1.1.1.1", "host1").fqdn()
    assert "domain" in str(vars(e))

    with pytest.raises(AttributeError) as e:
        Host("1.1.1.1", domain="domain.com").fqdn()
    assert "hostname" in str(vars(e))

    assert Host("1.1.1.1", "host1", "domain.com").fqdn() == "host1.domain.com"


def test_format():
    assert Host("1.1.1.1").format("<{ip}>") == "<1.1.1.1>"


@mock.patch("viper.collections.Task")
def test_task(Task):

    from viper import Runner

    task = Task()
    runner = Host("1.1.1.1").task(task)

    assert isinstance(runner, Runner)
    assert runner.task == task


def test_run_task():

    from viper.db import ViperDB
    from viper.demo.tasks import ping

    ViperDB.init(ViperDB.url, force=True)

    assert Host("8.8.8.8").run_task(ping()).returncode == 0


@mock.patch("viper.collections.Results")
def test_host_results(Results):
    host = Host("1.1.1.1")
    host.results()
    Results.by_host.assert_called_with(host)
