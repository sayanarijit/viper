from viper import Host
from viper import Result
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


def test_result_to_from_json():
    result = Result(
        trigger_time=1.0,
        task=Task("print IP address", command_factory=make_echo_command),
        host=Host("1.1.1.1"),
        args=("bar",),
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
            "trigger_time": 1.0,
            "task": {
                "name": "print IP address",
                "command_factory": "tests.test_result.make_echo_command",
                "timeout": None,
                "retry": 0,
                "stdout_processor": None,
                "stderr_processor": None,
                "pre_run": None,
                "post_run": None,
                "meta": {},
            },
            "host": {
                "ip": "1.1.1.1",
                "hostname": None,
                "domain": None,
                "port": 22,
                "login_name": None,
                "identity_file": None,
                "meta": {},
            },
            "args": ["bar"],
            "command": ["foo"],
            "stdout": "out",
            "stderr": "err",
            "returncode": 0,
            "start": 1.1,
            "end": 1.2,
            "retry": 0,
        }
    )

    assert result_json == result.to_json()
    assert Result.from_json(result_json) == result

    with pytest.raises(ValueError) as e:
        Result.from_dict({})

    assert "value is required" in str(e.__dict__)
