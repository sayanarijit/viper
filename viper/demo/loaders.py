from viper import Hosts

import typing as t


def json(f: t.TextIO) -> Hosts:

    return Hosts.from_json(f.read())
