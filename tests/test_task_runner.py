from unittest import mock

from viper import Host, Task, TaskResult, TaskRunner


def make_echo_command(host):
    return ("echo", host.ip)


def make_failing_command(host):
    return ("false",)


def process_stdout(out):
    return f"output: {out}"


def process_stderr(err):
    return f"error: {err}"


def test_task_runner_run_save_load():
    host = Host("1.1.1.1")
    task = Task(
        "print IP address",
        command_factory=make_echo_command,
        stdout_processor=process_stdout,
        stderr_processor=process_stderr,
    )

    runner = host.task(task)

    result = runner.run()

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
    assert TaskResult.from_hash(hash(result)) == result


def test_tasks_runner_retry():
    host = Host("1.1.1.1")
    task = Task("Fail", command_factory=make_failing_command, retry=3)

    assert host.task(task).run().retry == 3


@mock.patch("viper.task_runner._task_results.TaskResults")
def test_task_runner_task_results(TaskResults):
    host = mock.Mock()
    task = mock.Mock()

    runner = TaskRunner(host=host, task=task)
    runner.task_results()
    TaskResults.by_task_runner.assert_called_with(runner)
