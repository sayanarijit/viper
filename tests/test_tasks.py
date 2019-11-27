from viper.host import Host
from viper.hosts import Hosts
from viper.task import Task, TaskRunner


def make_command(host):
    return ("echo", host.ip)


def process_stdout(out):
    return f"output: {out}"


def process_stderr(err):
    return f"error: {err}"


def test_tasks_runner():
    host = Host("1.1.1.1")
    hosts = Hosts.from_items(host)
    task = Task(
        "print IP address",
        command_factory=make_command,
        stdout_processor=process_stdout,
        stderr_processor=process_stderr,
    )

    tasks_runner = hosts.task(task)
    results = tasks_runner.run_in_sequence()

    runner = tasks_runner.first()
    result = results[0]

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
