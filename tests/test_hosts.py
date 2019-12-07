from tests.const import TEST_DATA_DIR
from unittest import mock
from viper import Host
from viper import Hosts
from viper import Results
from viper import Runner
from viper import WhereConditions
from viper.db import ViperDB

import json
import pytest

CSV_FILE = f"{TEST_DATA_DIR}/hosts.csv"
JSON_FILE = f"{TEST_DATA_DIR}/hosts.json"


def test_hosts_to_from_json():
    hosts = Hosts.from_items(Host("1.1.1.1"))

    hosts_json = json.dumps(
        [
            {
                "ip": "1.1.1.1",
                "hostname": None,
                "domain": None,
                "port": 22,
                "login_name": None,
                "identity_file": None,
                "meta": {},
            }
        ]
    )

    assert Hosts.from_json(hosts_json) == Hosts.from_json(hosts.to_json()) == hosts

    with pytest.raises(ValueError) as e:
        Hosts.from_json("[{}]")

    assert "invalid input data" in str(e.__dict__)


def test_hosts_from_csv_file():
    CSV_FILE = f"{TEST_DATA_DIR}/hosts.csv"

    with open(CSV_FILE) as f:
        hosts = Hosts.from_items(*(Host(ip.strip()) for ip in f.read().strip().split()))

    assert (
        hosts.sort()
        == Hosts.from_file(CSV_FILE).sort()
        == Hosts((Host("1.1.1.1"), Host("1.2.3.4"), Host("2.2.2.2"))).sort()
    )


def test_hosts_from_json_file():

    assert Hosts.from_file(CSV_FILE) == Hosts.from_file(
        JSON_FILE, lambda f: Hosts.from_json(f.read())
    )


def test_hosts_format():
    hosts = Hosts.from_items(Host("1.1.1.1"), Host("2.2.2.2")).sort()
    assert hosts.format("<{ip}>") == "<1.1.1.1>\n<2.2.2.2>"
    assert hosts.format("<{ip}>", sep=" ") == "<1.1.1.1> <2.2.2.2>"


def test_hosts_range():
    hosts = Hosts.from_items(Host("1.1.1.1"), Host("2.2.2.2"), Host("3.3.3.3")).sort()
    assert hosts.range(1).sort().all() == hosts.all()[1:]
    assert hosts.range(None, 1).sort().all() == hosts.all()[:1]
    assert hosts.range(1, 2).sort().all() == hosts.all()[1:2]


def test_hosts_where():
    hosts = Hosts.from_items(Host("1.1.1.1"), Host("2.2.2.2"), Host("1.2.3.4")).sort()

    assert hosts.where("ip", WhereConditions.is_, ["1.1.1.1"]) == Hosts.from_items(
        Host("1.1.1.1")
    )

    assert hosts.where("ip", WhereConditions.is_not, ["1.1.1.1"]) == Hosts.from_items(
        Host("1.2.3.4"), Host("2.2.2.2")
    )

    assert hosts.where("ip", WhereConditions.contains, ["2.3"]) == Hosts.from_items(
        Host("1.2.3.4")
    )

    assert hosts.where("ip", WhereConditions.not_contains, ["2.3"]) == Hosts.from_items(
        Host("1.1.1.1"), Host("2.2.2.2")
    )

    assert hosts.where("ip", WhereConditions.startswith, ["1."]) == Hosts.from_items(
        Host("1.1.1.1"), Host("1.2.3.4")
    )

    assert hosts.where(
        "ip", WhereConditions.not_startswith, ["1."]
    ) == Hosts.from_items(Host("2.2.2.2"))

    assert hosts.where("ip", WhereConditions.endswith, ["3.4"]) == Hosts.from_items(
        Host("1.2.3.4")
    )

    assert hosts.where("ip", WhereConditions.not_endswith, ["3.4"]) == Hosts.from_items(
        Host("1.1.1.1"), Host("2.2.2.2")
    )

    with pytest.raises(ValueError) as e:
        hosts.where("ip", "IS", "1.1.1.1")

    assert "expecting enum" in str(e.__dict__)


def test_hosts_filter():
    assert Hosts.from_file(CSV_FILE).filter(
        lambda h: h.ip.startswith("1.")
    ) == Hosts.from_items(Host("1.2.3.4"), Host("1.1.1.1"))


def test_hosts_first():
    assert Hosts.from_file(CSV_FILE).sort().first(1) == Hosts.from_items(
        Host("1.1.1.1")
    )


def test_hosts_last():
    assert Hosts.from_file(CSV_FILE).sort().last(1) == Hosts.from_items(Host("2.2.2.2"))


def test_hosts_count():
    len(Hosts.from_file(CSV_FILE)) == Hosts.from_file(CSV_FILE).count() == 3


def test_hosts_sort():
    assert (
        Hosts.from_file(CSV_FILE).sort()
        == Hosts.from_file(CSV_FILE).sort(lambda h: h.ip)
        == Hosts((Host("1.1.1.1"), Host("1.2.3.4"), Host("2.2.2.2")))
    )


def test_hosts_task():

    task = mock.Mock()
    hosts = Hosts.from_file(CSV_FILE)

    assert hosts.task(task).sort(lambda x: x.host).all()[0] == Runner(
        task=task, host=hosts.sort().all()[0]
    )


@mock.patch("viper.collections.Task")
@mock.patch("viper.collections.Runners")
def test_hosts_run_task(Runners, Task):

    ViperDB.init(ViperDB.url, force=True)

    task = Task()
    hosts = Hosts.from_file(CSV_FILE)

    hosts.run_task(task, max_workers=3)

    Runners.from_items().run.assert_called_with(max_workers=3)

    assert hosts.results() == Results.from_items()
