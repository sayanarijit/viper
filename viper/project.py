"""Viper Project APIs (the ``viperfile.py``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Viper provides APIs for customizing the viper CLI based on the project
requirement. When viper detects a ``viperfile.py`` file in the current
working directory, it scans that file and adds the project specific
commands and options to it's own list.

We can see the commands by running ``viper --help``. These commands are
prefixed with ``@`` so that they are easily recognizable.


After defining this in ``viperfile.py`` we can use commands like ``viper @myproj:allhosts``
(example) to get the list of hosts which can be piped to other commands that recieves
a list of hosts from `stdin`.


.. tip:: See :py:mod:`viper.demo.viperfile` for the full project example.
"""


from __future__ import annotations
from argparse import ArgumentParser
from argparse import Namespace
from collections.abc import Iterable
from dataclasses import dataclass
from dataclasses import field
from viper.cli_base import SubCommand
from viper.collections import Collection as ViperCollection
from viper.collections import Hosts
from viper.collections import Results

import typing as t

T = t.TypeVar("T")
C = t.TypeVar("C")
ArgType = t.Tuple[t.Tuple[str, ...], t.Dict[str, t.Any]]
HostsFuncType = t.Callable[[Namespace], Hosts]
HandlerFuncType = t.Callable[[T, Namespace], C]
JobFuncType = t.Callable[[Hosts, Namespace], Results]
ActionFuncType = t.Callable[[Namespace], T]


def arg(*args: str, **kwargs: t.Any) -> ArgType:
    """Argumenst to be passed to argparse"""
    return args, kwargs


@dataclass
class Project:
    """A project (namespace) for the viper sub commands

    :param str prefix: Prefix for the related sub commands.

    When we define a project, we basically define a namespace (a prefix)
    for the commands.

    .. tip:: See :py:mod:`viper.demo.viperfile`
    """

    prefix: str
    action_commands: t.List[t.Type[SubCommand]] = field(default_factory=lambda: [])
    hostgroup_commands: t.List[t.Type[SubCommand]] = field(default_factory=lambda: [])
    filter_commands: t.List[t.Type[SubCommand]] = field(default_factory=lambda: [])
    handler_commands: t.List[t.Type[SubCommand]] = field(default_factory=lambda: [])
    job_commands: t.List[t.Type[SubCommand]] = field(default_factory=lambda: [])

    def all_commands(self) -> t.List[t.Type[SubCommand]]:
        """Return all sub commands"""
        return (
            self.action_commands
            + self.hostgroup_commands
            + self.filter_commands
            + self.handler_commands
            + self.job_commands
        )

    def hostgroup(
        self, args: t.Optional[t.Sequence[ArgType]] = None
    ) -> t.Callable[[HostsFuncType], HostsFuncType]:
        """Use this decorator to define host groups

        :param list args (optional): Arguments to be parsed by py:class:`argparse.ArgumentParser`

        .. tip:: See :py:func:`viper.demo.viperfile.allhosts`.
        """

        def wrapper(func: HostsFuncType) -> HostsFuncType:

            doc = func.__doc__.splitlines()[0] if func.__doc__ else ""

            class HostGroupCommand(SubCommand):
                __doc__ = f"[-> Hosts] {doc}"
                name = f"@{self.prefix}:{func.__name__}"

                def add_arguments(self, parser: ArgumentParser) -> None:
                    if args:
                        for arg in args:
                            parser.add_argument(*arg[0], **arg[1])
                    parser.add_argument("-i", "--indent", type=int, default=None)

                def __call__(self, args: Namespace) -> int:
                    print(func(args).to_json(indent=args.indent))
                    return 0

            self.hostgroup_commands.append(HostGroupCommand)
            return func

        return wrapper

    def handler(
        self,
        fromtype: type,
        totype: type,
        args: t.Optional[t.Sequence[ArgType]] = None,
    ) -> t.Callable[[HandlerFuncType[T, C]], HandlerFuncType[T, C]]:
        """Use this decorator to define handlers

        :param type fromtype: The type of object this handler is expecting.
        :param type totype: The type of object this handler returns.
        :param list args (optional): List of arguments for :py:class:`argparse.ArgumentParser`.

        .. tip:: See :py:func:`viper.demo.viperfile.results2csv`.
        """

        if not issubclass(fromtype, ViperCollection):
            raise ValueError(f"{fromtype} does not have pipe option")

        def wrapper(func: HandlerFuncType[T, C]) -> HandlerFuncType[T, C]:

            doc = func.__doc__.splitlines()[0] if func.__doc__ else ""

            class HandlerCommand(SubCommand):
                __doc__ = f"[{fromtype.__name__} -> {totype.__name__}] {doc}"
                name = f"@{self.prefix}:{func.__name__}"

                def add_arguments(self, parser: ArgumentParser) -> None:
                    if args:
                        for arg in args:
                            parser.add_argument(*arg[0], **arg[1])
                    parser.add_argument("-i", "--indent", type=int, default=None)

                def __call__(self, args: Namespace) -> int:
                    if not issubclass(fromtype, ViperCollection):
                        raise ValueError(f"{fromtype}: invalid fromtype")

                    obj: C = fromtype.from_json(input()).pipe(
                        lambda obj: func(obj, args)
                    )
                    if not isinstance(obj, totype):
                        raise ValueError(
                            f"invalid totype, expected {totype} but got {type(obj)}"
                        )

                    if isinstance(obj, ViperCollection):
                        print(obj.to_json(indent=args.indent))
                    else:
                        print(obj)

                    return 0

            self.handler_commands.append(HandlerCommand)
            return func

        return wrapper

    def job(
        self, args: t.Optional[t.Sequence[ArgType]] = None,
    ) -> t.Callable[[JobFuncType], JobFuncType]:
        """Use this decorator to define a job.

        :param list args (optional): List of arguments for :py:class:`argparse.ArgumentParser`.

        .. tip:: See :py:func:`viper.demo.viperfile.remote_exec`.
        """

        def wrapper(func: JobFuncType) -> JobFuncType:

            doc = func.__doc__.splitlines()[0] if func.__doc__ else ""

            class JobCommand(SubCommand):
                __doc__ = f"[Hosts -> Results] {doc}"
                name = f"@{self.prefix}:{func.__name__}"

                def add_arguments(self, parser: ArgumentParser) -> None:
                    if args:
                        for arg in args:
                            parser.add_argument(*arg[0], **arg[1])
                    parser.add_argument("-i", "--indent", type=int, default=None)

                def __call__(self, args: Namespace) -> int:
                    results = func(Hosts.from_json(input()), args)
                    if not isinstance(results, Results):
                        raise ValueError(
                            f"a job must return {Results} object but got {type(results)}"
                        )
                    print(results.to_json(indent=args.indent))
                    return 0

            self.job_commands.append(JobCommand)
            return func

        return wrapper

    def action(
        self,
        args: t.Optional[t.Sequence[ArgType]] = None,
        totype: t.Optional[type] = None,
    ) -> t.Callable[[ActionFuncType[T]], ActionFuncType[T]]:
        """Use this decorator to define an action.

        :param list args (optional): List of arguments for :py:class:`argparse.ArgumentParser`.

        .. tip:: See :py:func:`viper.demo.viperfile.get_triggers`.
        """

        def wrapper(func: ActionFuncType[T]) -> ActionFuncType[T]:

            doc = func.__doc__.splitlines()[0] if func.__doc__ else ""

            class ActionCommand(SubCommand):
                __doc__ = f"[-> totype.__name__] {doc}" if totype else doc
                name = f"@{self.prefix}:{func.__name__}"

                def add_arguments(self, parser: ArgumentParser) -> None:
                    if args:
                        for arg in args:
                            parser.add_argument(*arg[0], **arg[1])

                def __call__(self, args: Namespace) -> int:
                    res = func(args)
                    if res is None:
                        if totype is None:
                            return 0
                        else:
                            raise ValueError(f"expected an object of type {totype}")

                    if totype is None:
                        raise ValueError(
                            f"not expecting any result, but got a result of type {type(res)}"
                        )

                    if not isinstance(res, totype):
                        raise ValueError(
                            f"expected result of type {totype} but got result of type {type(res)}"
                        )

                    if isinstance(res, ViperCollection):
                        print(res.to_json())
                    elif isinstance(res, Iterable):
                        print("\n".join(map(str, res)))
                    else:
                        print(res)
                    return 0

            self.action_commands.append(ActionCommand)
            return func

        return wrapper
