import json
from unittest import mock

import pytest

from tests.const import TEST_DATA_DIR
from viper.host import Host
from viper.hosts import Hosts

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
            }
        ]
    )

    assert Hosts.from_json(hosts_json) == Hosts.from_json(hosts.to_json()) == hosts


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


def test_hosts_filter():
    assert Hosts.from_file(CSV_FILE).filter(
        lambda h: h.ip.startswith("1.")
    ) == Hosts.from_items(Host("1.2.3.4"), Host("1.1.1.1"))


def test_hosts_get():

    with pytest.raises(LookupError) as e:
        Hosts.from_file(CSV_FILE).get(lambda h: False)
    assert "could not find" in str(e)

    with pytest.raises(LookupError) as e:
        Hosts.from_file(CSV_FILE).get(lambda h: True)
    assert "multiple" in str(e)

    assert Hosts.from_file(CSV_FILE).get(lambda h: h.ip == "1.1.1.1") == Host("1.1.1.1")


def test_hosts_first():
    assert Hosts.from_file(CSV_FILE).sort().first() == Host("1.1.1.1")


def test_hosts_last():
    assert Hosts.from_file(CSV_FILE).sort().last() == Host("2.2.2.2")


def test_hosts_index():
    assert (
        Hosts.from_file(CSV_FILE).sort().index(1)
        == Hosts.from_file(CSV_FILE).sort()[1]
        == Host("1.2.3.4")
    )


def test_hosts_count():
    len(Hosts.from_file(CSV_FILE)) == Hosts.from_file(CSV_FILE).count() == 3


def test_hosts_sort():
    assert (
        Hosts.from_file(CSV_FILE).sort()
        == Hosts.from_file(CSV_FILE).sort(lambda h: h.ip)
        == Hosts((Host("1.1.1.1"), Host("1.2.3.4"), Host("2.2.2.2")))
    )


def test_hosts_task():

    from viper import Task, Hosts, TaskRunner

    task = mock.Mock()
    hosts = Hosts.from_file(CSV_FILE)

    assert hosts.task(task).sort(lambda x: x.host).first() == TaskRunner(
        task=task, host=hosts.sort().first()
    )


@mock.patch("viper.task.Task")
@mock.patch("viper.task_runners.TaskRunners")
def test_hosts_run_task(TaskRunners, Task):

    task = Task()
    hosts = Hosts.from_file(CSV_FILE)

    hosts.run_task(task, max_workers=3)

    TaskRunners.from_items().run.assert_called_with(max_workers=3)
