"""Viper CLI library."""

from argparse import _SubParsersAction
from argparse import ArgumentParser
from argparse import Namespace
from pydoc import locate
from viper import __version__
from viper import Hosts
from viper import Results
from viper import Runners
from viper import Task
from viper.collections import FilterType
from viper.collections import HandlerType
from viper.const import Config
from viper.db import ViperDB

import sys
import traceback
import typing as t

__all__ = ["SubParser", "func", "run"]


def func(objpath: str) -> t.Union[HandlerType, FilterType]:
    """Resolved python function from given string."""

    func = locate(objpath)
    if not func:
        raise ValueError(f"could not resolve {repr(objpath)}.")

    if not callable(func):
        raise ValueError(f"{repr(objpath)} is not a valid function.")

    return func


class SubParser:
    """Base class for the subcommand parsers."""

    subcommand: t.Optional[str] = None

    aliases: t.Sequence[str] = ()

    @classmethod
    def attach_to(cls, subparsers: _SubParsersAction) -> None:

        if not cls.subcommand:
            raise NotImplementedError()  # no cover

        subparser = subparsers.add_parser(cls.subcommand, help=cls.__doc__)
        if cls.aliases:
            for alias in cls.aliases:
                cls(
                    subparsers.add_parser(
                        alias, help=f"alias of {repr(cls.subcommand)}"
                    )
                )
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


class InitCommand(SubParser):
    """initialize the current workspace"""

    subcommand = "init"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "-f",
            "--force",
            action="store_true",
            help="remove or overwrite existing data",
        )

    def __call__(self, args: Namespace) -> int:
        ViperDB.init(ViperDB.url, force=args.force)
        return 0


class TaskFromFuncCommand(SubParser):
    """[task:from-func FUNC > Task] get the task from a Python function location"""

    subcommand = "task:from-func"
    aliases = ("task",)

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "func", type=Task.from_func, help=Task.from_func.__doc__.lower()
        )
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(args.func.to_json(indent=args.indent))
        return 0


class ResultsCommand(SubParser):
    """[Task > task:results > Results] get the past results of given task"""

    subcommand = "task:results"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(Task.from_json(input()).results().to_json(indent=args.indent))
        return 0


class HostsFromFuncCommand(SubParser):
    """[hosts:from-func FUNC > Hosts] get a group of hosts from a Python function location"""

    subcommand = "hosts:from-func"
    aliases = ("hosts",)

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "func", type=Hosts.from_func, help=Hosts.from_func.__doc__.lower()
        )
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(args.func.to_json(indent=args.indent))
        return 0


class HostsFromFileCommand(SubParser):
    """[hosts:from-file FILE > Hosts] get a group of hosts from a file"""

    subcommand = "hosts:from-file"

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


class HostsTaskCommand(SubParser):
    """[Hosts > hosts:task TASK > Runners] assign a task to each host"""

    subcommand = "hosts:task"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "task", type=Task.from_func, help=Task.from_func.__doc__.lower()
        )
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:

        print(Hosts.from_json(input()).task(args.task).to_json(indent=args.indent))
        return 0


class HostsRunTaskCommand(SubParser):
    """[Hosts > hosts:run-task > Runners] assign a task to each host and run"""

    subcommand = "hosts:run-task"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "task", type=Task.from_func, help=Task.from_func.__doc__.lower()
        )
        parser.add_argument("--max-workers", type=int, default=Config.max_workers.value)
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:

        print(
            Hosts.from_json(input())
            .run_task(args.task, max_workers=args.max_workers)
            .to_json(indent=args.indent)
        )
        return 0


class HostsRunTaskThenPipeCommand(SubParser):
    """[Hosts > hosts:run-task-then-pipe TASK HANDLER *ARGS > ?] run the task on hosts and pipe the results to a handler"""

    subcommand = "hosts:run-task-then-pipe"
    aliases = ("hosts:rttp",)

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "task", type=Task.from_func, help=Task.from_func.__doc__.lower()
        )
        parser.add_argument("handler", type=func, help="the result handler function")
        parser.add_argument(
            "args", nargs="*", help="arguments to be passed to the filter"
        )
        parser.add_argument("--max-workers", type=int, default=Config.max_workers.value)

    def __call__(self, args: Namespace) -> int:
        Hosts.from_json(input()).run_task_then_pipe(
            args.task, args.handler, *args.args, max_workers=args.max_workers
        )
        return 0


class HostsFilterCommand(SubParser):
    """[Hosts > hosts:filter FILTER *AGS > Hosts] filter hosts by a given function"""

    subcommand = "hosts:filter"

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


class HostsCountCommand(SubParser):
    """[Hosts > hosts:count > int] count the number of hosts"""

    subcommand = "hosts:count"

    def add_arguments(self, parser: ArgumentParser) -> None:
        pass

    def __call__(self, args: Namespace) -> int:
        print(Hosts.from_json(input()).count())
        return 0


class HostsSortCommand(SubParser):
    """[Hosts > hosts:sort > Hosts] sort the hosts"""

    subcommand = "hosts:sort"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--key", type=func)
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(Hosts.from_json(input()).sort(key=args.key).to_json(indent=args.indent))
        return 0


class HostsPipeCommand(SubParser):
    """[Hosts > hosts:pipe HANDLER *ARGS > ?] pipe the hosts to the given handler"""

    subcommand = "hosts:pipe"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("handler", type=func)
        parser.add_argument(
            "args", nargs="*", help="arguments to be passed to the filter"
        )

    def __call__(self, args: Namespace) -> int:
        Hosts.from_json(input()).pipe(args.handler, *args.args)
        return 0


class HostsResultsCommand(SubParser):
    """[Hosts > hosts:results > Results] get the past results of the hosts"""

    subcommand = "hosts:results"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(Hosts.from_json(input()).results().to_json(indent=args.indent))
        return 0


class RunnersFilterCommand(SubParser):
    """[Runners > runners:filter FILTER *ARGS > Runners] filter runners by a given function"""

    subcommand = "runners:filter"

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


class RunnersCountCommand(SubParser):
    """[Runners > runners:count > int] count the number of runners"""

    subcommand = "runners:count"

    def add_arguments(self, parser: ArgumentParser) -> None:
        pass

    def __call__(self, args: Namespace) -> int:
        print(Runners.from_json(input()).count())
        return 0


class RunnersSortCommand(SubParser):
    """[Runners > runners:sort > Runners] sort the runners"""

    subcommand = "runners:sort"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--key", type=func)
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(Runners.from_json(input()).sort(key=args.key).to_json(indent=args.indent))
        return 0


class RunnersPipeCommand(SubParser):
    """[Runners > runners:pipe HANDLER *ARGS > ?] pipe the runners to the given handler"""

    subcommand = "runners:pipe"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("handler", type=func)
        parser.add_argument(
            "args", nargs="*", help="arguments to be passed to the filter"
        )

    def __call__(self, args: Namespace) -> int:
        Runners.from_json(input()).pipe(args.handler, *args.args)
        return 0


class RunnersRunCommand(SubParser):
    """[Runners > runners:run > Results] run the assigned tasks"""

    subcommand = "runners:run"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--max-workers", type=int, default=Config.max_workers.value)
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(
            Runners.from_json(input())
            .run(max_workers=args.max_workers)
            .to_json(indent=args.indent)
        )
        return 0


class RunnersHostsCommand(SubParser):
    """[Runners > runners:hosts > Hosts] get the hohsts from the runners"""

    subcommand = "runners:hosts"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(Runners.from_json(input()).hosts().to_json(indent=args.indent))
        return 0


class ResultsFilterCommand(SubParser):
    """[Results > results:filter FILTER *ARGS > Results] filter results by a given handler"""

    subcommand = "results:filter"

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


class ResultsCountCommand(SubParser):
    """[Results > results:count > int] count the number of results"""

    subcommand = "results:count"

    def add_arguments(self, parser: ArgumentParser) -> None:
        pass

    def __call__(self, args: Namespace) -> int:
        print(Results.from_json(input()).count())
        return 0


class ResultsSortCommand(SubParser):
    """[Results > results:sort > Results] sort the results"""

    subcommand = "results:sort"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--key", type=func)
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(Results.from_json(input()).sort(key=args.key).to_json(indent=args.indent))
        return 0


class ResultsPipeCommand(SubParser):
    """[Results > results:pipe HANDLER *ARGS > ?] pipe the results to the given handler"""

    subcommand = "results:pipe"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("handler", type=func)
        parser.add_argument(
            "args", nargs="*", help="arguments to be passed to the filter"
        )

    def __call__(self, args: Namespace) -> int:
        Results.from_json(input()).pipe(args.handler, *args.args)
        return 0


class ResultsHostsCommand(SubParser):
    """[Results > results:hosts > Hosts] get the hosts from the results"""

    subcommand = "results:hosts"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(Results.from_json(input()).hosts().to_json(indent=args.indent))
        return 0


class ResultsByTaskCommand(SubParser):
    """[Task > results:by-task > Results] get the past results of given task"""

    subcommand = "results:by-task"

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

    # Task commands
    TaskFromFuncCommand.attach_to(subparsers)
    ResultsCommand.attach_to(subparsers)

    # Hosts commands
    HostsFromFileCommand.attach_to(subparsers)
    HostsFromFuncCommand.attach_to(subparsers)

    HostsFilterCommand.attach_to(subparsers)
    HostsCountCommand.attach_to(subparsers)
    HostsSortCommand.attach_to(subparsers)
    HostsPipeCommand.attach_to(subparsers)

    HostsTaskCommand.attach_to(subparsers)
    HostsRunTaskCommand.attach_to(subparsers)
    HostsRunTaskThenPipeCommand.attach_to(subparsers)
    HostsResultsCommand.attach_to(subparsers)

    # Task runners commands
    RunnersFilterCommand.attach_to(subparsers)
    RunnersCountCommand.attach_to(subparsers)
    RunnersSortCommand.attach_to(subparsers)
    RunnersPipeCommand.attach_to(subparsers)

    RunnersRunCommand.attach_to(subparsers)
    RunnersHostsCommand.attach_to(subparsers)

    # Task results commands
    ResultsFilterCommand.attach_to(subparsers)
    ResultsCountCommand.attach_to(subparsers)
    ResultsSortCommand.attach_to(subparsers)
    ResultsPipeCommand.attach_to(subparsers)

    ResultsHostsCommand.attach_to(subparsers)
    ResultsByTaskCommand.attach_to(subparsers)

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
