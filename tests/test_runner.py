from unittest import mock
from viper import Host
from viper import Runner
from viper import Task

import pytest


def make_empty_command(host):
    return ()


def make_echo_command(host, what="foo"):
    return ("echo", what)


def make_failing_command(host):
    return ("false",)


def make_invalid_command(host):
    return ("echo", 1, None, True, False)


def process_stdout(out):
    return f"output: {out}"


def process_stderr(err):
    return f"error: {err}"


def pre_run(task):
    pass


def post_run(result):
    pass


def test_runner_invalid_data():
    with pytest.raises(ValueError) as e:
        Runner.from_dict({})

    assert "invalid input data" in str(e.__dict__)


def test_runner_run_save_load():
    host = Host("1.1.1.1")

    task = Task(
        "print IP address",
        command_factory=make_echo_command,
        stdout_processor=process_stdout,
        stderr_processor=process_stderr,
        pre_run=pre_run,
        post_run=post_run,
    )

    runner = host.task(task)

    result = runner.run()

    assert runner == Runner(host, task)
    assert result.task == task
    assert result.host == host
    assert result.args == ()
    assert result.command == ("echo", "foo")
    assert result.stdout == "output: foo\n"
    assert result.stderr == "error: "
    assert result.returncode == 0
    assert result.end > result.start
    assert result.ok()
    assert not result.errored()


def test_tasks_runner_run_invalid_commands():
    host = Host("1.1.1.1")
    task = Task("Fail", command_factory=make_invalid_command)

    with pytest.raises(ValueError) as e:
        host.task(task).run()

    assert "command must be a list/tuple of strings" in str(e.__dict__)


def test_tasks_runner_run_invalid_args():
    host = Host("1.1.1.1")
    task = Task("Fail", command_factory=make_echo_command)

    with pytest.raises(ValueError) as e:
        host.task(task, None).run()

    assert "args must be a list/tuple of strings" in str(e.__dict__)


def test_tasks_runner_run_empty_command():
    host = Host("1.1.1.1")
    task = Task("Fail", command_factory=make_empty_command)

    with pytest.raises(ValueError) as e:
        host.task(task).run()

    assert "generated empty command" in str(e.__dict__)


def test_tasks_runner_retry():
    host = Host("1.1.1.1")
    task = Task("Fail", command_factory=make_failing_command, retry=1)

    assert host.task(task).run().retry == 1


@mock.patch("viper.collections.Results")
def test_runner_results(Results):
    host = mock.Mock()
    task = mock.Mock()

    runner = Runner(host=host, task=task)
    runner.results()
    Results.by_runner.assert_called_with(runner)
