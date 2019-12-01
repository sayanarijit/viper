from viper import Host
from viper import Hosts


def group1() -> Hosts:
    """Just a group of hosts."""

    return Hosts.from_items(
        Host("127.0.0.1"),
        Host("1.1.1.1"),
        Host("2.2.2.2"),
        Host("8.8.8.8"),
        Host(
            ip="::1",
            hostname="localhost",
            domain="localdomain",
            port=22,
            login_name="root",
            identity_file="/root/.ssh/id_rsa.pub",
        ),
    )
