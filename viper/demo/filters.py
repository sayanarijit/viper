from viper import Host


def no_hostname(host: Host) -> bool:
    """Show hosts with no hostname."""
    return not host.hostname


def has_hostname(host: Host) -> bool:
    """Show hosts with hostname set."""
    return bool(host.hostname)


def no_login_name(host: Host) -> bool:
    """Show hosts with no login_name."""
    return not host.login_name


def has_login_name(host: Host) -> bool:
    """Show hosts with login_name set."""
    return bool(host.login_name)
