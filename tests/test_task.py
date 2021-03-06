from viper import Host
from viper import Runner
from viper import Task

import json
import pytest


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
            "command_factory": "tests.test_task.make_echo_command",
            "timeout": None,
            "retry": 0,
            "stdout_processor": "tests.test_task.process_stdout",
            "stderr_processor": "tests.test_task.process_stderr",
            "pre_run": None,
            "post_run": None,
            "meta": {},
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
                "command_factory": "tests.test_task.make_echo_command",
                "timeout": None,
                "stdout_processor": "tests.test_task.process_stdout",
                "stderr_processor": "tests.test_task.process_stderr",
                "pre_run": None,
                "post_run": None,
            }
        )
    )

    assert task == task_json

    with pytest.raises(ValueError) as e:
        Task.from_json("{}")

    assert "value is required" in str(e.__dict__)


def test_runner_to_from_json():
    runner = Runner(
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
                "meta": {},
            },
            "task": {
                "name": "print IP address",
                "command_factory": "tests.test_task.make_echo_command",
                "timeout": None,
                "retry": 0,
                "stdout_processor": None,
                "stderr_processor": None,
                "pre_run": None,
                "post_run": None,
                "meta": {},
            },
            "args": [],
        }
    )

    assert runner.to_json() == runner_json
    assert Runner.from_json(runner_json) == runner

    with pytest.raises(ValueError):
        Task.from_json('{"name": "foo", "command_factory": "foo"}')
