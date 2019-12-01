from viper import Host
from viper import Result


def ip_is(host: Host, ip: str) -> bool:
    """Filter a host by IP address."""
    return host.ip == ip


def result_ok(result: Result) -> bool:
    """Filter results by OK status."""
    return result.ok()


def result_errored(result: Result) -> bool:
    """Filter results by error status."""
    return result.errored()
