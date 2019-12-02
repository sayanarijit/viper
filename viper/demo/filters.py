from viper import Host
from viper import Hosts
from viper import Result
from viper import Results
from viper import Runners

import typing as t


def ip_is(host: Host, ip: str) -> bool:
    """Filter a host by IP address."""
    return host.ip == ip


def result_ok(result: Result) -> bool:
    """Filter results by OK status."""
    return result.ok()


def result_errored(result: Result) -> bool:
    """Filter results by error status."""
    return result.errored()


def exact(obj: t.Union[Hosts, Runners, Results], key: str, val: str) -> bool:
    """A generic filter for all items."""
    return hasattr(obj, key) and str(getattr(obj, key)) == val


def contains(obj: t.Union[Hosts, Runners, Results], key: str, val: str) -> bool:
    """A generic filter for all items."""
    return hasattr(obj, key) and val in str(getattr(obj, key))


def startswith(obj: t.Union[Hosts, Runners, Results], key: str, val: str) -> bool:
    """A generic filter for all items."""
    return hasattr(obj, key) and str(getattr(obj, key)).startswith(val)


def endswith(obj: t.Union[Hosts, Runners, Results], key: str, val: str) -> bool:
    """A generic filter for all items."""
    return hasattr(obj, key) and str(getattr(obj, key)).endsswith(val)
