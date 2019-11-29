"""Viper CLI library."""

import sys
import traceback
import typing as t
from argparse import ArgumentParser
from pydoc import locate

from viper import Hosts, Task, TaskRunners, TaskResults, TaskRunners, __version__
from viper.db import ViperDB


def func(objpath):
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
    def attach_to(cls, subparsers):
        subparser = subparsers.add_parser(cls.subcommand, help=cls.__doc__.lower())
        if cls.aliases:
            for alias in cls.aliases:
                cls(
                    subparsers.add_parser(
                        alias, help=f"alias of {repr(cls.subcommand)}"
                    )
                )
        return cls(subparser)

    def __init__(self, subparser):
        self.add_arguments(subparser)
        subparser.add_argument("--debug", action="store_true")
        subparser.set_defaults(handler=self)

    def add_arguments(self, parser):
        raise NotImplementedError()

    def __call__(self, args):
        raise NotImplementedError()


class InitCommand(SubParser):
    """initialize the current workspace"""

    subcommand = "init"

    def add_arguments(self, parser):
        parser.add_argument(
            "-f",
            "--force",
            action="store_true",
            help="remove or overwrite existing data",
        )

    def __call__(self, args) -> int:
        ViperDB.init(ViperDB.url, force=args.force)
        return 0


class TaskFromObjCommand(SubParser):
    """get the task from a Python object location"""

    subcommand = "task:from-obj"

    def add_arguments(self, parser):
        parser.add_argument(
            "obj", type=Task.from_obj, help=Task.from_obj.__doc__.lower()
        )
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args) -> int:
        print(args.obj.to_json(indent=args.indent))
        return 0


class HostsFromObjCommand(SubParser):
    """get a group of hosts from a Python object location"""

    subcommand = "hosts:from-obj"

    def add_arguments(self, parser):
        parser.add_argument(
            "obj", type=Hosts.from_obj, help=Hosts.from_obj.__doc__.lower()
        )
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args) -> int:
        print(args.obj.to_json(indent=args.indent))
        return 0


class HostsFromFileCommand(SubParser):
    """get a group of hosts from a file"""

    subcommand = "hosts:from-file"

    def add_arguments(self, parser):
        parser.add_argument("filepath")
        parser.add_argument(
            "--loader",
            type=func,
            help="function that resolves a file object to a viper.Hosts object",
        )
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args) -> int:
        print(
            Hosts.from_file(args.filepath, loader=args.loader).to_json(
                indent=args.indent
            )
        )
        return 0


class HostsTaskCommand(SubParser):
    """assign a task to each host"""

    subcommand = "hosts:task"

    def add_arguments(self, parser):
        parser.add_argument(
            "task", type=Task.from_obj, help=Task.from_obj.__doc__.lower()
        )
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args) -> int:

        print(Hosts.from_json(input()).task(args.task).to_json(indent=args.indent))
        return 0


class HostsRunTaskCommand(SubParser):
    """assign a task to each host and run"""

    subcommand = "hosts:run-task"

    def add_arguments(self, parser):
        parser.add_argument(
            "task", type=Task.from_obj, help=Task.from_obj.__doc__.lower()
        )
        parser.add_argument("--max-workers", type=int, default=0)
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args) -> int:

        print(
            Hosts.from_json(input())
            .run_task(args.task, max_workers=args.max_workers)
            .to_json(indent=args.indent)
        )
        return 0


class HostsFilterCommand(SubParser):
    """filter hosts by a given function"""

    subcommand = "hosts:filter"

    def add_arguments(self, parser):
        parser.add_argument("filter", type=func)
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args):
        print(Hosts.from_json(input()).filter(args.filter).to_json(indent=args.indent))
        return 0


class HostsCountCommand(SubParser):
    """count the number of hosts"""

    subcommand = "hosts:count"

    def add_arguments(self, parser):
        pass

    def __call__(self, args):
        print(Hosts.from_json(input()).count())
        return 0


class HostsSortCommand(SubParser):
    """sort the hosts"""

    subcommand = "hosts:sort"

    def add_arguments(self, parser):
        parser.add_argument("--key", type=func)
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args):
        print(Hosts.from_json(input()).sort(key=args.key).to_json(indent=args.indent))
        return 0


class HostsTaskResultsCommand(SubParser):
    """get the past task results of the hosts"""

    subcommand = "hosts:task-results"

    def add_arguments(self, parser):
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args):
        print(Hosts.from_json(input()).task_results().to_json(indent=args.indent))
        return 0


class TaskRunnersFilterCommand(SubParser):
    """filter task runners by a given function"""

    subcommand = "task-runners:filter"

    def add_arguments(self, parser):
        parser.add_argument("filter", type=func)
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args):
        print(
            TaskRunners.from_json(input())
            .filter(args.filter)
            .to_json(indent=args.indent)
        )
        return 0


class TaskRunnersCountCommand(SubParser):
    """count the number of task runners"""

    subcommand = "task-runners:count"

    def add_arguments(self, parser):
        pass

    def __call__(self, args):
        print(TaskRunners.from_json(input()).count())
        return 0


class TaskRunnersSortCommand(SubParser):
    """sort the task runners"""

    subcommand = "task-runners:sort"

    def add_arguments(self, parser):
        parser.add_argument("--key", type=func)
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args):
        print(
            TaskRunners.from_json(input())
            .sort(key=args.key)
            .to_json(indent=args.indent)
        )
        return 0


class TaskRunnersRunCommand(SubParser):
    """run the assigned tasks"""

    subcommand = "task-runners:run"

    def add_arguments(self, parser):
        parser.add_argument("--max-workers", type=int, default=0)
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args):
        print(
            TaskRunners.from_json(input())
            .run(max_workers=args.max_workers)
            .to_json(indent=args.indent)
        )
        return 0


class TaskRunnersHostsCommand(SubParser):
    """get the hohsts from the task runners"""

    subcommand = "task-runners:hosts"

    def add_arguments(self, parser):
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args):
        print(TaskRunners.from_json(input()).hosts().to_json(indent=args.indent))
        return 0


class TaskResultsFilterCommand(SubParser):
    """filter task results by a given function"""

    subcommand = "task-results:filter"

    def add_arguments(self, parser):
        parser.add_argument("filter", type=func)
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args):
        print(
            TaskResults.from_json(input())
            .filter(args.filter)
            .to_json(indent=args.indent)
        )
        return 0


class TaskResultsCountCommand(SubParser):
    """count the number of task results"""

    subcommand = "task-results:count"

    def add_arguments(self, parser):
        pass

    def __call__(self, args):
        print(TaskResults.from_json(input()).count())
        return 0


class TaskResultsSortCommand(SubParser):
    """sort the task results"""

    subcommand = "task-results:sort"

    def add_arguments(self, parser):
        parser.add_argument("--key", type=func)
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args):
        print(
            TaskResults.from_json(input())
            .sort(key=args.key)
            .to_json(indent=args.indent)
        )
        return 0


class TaskResultsHostsCommand(SubParser):
    """get the hosts from the task results"""

    subcommand = "task-results:hosts"

    def add_arguments(self, parser):
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args):
        print(TaskResults.from_json(input()).hosts().to_json(indent=args.indent))
        return 0


class TaskResultsByTaskCommand(SubParser):
    """get the past task results of given task"""

    subcommand = "task-results:by-task"

    def add_arguments(self, parser):
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args):
        print(TaskResults.by_task(Task.from_json(input())).to_json(indent=args.indent))
        return 0


def run() -> int:
    parser = ArgumentParser("viper", description=f"Viper CLI {__version__}")
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("--debug", action="store_true")
    subparsers = parser.add_subparsers()

    # Init command
    InitCommand.attach_to(subparsers)

    # Task commands
    TaskFromObjCommand.attach_to(subparsers)

    # Hosts commands
    HostsFromFileCommand.attach_to(subparsers)
    HostsFromObjCommand.attach_to(subparsers)

    HostsFilterCommand.attach_to(subparsers)
    HostsCountCommand.attach_to(subparsers)
    HostsSortCommand.attach_to(subparsers)

    HostsTaskCommand.attach_to(subparsers)
    HostsRunTaskCommand.attach_to(subparsers)
    HostsTaskResultsCommand.attach_to(subparsers)

    # Task runners commands
    TaskRunnersFilterCommand.attach_to(subparsers)
    TaskRunnersCountCommand.attach_to(subparsers)
    TaskRunnersSortCommand.attach_to(subparsers)

    TaskRunnersRunCommand.attach_to(subparsers)
    TaskRunnersHostsCommand.attach_to(subparsers)

    # Task results commands
    TaskResultsFilterCommand.attach_to(subparsers)
    TaskResultsCountCommand.attach_to(subparsers)
    TaskResultsSortCommand.attach_to(subparsers)

    TaskResultsHostsCommand.attach_to(subparsers)
    TaskResultsByTaskCommand.attach_to(subparsers)

    args = parser.parse_args()

    if not hasattr(args, "handler"):
        parser.print_usage()
        return 2

    try:
        return args.handler(args)
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        if args.debug:
            print(traceback.format_exc(), file=sys.stderr)
        return 1
