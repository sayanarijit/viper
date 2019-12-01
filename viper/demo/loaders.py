from viper import Hosts
from viper.demo import __doc__

import typing as t

__doc__ = __doc__


def json(f: t.TextIO) -> Hosts:

    return Hosts.from_json(f.read())
