from viper import Host
from viper.demo import __doc__

__doc__ = __doc__


def by_ip(host: Host) -> object:
    """Sort by IP"""
    return host.ip
