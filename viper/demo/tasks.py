from viper import Host
from viper import Task
from viper.demo import __doc__

import typing as t

__doc__ = __doc__


def ping_command(host: Host) -> t.Sequence[str]:
    return ("ping", "-c", "1", host.ip)


def ping() -> Task:
    return Task("Ping", ping_command, timeout=5, retry=1)
