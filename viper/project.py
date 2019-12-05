"""Viper Project APIs (the ``viperfile.py``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module provides APIs for customizing viper based on any project
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

    :example:

    .. code-block:: python

        from argparse import Namespace
        from viper import Host, Hosts
        from viper.project import Project, arg

        import json

        myproj = Project(prefix="myproj")
    """

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

    def hostgroup(self, args: t.Optional[t.Sequence[ArgType]] = None) -> Hosts:
        '''Use this decorator to define host groups

        :param list args (optional): Arguments to be parsed by py:class:`argparse.ArgumentParser`

        :example:

        .. code-block:: python

            @myproj.hostgroup(
                args=[
                    arg("-f", "--file", type=FileType("r"), default="hosts.json"),
                    arg("-I", "--identity_file", default="/root/.ssh/id_rsa.pub"),
                ]
            )
            def allhosts(args: Namespace) -> Hosts:
                """get all hosts in myproj"""

                return Hosts.from_items(
                    *(
                        Host(
                            ip=d["ip"],
                            hostname=d["name"],
                            login_name="root",
                            identity_file=args.identity_file,
                            meta=tuple(d.items()),
                        )
                        for d in json.load(args.file)
                    )
                )


        We can print the command usage with

        .. code-block:: bash

            viper @myproj:allhosts --help

        .. tip:: See :py:func:`viper.demo.viperfile.allhosts`.
        '''

        def wrapper(
            func: t.Callable[[Namespace], Hosts]
        ) -> t.Callable[[Namespace], Hosts]:

            doc = func.__doc__.splitlines()[0] if func.__doc__ else ""

            class HostGroupCommand(SubCommand):
                name = f"@{self.prefix}:{func.__name__}"
                __doc__ = f"[-> Hosts] {doc}"

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
        '''Use this decorator to define filters.

        :param type objtype: The object type that the filter is expecting.
        :param list args (optional): List of arguments for :py:class:`argparse.ArgumentParser`.

        Custom project specific filters can be defined in the ``viperfile.py`` like below.

        .. code-block:: python

            @myproj.filter(objtype=Hosts, args=[arg("key"), arg("val")])
            def hosts_by(host: Host, args: Namespace) -> bool:
                """Filter hosts by key and metadata"""

                return str(dict(host.meta)[args.key]) == args.val

        We can print the command usage with

        .. code-block:: bash

            viper @myproj:hosts_by --help

        .. tip:: See :py:func:`viper.demo.viperfile.hosts_by`.
        '''

        if not issubclass(objtype, Items):
            raise ValueError(f"{objtype} does not have filter option")

        def wrapper(
            func: t.Callable[[Items, Namespace], bool],
        ) -> t.Callable[[Items, Namespace], bool]:

            doc = func.__doc__.splitlines()[0] if func.__doc__ else ""

            class FilterCommand(SubCommand):
                name = f"@{self.prefix}:{func.__name__}"
                __doc__ = f"[{objtype.__name__} -> {objtype.__name__}] {doc}"

                def add_arguments(self, parser: ArgumentParser) -> None:
                    if args:
                        for arg in args:
                            parser.add_argument(*arg[0], **arg[1])

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
        args: t.Optional[t.Sequence[ArgType]] = None,
    ):
        '''Use this decorator to define handlers

        :param type fromtype: The type of object this handler is expecting.
        :param type totype: The type of object this handler returns.
        :param list args (optional): List of arguments for :py:class:`argparse.ArgumentParser`.

        Custom project specific handlers can be defined in the ``viperfile.py`` like below.

        .. code-block:: python

            @myproj.handler(
                fromtype=Results, totype=Results, args=[arg("file", type=FileType("w"))]
            )
            def results2csv(results: Results, args: Namespace) -> Results:
                """Export csv formatted results to file"""

                if results.count() > 0:

                    import csv
                    # Export the results to a CSV file

                # Return the results so that it can be piped to some other command/handler.
                return results

        We can print the command usage with

        .. code-block:: bash

            viper @myproj:results2csv --help

        .. tip:: See :py:func:`viper.demo.viperfile.results2csv`.
        '''

        if not issubclass(fromtype, ViperCollection):
            raise ValueError(f"{fromtype} does not have pipe option")

        def wrapper(
            func: t.Callable[[ViperCollection, Namespace], object]
        ) -> t.Callable[[ViperCollection, Namespace], object]:

            doc = func.__doc__.splitlines()[0] if func.__doc__ else ""

            class HandlerCommand(SubCommand):
                name = f"@{self.prefix}:{func.__name__}"
                __doc__ = f"[{fromtype.__name__} -> {totype.__name__}] {doc}"

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
        self,
        fromtype: type,
        totype: t.Optional[type] = None,
        args: t.Optional[t.Sequence[ArgType]] = None,
    ):
        '''Use this decorator to define a job.

        :param type fromtype: The type of object this handler is expecting.
        :param type totype: The type of object this handler returns.
        :param list args (optional): List of arguments for :py:class:`argparse.ArgumentParser`.

        Custom project specific handlers can be defined in the ``viperfile.py`` like below.

        :example:

        .. code-block:: python

            @myproj.job(
                fromtype=Hosts,
                totype=Results,
                args=[
                    arg("command"),
                    arg("file", type=FileType("w"), help="CSV file path for the result"),
                    arg("--max-workers", default=0, type=int),
                ],
            )
            def remote_exec(hosts: Hosts, args: Namespace) -> Results:
                """Execute command on hosts remotely."""
                return hosts.run_task(
                    Task(
                        "Remote execute",
                        remote_exec_command,
                        timeout=300,
                        retry=0,
                        pre_run=log_command_callback,
                        post_run=log_status_callback,
                    ),
                    args.command,
                    max_workers=args.max_workers,
                ).pipe(lambda results: results2csv(results, args))

        We can print the command usage with

        .. code-block:: bash

            viper @myproj:remote_exec --help

        .. tip:: See :py:func:`viper.demo.viperfile.allhosts`.
        '''

        def wrapper(
            func: t.Callable[[ViperCollection, Namespace], object]
        ) -> t.Callable[[ViperCollection, Namespace], object]:

            doc = func.__doc__.splitlines()[0] if func.__doc__ else ""

            class WorkFlowCommand(SubCommand):
                name = f"@{self.prefix}:{func.__name__}"
                __doc__ = f"[{fromtype.__name__} -> {totype.__name__}] {doc}"

                def add_arguments(self, parser: ArgumentParser) -> None:
                    if args:
                        for arg in args:
                            parser.add_argument(*arg[0], **arg[1])
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
