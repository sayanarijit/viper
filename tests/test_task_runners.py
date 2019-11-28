from viper.host import Host
from viper.hosts import Hosts
from viper.task import Task, TaskRunner


def make_command(host):
    return ("echo", host.ip)


def process_stdout(out):
    return f"output: {out}"


def process_stderr(err):
    return f"error: {err}"


def test_task_runners_run_in_sequence():
    host = Host("1.1.1.1")
    hosts = Hosts.from_items(host)
    task = Task(
        "print IP address",
        command_factory=make_command,
        stdout_processor=process_stdout,
        stderr_processor=process_stderr,
    )

    task_runners = hosts.task(task)
    results = task_runners.run_in_sequence()

    runner = task_runners.first()
    result = results.first()

    assert runner == TaskRunner(host, task)
    assert result.task == task
    assert result.host == host
    assert result.command == ("echo", "1.1.1.1")
    assert result.stdout == "output: 1.1.1.1\n"
    assert result.stderr == "error: "
    assert result.returncode == 0
    assert result.end > result.start
    assert result.ok()
    assert not result.errored()


def test_task_runners_run_in_sequence():
    host = Host("1.1.1.1")
    hosts = Hosts.from_items(host)
    task = Task(
        "print IP address",
        command_factory=make_command,
        stdout_processor=process_stdout,
        stderr_processor=process_stderr,
    )

    task_runners = hosts.task(task)
    results = task_runners.run_in_parallel()

    runner = task_runners.first()
    result = results.first()

    assert runner == TaskRunner(host, task)
    assert result.task == task
    assert result.host == host
    assert result.command == ("echo", "1.1.1.1")
    assert result.stdout == "output: 1.1.1.1\n"
    assert result.stderr == "error: "
    assert result.returncode == 0
    assert result.end > result.start
    assert result.ok()
    assert not result.errored()
