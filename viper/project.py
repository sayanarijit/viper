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
from dataclasses import dataclass
from dataclasses import field
from viper.cli_base import SubCommand
from viper.collections import Collection as ViperCollection
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

        def wrapper(func):
            class HostGroupCommand(SubCommand):
                name = f"@{self.prefix}:{func.__name__}"
                __doc__ = f"[@{self.prefix}:{func.__name__} > Hosts] {func.__doc__}"

                def add_arguments(self, parser):
                    if args:
                        for arg in args:
                            parser.add_argument(*arg.args, **arg.kwargs)

                def __call__(self, args):
                    print(func(args).to_json())
                    return 0

            self.hostgroup_commands.append(HostGroupCommand)
            return func

        return wrapper

    def filter(self, objtype: type, args: t.Optional[t.Sequence[Arg]] = None):
        """Use this decorator to define filters."""

        if not issubclass(objtype, Items):
            raise ValueError(f"{objtype} does not have filter option")

        def wrapper(func):
            class FilterCommand(SubCommand):
                name = f"@{self.prefix}:{func.__name__}"
                __doc__ = f"[{objtype.__name__} > @{self.prefix}:{func.__name__} > {objtype.__name__}] {func.__doc__}"

                def add_arguments(self, parser):
                    if args:
                        for arg in args:
                            parser.add_argument(*arg.args, **arg.kwargs)

                def __call__(self, args):
                    print(
                        objtype.from_json(input())
                        .filter(lambda host: func(args, host))
                        .to_json()
                    )
                    return 0

            self.filter_commands.append(FilterCommand)
            return func

        return wrapper

    def handler(
        self,
        fromtype: type,
        totype: t.Optional[type] = None,
        args: t.Optional[t.Sequence[Arg]] = None,
    ):
        """Use this decorator to define handlers."""

        if not issubclass(fromtype, ViperCollection):
            raise ValueError(f"{fromtype} does not have pipe option")

        def wrapper(func):
            class HandlerCommand(SubCommand):
                name = f"@{self.prefix}:{func.__name__}"
                __doc__ = f"[{fromtype.__name__} > @{self.prefix}:{func.__name__} > {totype.__name__}] {func.__doc__}"

                def add_arguments(self, parser):
                    if args:
                        for arg in args:
                            parser.add_argument(*arg.args, **arg.kwargs)

                def __call__(self, args):
                    r = fromtype.from_json(input()).pipe(
                        lambda hosts: func(args, hosts)
                    )
                    if totype:
                        print(
                            r.to_json()
                            if issubclass(totype, ViperCollection)
                            else totype(r)
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

        if not issubclass(fromtype, ViperCollection):
            raise ValueError(f"{fromtype} is not a valid input for any job")

        def wrapper(func):
            class WorkFlowCommand(SubCommand):
                name = f"@{self.prefix}:{func.__name__}"
                __doc__ = f"[{fromtype.__name__} > @{self.prefix}:{func.__name__} > {totype.__name__}] {func.__doc__}"

                def add_arguments(self, parser):
                    if args:
                        for arg in args:
                            parser.add_argument(*arg.args, **arg.kwargs)

                def __call__(self, args):
                    if totype:
                        r = func(args, fromtype.from_json(input()))
                        print(
                            r.to_json()
                            if issubclass(totype, ViperCollection)
                            else totype(r)
                        )
                    return 0

            self.job_commands.append(WorkFlowCommand)
            return func

        return wrapper
