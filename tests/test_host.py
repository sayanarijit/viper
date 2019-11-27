from unittest import mock

import pytest

from viper.host import Host


def test_fqdn():
    with pytest.raises(UnboundLocalError) as e:
        Host("1.1.1.1").fqdn()
    assert "hostname and domain" in str(e)

    with pytest.raises(UnboundLocalError) as e:
        Host("1.1.1.1", hostname="host1").fqdn()
    assert "domain" in str(e)

    with pytest.raises(UnboundLocalError) as e:
        Host("1.1.1.1", domain="domain.com").fqdn()
    assert "hostname" in str(e)

    assert (
        Host("1.1.1.1", hostname="host1", domain="domain.com").fqdn()
        == "host1.domain.com"
    )


@mock.patch("viper.task.Task")
def test_task(Task):

    from viper.task import TaskRunner

    task = Task()
    runner = Host("1.1.1.1").task(task)

    assert isinstance(runner, TaskRunner)
    assert runner.task == task
