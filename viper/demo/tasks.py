from viper import Host
from viper import Task
from viper.demo.callbacks import log_command
from viper.demo.callbacks import log_status

import typing as t


def ping_command(host: Host) -> t.Sequence[str]:
    return ("ping", "-c", "1", host.ip)


def ping() -> Task:
    return Task(
        "Ping",
        ping_command,
        timeout=5,
        retry=1,
        pre_run=log_command,
        post_run=log_status,
    )
