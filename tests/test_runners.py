from viper import Host
from viper import Hosts
from viper import Runner
from viper import Task


def make_command(host):
    return ("echo", host.ip)


def process_stdout(out):
    return f"output: {out}"


def process_stderr(err):
    return f"error: {err}"


def pre_run(task):
    pass


def post_run(result):
    pass


def test_runners_hosts():
    hosts = Hosts.from_items(Host("1.1.1.1"), Host("2.2.2.2"))
    task = Task(
        "print IP address",
        command_factory=make_command,
        stdout_processor=process_stdout,
        stderr_processor=process_stderr,
        pre_run=pre_run,
        post_run=post_run,
    )

    runners = hosts.task(task)
    assert runners.hosts() == hosts


def test_runners_run_in_sequence():
    host = Host("1.1.1.1")
    hosts = Hosts.from_items(host)
    task = Task(
        "print IP address",
        command_factory=make_command,
        stdout_processor=process_stdout,
        stderr_processor=process_stderr,
    )

    runners = hosts.task(task)
    results = runners.run()

    runner = runners.all()[0]
    result = results.all()[0]

    assert runner == Runner(host, task)
    assert result.task == task
    assert result.host == host
    assert result.command == ("echo", "1.1.1.1")
    assert result.stdout == "output: 1.1.1.1\n"
    assert result.stderr == "error: "
    assert result.returncode == 0
    assert result.end > result.start
    assert result.ok()
    assert not result.errored()
    assert results.hosts() == hosts


def test_runners_run_in_parallel():
    host = Host("1.1.1.1")
    hosts = Hosts.from_items(host)
    task = Task(
        "print IP address",
        command_factory=make_command,
        stdout_processor=process_stdout,
        stderr_processor=process_stderr,
    )

    runners = hosts.task(task)
    results = runners.run(max_workers=5)

    runner = runners.all()[0]
    result = results.all()[0]

    assert runner == Runner(host, task)
    assert result.task == task
    assert result.host == host
    assert result.command == ("echo", "1.1.1.1")
    assert result.stdout == "output: 1.1.1.1\n"
    assert result.stderr == "error: "
    assert result.returncode == 0
    assert result.end > result.start
    assert result.ok()
    assert not result.errored()
    assert results.hosts() == hosts
