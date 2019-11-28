from viper import Host, Task
import typing as t


def ping_command(host: Host) -> t.Sequence[str]:
    return ("ping", "-c", "1", host.ip)


# Run with `viper hosts:from_file [filepath] | viper task viper.demo.tasks.ping - | viper run -i 4 -`
ping = Task("Ping", ping_command, timeout=5, retry=1)
