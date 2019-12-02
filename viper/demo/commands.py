from viper import Host

import typing as t


def ping_command(host: Host) -> t.Sequence[str]:
    """Basic ping command."""
    return "ping", "-c", "1", host.ip


def remote_execute_command(host: Host, command: str) -> t.Sequence[str]:
    """Basic SSH command generator."""

    if not host.login_name:
        raise ValueError(f"{host}: 'login_name' is not set")

    if not host.identity_file:
        raise ValueError(f"{host}: 'identity_file' is not set")

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


def df_command(host: Host) -> t.Sequence[str]:
    """Get the local disk usage"""
    return remote_execute_command(host, "df -lh")
