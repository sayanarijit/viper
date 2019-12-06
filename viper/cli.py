"""Viper Command-line Interface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TODO: add docs
"""

from argparse import ArgumentParser
from argparse import Namespace
from pydoc import locate
from viper import __version__
from viper import Hosts
from viper import Results
from viper import Runners
from viper import Task
from viper.cli_base import SubCommand
from viper.collections import Collection as ViperCollection
from viper.collections import FilterType
from viper.collections import HandlerType
from viper.collections import WhereQueryOptions
from viper.const import Config
from viper.db import ViperDB

import os
import sqlite3
import sys
import traceback
import typing as t

__all__ = ["func", "run"]


def func(objpath: str) -> t.Union[HandlerType, FilterType]:
    """Resolved python function from given string."""

    funcobj = locate(objpath)
    if not func:
        raise ValueError(f"could not resolve {repr(objpath)}.")

    if not callable(funcobj):
        raise ValueError(f"{repr(objpath)} is not a valid function.")

    return funcobj


class InitCommand(SubCommand):
    """initialize the current workspace"""

    name = "init"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "-f",
            "--force",
            action="store_true",
            help="remove or overwrite existing data",
        )

    def __call__(self, args: Namespace) -> int:
        try:
            ViperDB.init(ViperDB.url, force=args.force)
        except sqlite3.OperationalError:
            raise RuntimeError(
                "database already exists!"
                " use '-f'/'--force' to force re-create the database."
            )
        return 0


class RunJobCommand(SubCommand):
    """[? -> ?] run a custom defined job"""

    name = "run-job"
    aliases = ("run",)

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("job", type=func, help="job definition location")
        parser.add_argument("args", nargs="*", help="arguments to be passed to the job")
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        obj = args.job(input(), *args.args)
        if obj is None:
            return 0

        if isinstance(obj, ViperCollection):
            print(obj.to_json(indent=args.indent))
            return 0

        print(obj)
        return 0


class TaskFromFuncCommand(SubCommand):
    """[-> Task] get the task from a Python function location"""

    name = "task:from-func"
    aliases = ("task",)

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "func", type=Task.from_func, help=Task.from_func.__doc__.lower()
        )
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(args.func.to_json(indent=args.indent))
        return 0


class TaskResultsCommand(SubCommand):
    """[Task -> Results] get the past results of given task"""

    name = "task:results"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(Task.from_json(input()).results().to_json(indent=args.indent))
        return 0


class TaskFormatCommand(SubCommand):
    """[Task -> str] format the data using the given template"""

    name = "task:format"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("template", help="use Python's string format syntax")

    def __call__(self, args: Namespace) -> int:
        print(Task.from_json(input()).format(args.template))
        return 0


class HostsFromFuncCommand(SubCommand):
    """[-> Hosts] get a group of hosts from a Python function location"""

    name = "hosts:from-func"
    aliases = ("hosts",)

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "func", type=Hosts.from_func, help=Hosts.from_func.__doc__.lower()
        )
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(args.func.to_json(indent=args.indent))
        return 0


class HostsFromFileCommand(SubCommand):
    """[-> Hosts] get a group of hosts from a file"""

    name = "hosts:from-file"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("filepath")
        parser.add_argument(
            "--loader",
            type=func,
            help="function that resolves a file object to a viper.Hosts object",
        )
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(
            Hosts.from_file(args.filepath, loader=args.loader).to_json(
                indent=args.indent
            )
        )
        return 0


class HostsTaskCommand(SubCommand):
    """[Hosts -> Runners] assign a task to each host"""

    name = "hosts:task"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "task", type=Task.from_func, help=Task.from_func.__doc__.lower()
        )
        parser.add_argument(
            "args", nargs="*", help="arguments to be passed to the command factory"
        )
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:

        print(
            Hosts.from_json(input())
            .task(args.task, *args.args)
            .to_json(indent=args.indent)
        )
        return 0


class HostsRunTaskCommand(SubCommand):
    """[Hosts -> Results] assign a task to each host and run"""

    name = "hosts:run-task"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "task", type=Task.from_func, help=Task.from_func.__doc__.lower()
        )
        parser.add_argument(
            "args", nargs="*", help="arguments to be passed to the command factory"
        )
        parser.add_argument("--max-workers", type=int, default=Config.max_workers.value)
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(
            Hosts.from_json(input())
            .run_task(args.task, *args.args, max_workers=args.max_workers)
            .to_json(indent=args.indent)
        )
        return 0


class HostsFilterCommand(SubCommand):
    """[Hosts -> Hosts] filter hosts by a given function"""

    name = "hosts:filter"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("filter", type=func)
        parser.add_argument(
            "args", nargs="*", help="arguments to be passed to the filter"
        )
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(
            Hosts.from_json(input())
            .filter(args.filter, *args.args)
            .to_json(indent=args.indent)
        )
        return 0


class HostsCountCommand(SubCommand):
    """[Hosts -> int] count the number of hosts"""

    name = "hosts:count"

    def add_arguments(self, parser: ArgumentParser) -> None:
        pass

    def __call__(self, args: Namespace) -> int:
        print(Hosts.from_json(input()).count())
        return 0


class HostsSortCommand(SubCommand):
    """[Hosts -> Hosts] sort the hosts"""

    name = "hosts:sort"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--key", type=func)
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(Hosts.from_json(input()).sort(key=args.key).to_json(indent=args.indent))
        return 0


class HostsPipeCommand(SubCommand):
    """[Hosts -> ?] pipe the hosts to the given handler"""

    name = "hosts:pipe"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("handler", type=func)
        parser.add_argument(
            "args", nargs="*", help="arguments to be passed to the filter"
        )
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        obj = Hosts.from_json(input()).pipe(args.handler, *args.args)

        if obj is None:
            return 0

        if isinstance(obj, ViperCollection):
            print(obj.to_json(indent=args.indent))
            return 0

        print(obj)
        return 0


class HostsFormatCommand(SubCommand):
    """[Hosts -> str] format the data using the given template"""

    name = "hosts:format"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("template", help="use Python's string format syntax")
        parser.add_argument(
            "-s", "--sep", help="separator used to join the strings", default="\n"
        )

    def __call__(self, args: Namespace) -> int:
        print(Hosts.from_json(input()).format(args.template, sep=args.sep))
        return 0


class HostsWhereCommand(SubCommand):
    """[Hosts -> Hosts] select hosts matching the given query"""

    name = "hosts:where"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("key", help="property name/path of each item")
        parser.add_argument(
            "query_option", choices=[o.value for o in WhereQueryOptions],
        )
        parser.add_argument("values", nargs="*")
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(
            Hosts.from_json(input())
            .where(args.key, WhereQueryOptions(args.query_option), args.values)
            .to_json(indent=args.indent)
        )
        return 0


class HostsResultsCommand(SubCommand):
    """[Hosts -> Results] get the past results of the hosts"""

    name = "hosts:results"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(Hosts.from_json(input()).results().to_json(indent=args.indent))
        return 0


class RunnersFilterCommand(SubCommand):
    """[Runners -> Runners] filter runners by a given function"""

    name = "runners:filter"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("filter", type=func)
        parser.add_argument(
            "args", nargs="*", help="arguments to be passed to the filter"
        )
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(
            Runners.from_json(input())
            .filter(args.filter, *args.args)
            .to_json(indent=args.indent)
        )
        return 0


class RunnersCountCommand(SubCommand):
    """[Runners -> int] count the number of runners"""

    name = "runners:count"

    def add_arguments(self, parser: ArgumentParser) -> None:
        pass

    def __call__(self, args: Namespace) -> int:
        print(Runners.from_json(input()).count())
        return 0


class RunnersSortCommand(SubCommand):
    """[Runners -> Runners] sort the runners"""

    name = "runners:sort"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--key", type=func)
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(Runners.from_json(input()).sort(key=args.key).to_json(indent=args.indent))
        return 0


class RunnersPipeCommand(SubCommand):
    """[Runners -> ?] pipe the runners to the given handler"""

    name = "runners:pipe"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("handler", type=func)
        parser.add_argument(
            "args", nargs="*", help="arguments to be passed to the filter"
        )
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        obj = Runners.from_json(input()).pipe(args.handler, *args.args)

        if obj is None:
            return 0

        if isinstance(obj, ViperCollection):
            print(obj.to_json(indent=args.indent))
            return 0

        print(obj)
        return 0


class RunnersFormatCommand(SubCommand):
    """[Runners -> str] format the data using the given template"""

    name = "runners:format"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("template", help="use Python's string format syntax")
        parser.add_argument(
            "-s", "--sep", help="separator used to join the strings", default="\n"
        )

    def __call__(self, args: Namespace) -> int:
        print(Runners.from_json(input()).format(args.template, sep=args.sep))


class RunnersWhereCommand(SubCommand):
    """[Runners -> Runners] select runners matching the given query"""

    name = "runners:where"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("key", help="property name/path of each item")
        parser.add_argument(
            "query_option", choices=[o.value for o in WhereQueryOptions],
        )
        parser.add_argument("values", nargs="*")
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(
            Runners.from_json(input())
            .where(args.key, WhereQueryOptions(args.query_option), args.values)
            .to_json(indent=args.indent)
        )
        return 0


class RunnersRunCommand(SubCommand):
    """[Runners -> Results] run the assigned tasks"""

    name = "runners:run"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "args", nargs="*", help="arguments to be passed to the command factory"
        )
        parser.add_argument("--max-workers", type=int, default=Config.max_workers.value)
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(
            Runners.from_json(input())
            .run(*args.args, max_workers=args.max_workers)
            .to_json(indent=args.indent)
        )
        return 0


class RunnersHostsCommand(SubCommand):
    """[Runners -> Hosts] get the hosts from the runners"""

    name = "runners:hosts"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(Runners.from_json(input()).hosts().to_json(indent=args.indent))
        return 0


class ResultsFromHistoryCommand(SubCommand):
    """[-> Results] get the past results from database"""

    name = "results:from-history"
    aliases = ("results",)

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(Results.from_history().to_json(indent=args.indent))
        return 0


class ResultsFilterCommand(SubCommand):
    """[Results -> Results] filter results by a given handler"""

    name = "results:filter"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("filter", type=func)
        parser.add_argument(
            "args", nargs="*", help="arguments to be passed to the filter"
        )
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(
            Results.from_json(input())
            .filter(args.filter, *args.args)
            .to_json(indent=args.indent)
        )
        return 0


class ResultsCountCommand(SubCommand):
    """[Results -> int] count the number of results"""

    name = "results:count"

    def add_arguments(self, parser: ArgumentParser) -> None:
        pass

    def __call__(self, args: Namespace) -> int:
        print(Results.from_json(input()).count())
        return 0


class ResultsSortCommand(SubCommand):
    """[Results -> Results] sort the results"""

    name = "results:sort"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--key", type=func)
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(Results.from_json(input()).sort(key=args.key).to_json(indent=args.indent))
        return 0


class ResultsPipeCommand(SubCommand):
    """[Results -> ?] pipe the results to the given handler"""

    name = "results:pipe"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("handler", type=func)
        parser.add_argument(
            "args", nargs="*", help="arguments to be passed to the filter"
        )
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        obj = Results.from_json(input()).pipe(args.handler, *args.args)

        if obj is None:
            return 0

        if isinstance(obj, ViperCollection):
            print(obj.to_json(indent=args.indent))
            return 0

        print(obj)
        return 0


class ResultsFormatCommand(SubCommand):
    """[Results -> str] format the data using the given template"""

    name = "results:format"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("template", help="use Python's string format syntax")
        parser.add_argument(
            "-s", "--sep", help="separator used to join the strings", default="\n"
        )

    def __call__(self, args: Namespace) -> int:
        print(Results.from_json(input()).format(args.template, sep=args.sep))
        return 0


class ResultsWhereCommand(SubCommand):
    """[Results -> Results] select results matching the given query"""

    name = "results:where"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("key", help="property name/path of each item")
        parser.add_argument(
            "query_option", choices=[o.value for o in WhereQueryOptions],
        )
        parser.add_argument("values", nargs="*")
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(
            Results.from_json(input())
            .where(args.key, WhereQueryOptions(args.query_option), args.values)
            .to_json(indent=args.indent)
        )
        return 0


class ResultsHostsCommand(SubCommand):
    """[Results -> Hosts] get the hosts from the results"""

    name = "results:hosts"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(Results.from_json(input()).hosts().to_json(indent=args.indent))
        return 0


class ResultsByTaskCommand(SubCommand):
    """[Task -> Results] get the past results of given task"""

    name = "results:by-task"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(Results.by_task(Task.from_json(input())).to_json(indent=args.indent))
        return 0


def run() -> int:
    parser = ArgumentParser("viper", description=f"Viper CLI {__version__}")
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument(
        "--debug",
        action="store_true",
        help="show traceback information when an exception is raised",
    )
    subparsers = parser.add_subparsers()

    # Init command
    InitCommand.attach_to(subparsers)

    # Job run command
    RunJobCommand.attach_to(subparsers)

    # Task commands
    TaskFromFuncCommand.attach_to(subparsers)
    TaskResultsCommand.attach_to(subparsers)
    TaskFormatCommand.attach_to(subparsers)

    # Hosts commands
    HostsFromFileCommand.attach_to(subparsers)
    HostsFromFuncCommand.attach_to(subparsers)

    HostsFilterCommand.attach_to(subparsers)
    HostsCountCommand.attach_to(subparsers)
    HostsSortCommand.attach_to(subparsers)
    HostsPipeCommand.attach_to(subparsers)
    HostsFormatCommand.attach_to(subparsers)
    HostsWhereCommand.attach_to(subparsers)

    HostsTaskCommand.attach_to(subparsers)
    HostsRunTaskCommand.attach_to(subparsers)
    HostsResultsCommand.attach_to(subparsers)

    # Task runners commands
    RunnersFilterCommand.attach_to(subparsers)
    RunnersCountCommand.attach_to(subparsers)
    RunnersSortCommand.attach_to(subparsers)
    RunnersPipeCommand.attach_to(subparsers)
    RunnersFormatCommand.attach_to(subparsers)
    RunnersWhereCommand.attach_to(subparsers)

    RunnersRunCommand.attach_to(subparsers)
    RunnersHostsCommand.attach_to(subparsers)

    # Task results commands
    ResultsFromHistoryCommand.attach_to(subparsers)
    ResultsFilterCommand.attach_to(subparsers)
    ResultsCountCommand.attach_to(subparsers)
    ResultsSortCommand.attach_to(subparsers)
    ResultsPipeCommand.attach_to(subparsers)
    ResultsFormatCommand.attach_to(subparsers)
    ResultsWhereCommand.attach_to(subparsers)

    ResultsHostsCommand.attach_to(subparsers)
    ResultsByTaskCommand.attach_to(subparsers)

    # Import project specific commands
    if os.path.exists("viperfile.py"):
        from viper import project

        sys.path.insert(0, os.path.realpath("."))
        import viperfile

        for k, v in vars(viperfile).items():
            if not isinstance(v, project.Project):
                continue

            for subcommand in v.all_commands():
                subcommand.attach_to(subparsers)

    args = parser.parse_args()

    if not hasattr(args, "_handler"):
        parser.print_usage()
        return 1

    try:
        return args._handler(args)
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        if args.debug:
            print(traceback.format_exc(), file=sys.stderr)
        return 1
