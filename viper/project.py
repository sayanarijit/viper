"""Viper project APIs
---------------------
This module provides APIs for customizing viper based on any project
requirements. When viper detects a `viperfile.py` file in the current directory,
it scans the file and adds the project specific commands to it's list.

We can see the commands by running `viper --help`. These commands are
generally prefixed with `@` so that they are easily recognizable.

See `viper.demo.viperfile.py` for examples.
"""


from __future__ import annotations
from argparse import ArgumentParser
from argparse import Namespace
from dataclasses import dataclass
from dataclasses import field
from viper.cli_base import SubCommand
from viper.collections import Collection as ViperCollection
from viper.collections import Hosts
from viper.collections import Items

import typing as t


class Arg:
    """Args that can be passed to ArgumentParser"""

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


@dataclass
class Project:
    """A project namespace for the sub commands."""

    prefix: str
    hostgroup_commands: t.List[SubCommand] = field(default_factory=lambda: [])
    filter_commands: t.List[SubCommand] = field(default_factory=lambda: [])
    handler_commands: t.List[SubCommand] = field(default_factory=lambda: [])
    job_commands: t.List[SubCommand] = field(default_factory=lambda: [])

    def all_commands(self) -> t.List[SubCommand]:
        """Return all sub commands"""
        return (
            self.hostgroup_commands
            + self.filter_commands
            + self.handler_commands
            + self.job_commands
        )

    def hostgroup(self, args: t.Optional[t.Sequence[Arg]] = None):
        """Use this decorator to define host groups."""

        def wrapper(
            func: t.Callable[[Namespace], Hosts]
        ) -> t.Callable[[Namespace], Hosts]:

            doc = func.__doc__.splitlines()[0] if func.__doc__ else ""

            class HostGroupCommand(SubCommand):
                name = f"@{self.prefix}:{func.__name__}"
                __doc__ = f"[> Hosts] {doc}"

                def add_arguments(self, parser: ArgumentParser) -> None:
                    if args:
                        for arg in args:
                            parser.add_argument(*arg.args, **arg.kwargs)
                    parser.add_argument("-i", "--indent", type=int, default=None)

                def __call__(self, args: Namespace) -> int:
                    print(func(args).to_json(indent=args.indent))
                    return 0

            self.hostgroup_commands.append(HostGroupCommand)
            return func

        return wrapper

    def filter(self, objtype: t.Type[Items], args: t.Optional[t.Sequence[Arg]] = None):
        """Use this decorator to define filters."""

        if not issubclass(objtype, Items):
            raise ValueError(f"{objtype} does not have filter option")

        def wrapper(
            func: t.Callable[[Items, Namespace], bool],
        ) -> t.Callable[[Items, Namespace], bool]:

            doc = func.__doc__.splitlines()[0] if func.__doc__ else ""

            class FilterCommand(SubCommand):
                name = f"@{self.prefix}:{func.__name__}"
                __doc__ = f"[{objtype.__name__} > {objtype.__name__}] {doc}"

                def add_arguments(self, parser: ArgumentParser) -> None:
                    if args:
                        for arg in args:
                            parser.add_argument(*arg.args, **arg.kwargs)

                def __call__(self, args: Namespace) -> int:
                    print(
                        objtype.from_json(input())
                        .filter(lambda host: func(host, args))
                        .to_json()
                    )
                    return 0

            self.filter_commands.append(FilterCommand)
            return func

        return wrapper

    def handler(
        self,
        fromtype: ViperCollection,
        totype: t.Optional[type] = None,
        args: t.Optional[t.Sequence[Arg]] = None,
    ):
        """Use this decorator to define handlers."""

        if not issubclass(fromtype, ViperCollection):
            raise ValueError(f"{fromtype} does not have pipe option")

        def wrapper(
            func: t.Callable[[ViperCollection, Namespace], object]
        ) -> t.Callable[[ViperCollection, Namespace], object]:

            doc = func.__doc__.splitlines()[0] if func.__doc__ else ""

            class HandlerCommand(SubCommand):
                name = f"@{self.prefix}:{func.__name__}"
                __doc__ = f"[{fromtype.__name__} > {totype.__name__}] {doc}"

                def add_arguments(self, parser: ArgumentParser) -> None:
                    if args:
                        for arg in args:
                            parser.add_argument(*arg.args, **arg.kwargs)
                    parser.add_argument("-i", "--indent", type=int, default=None)

                def __call__(self, args: Namespace) -> int:
                    obj = fromtype.from_json(input()).pipe(lambda obj: func(obj, args))
                    if totype:
                        print(
                            obj.to_json(indent=args.indent)
                            if isinstance(obj, ViperCollection)
                            else totype(obj)
                        )
                    return 0

            self.handler_commands.append(HandlerCommand)
            return func

        return wrapper

    def job(
        self,
        fromtype: type,
        totype: t.Optional[type] = None,
        args: t.Optional[t.Sequence[Arg]] = None,
    ):
        """Use this decorator to define job."""

        def wrapper(
            func: t.Callable[[ViperCollection, Namespace], object]
        ) -> t.Callable[[ViperCollection, Namespace], object]:

            doc = func.__doc__.splitlines()[0] if func.__doc__ else ""

            class WorkFlowCommand(SubCommand):
                name = f"@{self.prefix}:{func.__name__}"
                __doc__ = f"[{fromtype.__name__} > {totype.__name__}] {doc}"

                def add_arguments(self, parser: ArgumentParser) -> None:
                    if args:
                        for arg in args:
                            parser.add_argument(*arg.args, **arg.kwargs)
                    parser.add_argument("-i", "--indent", type=int, default=None)

                def __call__(self, args: Namespace) -> int:
                    if issubclass(fromtype, ViperCollection):
                        data = fromtype.from_json(input())
                    else:
                        data = fromtype(input())

                    if totype:
                        obj = func(data, args)
                        print(
                            obj.to_json(indent=args.indent)
                            if isinstance(obj, ViperCollection)
                            else totype(obj)
                        )
                    return 0

            self.job_commands.append(WorkFlowCommand)
            return func

        return wrapper
