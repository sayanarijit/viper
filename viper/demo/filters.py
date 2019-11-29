from viper import Host
from viper.demo import __doc__


def ip_starts_with_2(host: Host) -> bool:
    """Show hosts with no hostname."""
    return host.ip.startswith("2")
