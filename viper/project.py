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
from viper.collections import Item
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

    def filter(self, objclass: type, args: t.Optional[t.Sequence[Arg]] = None):
        """Use this decorator to define filters."""

        if not issubclass(objclass, Items):
            raise ValueError(f"{objclass} does not have filter option")

        def wrapper(func):
            class FilterCommand(SubCommand):
                name = f"@{self.prefix}:{func.__name__}"
                __doc__ = f"[{objclass.__name__} > @{self.prefix}:{func.__name__} > {objclass.__name__}] {func.__doc__}"

                def add_arguments(self, parser):
                    if args:
                        for arg in args:
                            parser.add_argument(*arg.args, **arg.kwargs)

                def __call__(self, args):
                    print(
                        objclass.from_json(input())
                        .filter(lambda host: func(args, host))
                        .to_json()
                    )
                    return 0

            self.filter_commands.append(FilterCommand)
            return func

        return wrapper

    def handler(
        self, fromclass: type, toclass: type, args: t.Optional[t.Sequence[Arg]] = None
    ):
        """Use this decorator to define handlers."""

        if not issubclass(fromclass, Item) and not issubclass(fromclass, Items):
            raise ValueError(f"{fromclass} does not have pipe option")

        def wrapper(func):
            class HandlerCommand(SubCommand):
                name = f"@{self.prefix}:{func.__name__}"
                __doc__ = f"[{fromclass.__name__} > @{self.prefix}:{func.__name__} > {toclass.__name__}] {func.__doc__}"

                def add_arguments(self, parser):
                    if args:
                        for arg in args:
                            parser.add_argument(*arg.args, **arg.kwargs)

                def __call__(self, args):
                    fromclass.from_json(input()).pipe(lambda hosts: func(args, hosts))
                    return 0

            self.handler_commands.append(HandlerCommand)
            return func

        return wrapper

    def job(
        self, fromclass: type, toclass: type, args: t.Optional[t.Sequence[Arg]] = None
    ):
        """Use this decorator to define job."""

        if not issubclass(fromclass, Item) and not issubclass(fromclass, Items):
            raise ValueError(f"{fromclass} is not a valid input for any job")

        def wrapper(func):
            class WorkFlowCommand(SubCommand):
                name = f"@{self.prefix}:{func.__name__}"
                __doc__ = f"[{fromclass.__name__} > @{self.prefix}:{func.__name__} > {toclass.__name__}] {func.__doc__}"

                def add_arguments(self, parser):
                    if args:
                        for arg in args:
                            parser.add_argument(*arg.args, **arg.kwargs)

                def __call__(self, args):
                    func(args, fromclass.from_json(input()))
                    return 0

            self.job_commands.append(WorkFlowCommand)
            return func

        return wrapper
