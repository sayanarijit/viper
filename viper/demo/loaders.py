import typing as t
from json import loads as loadjson

from viper import Hosts
from viper.demo import __doc__


def json(f: t.TextIO) -> Hosts:

    return Hosts.from_json(f.read())
