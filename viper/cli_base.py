"""Base classes for the viper.cli module."""

from argparse import _SubParsersAction
from argparse import ArgumentParser
from argparse import Namespace

import typing as t

__all__ = ["SubCommand"]


class SubCommand:
    """Base class for the subcommand parsers."""

    name: t.Optional[str] = None

    aliases: t.Sequence[str] = ()

    @classmethod
    def attach_to(cls, subparsers: _SubParsersAction) -> None:

        if not cls.name:
            raise NotImplementedError()  # no cover

        subparser = subparsers.add_parser(cls.name, help=cls.__doc__)
        if cls.aliases:
            for alias in cls.aliases:
                cls(subparsers.add_parser(alias, help=f"alias of {repr(cls.name)}"))
        cls(subparser)

    def __init__(self, subparser: ArgumentParser) -> None:
        self.add_arguments(subparser)
        subparser.set_defaults(_handler=self)
        subparser.add_argument(
            "--debug",
            action="store_true",
            help="show traceback information when an exception is raised",
        )

    def add_arguments(self, parser: ArgumentParser) -> None:
        raise NotImplementedError()  # no cover

    def __call__(self, args: Namespace) -> int:
        raise NotImplementedError()  # no cover
