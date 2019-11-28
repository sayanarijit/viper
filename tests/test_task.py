import json

from viper.host import Host
from viper.task import Task, TaskResult, TaskRunner


def make_echo_command(host):
    return ("echo", host.ip)


def make_failing_command(host):
    return ("false",)


def process_stdout(out):
    return f"output: {out}"


def process_stderr(err):
    return f"error: {err}"


def test_task_to_json():
    task = Task(
        "print IP address",
        command_factory=make_echo_command,
        stdout_processor=process_stdout,
        stderr_processor=process_stderr,
    )

    assert task.to_json() == json.dumps(
        {
            "name": "print IP address",
            "command_factory": "test_task.make_echo_command",
            "timeout": None,
            "retry": 0,
            "stdout_processor": "test_task.process_stdout",
            "stderr_processor": "test_task.process_stderr",
        }
    )


def test_task_from_json():
    task = Task(
        "print IP address",
        command_factory=make_echo_command,
        stdout_processor=process_stdout,
        stderr_processor=process_stderr,
    )

    task_json = Task.from_json(
        json.dumps(
            {
                "name": "print IP address",
                "command_factory": "test_task.make_echo_command",
                "timeout": None,
                "stdout_processor": "test_task.process_stdout",
                "stderr_processor": "test_task.process_stderr",
            }
        )
    )

    assert task == task_json


def test_task_result_to_from_json():
    result = TaskResult(
        task=Task("print IP address", command_factory=make_echo_command),
        host=Host("1.1.1.1"),
        command=("foo",),
        stdout="out",
        stderr="err",
        returncode=0,
        start=1.1,
        end=1.2,
        retry=0,
    )

    result_json = json.dumps(
        {
            "task": {
                "name": "print IP address",
                "command_factory": "test_task.make_echo_command",
                "timeout": None,
                "retry": 0,
                "stdout_processor": None,
                "stderr_processor": None,
            },
            "host": {
                "ip": "1.1.1.1",
                "hostname": None,
                "domain": None,
                "port": 22,
                "login_name": None,
                "identity_file": None,
            },
            "command": ("foo",),
            "stdout": "out",
            "stderr": "err",
            "returncode": 0,
            "start": 1.1,
            "end": 1.2,
            "retry": 0,
        }
    )

    assert result_json == result.to_json()
    assert TaskResult.from_json(result_json) == result


def test_task_runner_to_from_json():
    runner = TaskRunner(
        task=Task("print IP address", command_factory=make_echo_command),
        host=Host("1.1.1.1"),
    )

    runner_json = json.dumps(
        {
            "host": {
                "ip": "1.1.1.1",
                "hostname": None,
                "domain": None,
                "port": 22,
                "login_name": None,
                "identity_file": None,
            },
            "task": {
                "name": "print IP address",
                "command_factory": "test_task.make_echo_command",
                "timeout": None,
                "retry": 0,
                "stdout_processor": None,
                "stderr_processor": None,
            },
        }
    )

    assert runner.to_json() == runner_json
    assert TaskRunner.from_json(runner_json) == runner


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
