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
from dataclasses import dataclass
from dataclasses import field
from viper.cli_base import SubCommand
from viper.collections import Collection as ViperCollection
from viper.collections import Hosts
from viper.collections import Items
from viper.collections import Results

import typing as t

ArgType = t.Tuple[t.Sequence[str], t.Dict[str, object]]


def arg(*args: str, **kwargs: object) -> ArgType:
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
    action_commands: t.List[SubCommand] = field(default_factory=lambda: [])
    hostgroup_commands: t.List[SubCommand] = field(default_factory=lambda: [])
    filter_commands: t.List[SubCommand] = field(default_factory=lambda: [])
    handler_commands: t.List[SubCommand] = field(default_factory=lambda: [])
    job_commands: t.List[SubCommand] = field(default_factory=lambda: [])

    def all_commands(self) -> t.List[SubCommand]:
        """Return all sub commands"""
        return (
            self.action_commands
            + self.hostgroup_commands
            + self.filter_commands
            + self.handler_commands
            + self.job_commands
        )

    def hostgroup(self, args: t.Optional[t.Sequence[ArgType]] = None) -> Hosts:
        """Use this decorator to define host groups

        :param list args (optional): Arguments to be parsed by py:class:`argparse.ArgumentParser`

        .. tip:: See :py:func:`viper.demo.viperfile.allhosts`.
        """

        def wrapper(
            func: t.Callable[[Namespace], Hosts]
        ) -> t.Callable[[Namespace], Hosts]:

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

    def filter(
        self, objtype: t.Type[Items], args: t.Optional[t.Sequence[ArgType]] = None
    ):
        """Use this decorator to define filters.

        :param type objtype: The object type that the filter is expecting.
        :param list args (optional): List of arguments for :py:class:`argparse.ArgumentParser`.

        .. tip:: See :py:func:`viper.demo.viperfile.hosts_by`.
        """

        if not issubclass(objtype, Items):
            raise ValueError(f"{objtype} does not have filter option")

        def wrapper(
            func: t.Callable[[Items, Namespace], bool],
        ) -> t.Callable[[Items, Namespace], bool]:

            doc = func.__doc__.splitlines()[0] if func.__doc__ else ""

            class FilterCommand(SubCommand):
                __doc__ = f"[{objtype.__name__} -> {objtype.__name__}] {doc}"
                name = f"@{self.prefix}:{func.__name__}"

                def add_arguments(self, parser: ArgumentParser) -> None:
                    if args:
                        for arg in args:
                            parser.add_argument(*arg[0], **arg[1])
                    parser.add_argument("-i", "--indent", type=int, default=None)

                def __call__(self, args: Namespace) -> int:
                    print(
                        objtype.from_json(input())
                        .filter(lambda host: func(host, args))
                        .to_json(indent=args.indent)
                    )
                    return 0

            self.filter_commands.append(FilterCommand)
            return func

        return wrapper

    def handler(
        self,
        fromtype: ViperCollection,
        totype: t.Optional[type] = None,
        args: t.Optional[t.Sequence[ArgType]] = None,
    ):
        """Use this decorator to define handlers

        :param type fromtype: The type of object this handler is expecting.
        :param type totype: The type of object this handler returns.
        :param list args (optional): List of arguments for :py:class:`argparse.ArgumentParser`.

        .. tip:: See :py:func:`viper.demo.viperfile.results2csv`.
        """

        if not issubclass(fromtype, ViperCollection):
            raise ValueError(f"{fromtype} does not have pipe option")

        def wrapper(
            func: t.Callable[[ViperCollection, Namespace], object]
        ) -> t.Callable[[ViperCollection, Namespace], object]:

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
        self, args: t.Optional[t.Sequence[ArgType]] = None,
    ):
        """Use this decorator to define a job.

        :param list args (optional): List of arguments for :py:class:`argparse.ArgumentParser`.

        .. tip:: See :py:func:`viper.demo.viperfile.remote_exec`.
        """

        def wrapper(
            func: t.Callable[[ViperCollection, Namespace], Results]
        ) -> t.Callable[[ViperCollection, Namespace], Results]:

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
        self, args: t.Optional[t.Sequence[ArgType]] = None,
    ):
        """Use this decorator to define an action.

        :param list args (optional): List of arguments for :py:class:`argparse.ArgumentParser`.

        .. tip:: See :py:func:`viper.demo.viperfile.get_triggers`.
        """

        def wrapper(
            func: t.Callable[[Namespace], object]
        ) -> t.Callable[[Namespace], object]:

            doc = func.__doc__.splitlines()[0] if func.__doc__ else ""

            class ActionCommand(SubCommand):
                __doc__ = f"{doc}"
                name = f"@{self.prefix}:{func.__name__}"

                def add_arguments(self, parser: ArgumentParser) -> None:
                    if args:
                        for arg in args:
                            parser.add_argument(*arg[0], **arg[1])

                def __call__(self, args: Namespace) -> int:
                    res = func(args)
                    if res is not None:
                        print(
                            "\n".join(map(str, res)) if isinstance(res, tuple) else res
                        )
                    return 0

            self.action_commands.append(ActionCommand)
            return func

        return wrapper
