'''Viper Host Groups Demo
~~~~~~~~~~~~~~~~~~~~~~~~~
A host group is a function that produces an instance of :py:class:`viper.collections.Hosts`.


.. tip:: See :py:class:`viper.collections.Host` for more details.


Viper Host Group Definition Structure
-------------------------------------
Here's an example of a viper host group definition.

.. code-block:: python

    def group1() -> Hosts:
        """Just a group of hosts."""

        return Hosts.from_items(
            Host("1.2.3.4"),
        )
'''

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
