from viper import Host, TaskResult
from viper.demo import __doc__


def ip_starts_with_2(host: Host) -> bool:
    """Filter hosts IPs that start with 2."""
    return host.ip.startswith("2")


def result_ok(result: TaskResult) -> bool:
    """Filter task results by OK status."""
    return result.ok()


def result_errored(result: TaskResult) -> bool:
    """Filter task results by error status."""
    return result.errored()
