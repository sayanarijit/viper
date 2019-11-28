import csv
import typing as t
from viper import Hosts


def basic_csv(f: t.TextIO) -> Hosts:
    r = csv.reader(f)
    rows = list(r)
    keys, values = rows[0], rows[1:]
    dicts = [dict(tuple(zip(keys, v))) for v in values]

    return Hosts.from_list(dicts)
