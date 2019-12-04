from unittest import mock
from viper import Host
from viper import Result
from viper import Runner
from viper import Task


def make_echo_command(host):
    return ("echo", host.ip)


def make_failing_command(host):
    return ("false",)


def process_stdout(out):
    return f"output: {out}"


def process_stderr(err):
    return f"error: {err}"


def pre_run(task):
    pass


def post_run(result):
    pass


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
    assert result.command == ("echo", "1.1.1.1")
    assert result.stdout == "output: 1.1.1.1\n"
    assert result.stderr == "error: "
    assert result.returncode == 0
    assert result.end > result.start
    assert result.ok()
    assert not result.errored()
    assert Result.by_hash(hash(result)) == result


def test_tasks_runner_retry():
    host = Host("1.1.1.1")
    task = Task("Fail", command_factory=make_failing_command, retry=3)

    assert host.task(task).run().retry == 3


@mock.patch("viper.collections.Results")
def test_runner_results(Results):
    host = mock.Mock()
    task = mock.Mock()

    runner = Runner(host=host, task=task)
    runner.results()
    Results.by_runner.assert_called_with(runner)
