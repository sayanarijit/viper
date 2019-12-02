from viper import Result
from viper import Runner

import sys


def log_command(runner: Runner) -> None:
    """Log the command before run."""
    command = runner.task.command_factory(runner.host, *runner.args)
    print(runner.host.ip, command, file=sys.stderr, sep=": ")


def log_status(result: Result) -> None:
    """Log the status after task run."""

    if result.ok():
        print(result.host.ip, "OK", file=sys.stderr, sep=": ")
        return

    print(result.host.ip, "FAILED", file=sys.stderr, sep=": ")
