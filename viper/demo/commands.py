from viper import Host

import typing as t


def _ssh_command(host: Host, command: str) -> t.Sequence[str]:
    """Basic SSH command generator."""
    return (
        "ssh",
        "-l",
        host.login_name,
        "-i",
        host.identity_file,
        "-o",
        "StrictHostKeyChecking=no",
        host.ip,
        command,
    )


def ping_command(host: Host) -> t.Sequence[str]:
    """Basic ping command."""
    return "ping", "-c", "1", host.ip


def df_command(host: Host) -> t.Sequence[str]:
    """dh -lh command."""
    return _ssh_command(host, "df -lh")
