from viper import Host, Task
import typing as t

from viper.demo import __doc__


def ping_command(host: Host) -> t.Sequence[str]:
    return ("ping", "-c", "1", host.ip)


ping = Task("Ping", ping_command, timeout=5, retry=1)
