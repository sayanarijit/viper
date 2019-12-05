"""Viper Demo Host loaders
~~~~~~~~~~~~~~~~~~~~~~~~~~
These loaders are used with :py:meth:`viper.collections.Hosts.from_file`
to generate a `viper.collections.Hosts` object.


Viper Host Loader Definition Structure
--------------------------------------

.. code-block:: python

    def loader_name(f: typing.TextIO) -> Hosts:

        data = somefunction(f)

        return Hosts.from_list(data)

See :py:func:`viper.demo.loaders.json` for example.
"""

from viper import Hosts

import typing as t


def json(f: t.TextIO) -> Hosts:

    return Hosts.from_json(f.read())
