"""Viper Object Serializers
~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains various loaders that helps loading viper collection
objects (such as Hosts, Task etc.) from a file, and also dumpers that helps
dump tha same to a file.
"""

from __future__ import annotations
from collections import namedtuple
from enum import Enum
from json import dumps
from json import JSONDecodeError
from json import load
from json import loads

import typing as t

__all__ = ["Serializers"]

T = t.TypeVar("T")


def _load_json(jsonobj: t.Union[str, t.TextIO]) -> t.Any:
    if isinstance(jsonobj, str):

        return loads(jsonobj)

    return load(jsonobj)


def _dump_json(data: object, fileobj: t.Optional[t.TextIO] = None) -> str:

    json = dumps(data, indent=4)
    if fileobj is not None:
        fileobj.write(json)
        fileobj.flush()
    return json


def _json_or_literal(val: object) -> object:
    if isinstance(val, str):
        try:
            return loads(val)
        except (JSONDecodeError, TypeError):
            pass
    return val


def _load_csv(txtobj: t.Union[str, t.TextIO]) -> t.List[t.Dict[str, object]]:
    from csv import DictReader

    if isinstance(txtobj, str):
        from io import StringIO

        txtobj = StringIO(txtobj)

    rows = DictReader(txtobj)
    return [{k: _json_or_literal(v) for k, v in row.items()} for row in rows]


def _dump_csv(
    data: t.Sequence[t.Dict[str, object]], fileobj: t.Optional[t.TextIO] = None
) -> str:
    from csv import writer
    from io import StringIO

    out = StringIO()

    target = writer(out)
    target.writerow(data[0].keys())
    for dict_ in data:
        target.writerow(list(map(dumps, dict_.values())))
    if fileobj is not None:
        fileobj.write(out.getvalue())
        fileobj.flush()
    return out.getvalue()


def _load_yaml(yamlobj: t.Union[str, t.TextIO]) -> t.Any:
    from yaml import safe_load

    return safe_load(yamlobj)


def _dump_yaml(data: object, fileobj: t.Optional[t.TextIO] = None) -> str:
    from yaml import safe_dump

    yaml: str = safe_dump(data, default_flow_style=False)
    if fileobj is not None:
        fileobj.write(yaml)
        fileobj.flush()
    return yaml


Serializer = namedtuple("Serializer", ("load", "dump"))


class Serializers(Enum):
    """A list of serializers to help loading and dumping objects
    from or to a file.
    """

    json = Serializer(load=_load_json, dump=_dump_json)
    csv = Serializer(load=_load_csv, dump=_dump_csv)
    yml = Serializer(load=_load_yaml, dump=_dump_yaml)
