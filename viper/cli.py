"""Viper CLI library."""

import sys
import traceback
import typing as t
from argparse import ArgumentParser
from pydoc import locate

from viper import Hosts, Task, TaskResults, TaskRunners, __version__
from viper.const import Config
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
        subparser = subparsers.add_parser(cls.subcommand, help=cls.__doc__)
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
        subparser.set_defaults(_handler=self)
        subparser.add_argument(
            "--debug",
            action="store_true",
            help="show traceback information when an exception is raised",
        )

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


class TaskFromFuncCommand(SubParser):
    """[task:from-func FUNC > Task] get the task from a Python function location"""

    subcommand = "task:from-func"
    aliases = ("task",)

    def add_arguments(self, parser):
        parser.add_argument(
            "func", type=Task.from_func, help=Task.from_func.__doc__.lower()
        )
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args) -> int:
        print(args.func.to_json(indent=args.indent))
        return 0


class TaskResultsCommand(SubParser):
    """[Task > task:results > TaskResults] get the past task results of given task"""

    subcommand = "task:results"

    def add_arguments(self, parser):
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args) -> int:
        print(Task.from_json(input()).results().to_json(indent=args.indent))
        return 0


class HostsFromFuncCommand(SubParser):
    """[hosts:from-func FUNC > Hosts] get a group of hosts from a Python function location"""

    subcommand = "hosts:from-func"
    aliases = ("hosts",)

    def add_arguments(self, parser):
        parser.add_argument(
            "func", type=Hosts.from_func, help=Hosts.from_func.__doc__.lower()
        )
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args) -> int:
        print(args.func.to_json(indent=args.indent))
        return 0


class HostsFromFileCommand(SubParser):
    """[hosts:from-file FILE > Hosts] get a group of hosts from a file"""

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
    """[Hosts > hosts:task TASK > TaskRunners] assign a task to each host"""

    subcommand = "hosts:task"

    def add_arguments(self, parser):
        parser.add_argument(
            "task", type=Task.from_func, help=Task.from_func.__doc__.lower()
        )
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args) -> int:

        print(Hosts.from_json(input()).task(args.task).to_json(indent=args.indent))
        return 0


class HostsRunTaskCommand(SubParser):
    """[Hosts > hosts:run-task > TaskRunners] assign a task to each host and run"""

    subcommand = "hosts:run-task"

    def add_arguments(self, parser):
        parser.add_argument(
            "task", type=Task.from_func, help=Task.from_func.__doc__.lower()
        )
        parser.add_argument("--max-workers", type=int, default=Config.max_workers.value)
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args) -> int:

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

    def add_arguments(self, parser):
        parser.add_argument(
            "task", type=Task.from_func, help=Task.from_func.__doc__.lower()
        )
        parser.add_argument("handler", type=func, help="the result handler function")
        parser.add_argument(
            "args", nargs="*", help="arguments to be passed to the filter"
        )
        parser.add_argument("--max-workers", type=int, default=Config.max_workers.value)

    def __call__(self, args) -> int:
        Hosts.from_json(input()).run_task_then_pipe(
            args.task, args.handler, *args.args, max_workers=args.max_workers,
        )
        return 0


class HostsFilterCommand(SubParser):
    """[Hosts > hosts:filter FILTER *AGS > Hosts] filter hosts by a given function"""

    subcommand = "hosts:filter"

    def add_arguments(self, parser):
        parser.add_argument("filter", type=func)
        parser.add_argument(
            "args", nargs="*", help="arguments to be passed to the filter"
        )
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args):
        print(
            Hosts.from_json(input())
            .filter(args.filter, *args.args)
            .to_json(indent=args.indent)
        )
        return 0


class HostsCountCommand(SubParser):
    """[Hosts > hosts:count > int] count the number of hosts"""

    subcommand = "hosts:count"

    def add_arguments(self, parser):
        pass

    def __call__(self, args):
        print(Hosts.from_json(input()).count())
        return 0


class HostsSortCommand(SubParser):
    """[Hosts > hosts:sort > Hosts] sort the hosts"""

    subcommand = "hosts:sort"

    def add_arguments(self, parser):
        parser.add_argument("--key", type=func)
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args):
        print(Hosts.from_json(input()).sort(key=args.key).to_json(indent=args.indent))
        return 0


class HostsPipeCommand(SubParser):
    """[Hosts > hosts:pipe HANDLER *ARGS > ?] pipe the hosts to the given handler"""

    subcommand = "hosts:pipe"

    def add_arguments(self, parser):
        parser.add_argument("handler", type=func)
        parser.add_argument(
            "args", nargs="*", help="arguments to be passed to the filter"
        )

    def __call__(self, args) -> int:
        Hosts.from_json(input()).pipe(args.handler, *args.args)
        return 0


class HostsTaskResultsCommand(SubParser):
    """[Hosts > hosts:task-results > TaskResults] get the past task results of the hosts"""

    subcommand = "hosts:task-results"

    def add_arguments(self, parser):
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args):
        print(Hosts.from_json(input()).task_results().to_json(indent=args.indent))
        return 0


class TaskRunnersFilterCommand(SubParser):
    """[TaskRunners > task-runners:filter FILTER *ARGS > TaskRunners] filter task runners by a given function"""

    subcommand = "task-runners:filter"

    def add_arguments(self, parser):
        parser.add_argument("filter", type=func)
        parser.add_argument(
            "args", nargs="*", help="arguments to be passed to the filter"
        )
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args):
        print(
            TaskRunners.from_json(input())
            .filter(args.filter, *args.args)
            .to_json(indent=args.indent)
        )
        return 0


class TaskRunnersCountCommand(SubParser):
    """[TaskRunners > task-runners:count > int] count the number of task runners"""

    subcommand = "task-runners:count"

    def add_arguments(self, parser):
        pass

    def __call__(self, args):
        print(TaskRunners.from_json(input()).count())
        return 0


class TaskRunnersSortCommand(SubParser):
    """[TaskRunners > task-runners:sort > TaskRunners] sort the task runners"""

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


class TaskRunnersPipeCommand(SubParser):
    """[TaskRunners > task-runners:pipe HANDLER *ARGS > ?] pipe the task runners to the given handler"""

    subcommand = "task-runners:pipe"

    def add_arguments(self, parser):
        parser.add_argument("handler", type=func)
        parser.add_argument(
            "args", nargs="*", help="arguments to be passed to the filter"
        )

    def __call__(self, args) -> int:
        TaskRunners.from_json(input()).pipe(args.handler, *args.args)
        return 0


class TaskRunnersRunCommand(SubParser):
    """[TaskRunners > task-runners:run > TaskResults] run the assigned tasks"""

    subcommand = "task-runners:run"

    def add_arguments(self, parser):
        parser.add_argument("--max-workers", type=int, default=Config.max_workers.value)
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args):
        print(
            TaskRunners.from_json(input())
            .run(max_workers=args.max_workers)
            .to_json(indent=args.indent)
        )
        return 0


class TaskRunnersHostsCommand(SubParser):
    """[TaskRunners > task-runners:hosts > Hosts] get the hohsts from the task runners"""

    subcommand = "task-runners:hosts"

    def add_arguments(self, parser):
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args):
        print(TaskRunners.from_json(input()).hosts().to_json(indent=args.indent))
        return 0


class TaskResultsFilterCommand(SubParser):
    """[TaskResults > task-results:filter FILTER *ARGS > TaskResults] filter task results by a given handler"""

    subcommand = "task-results:filter"

    def add_arguments(self, parser):
        parser.add_argument("filter", type=func)
        parser.add_argument(
            "args", nargs="*", help="arguments to be passed to the filter"
        )
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args):
        print(
            TaskResults.from_json(input())
            .filter(args.filter, *args.args)
            .to_json(indent=args.indent)
        )
        return 0


class TaskResultsCountCommand(SubParser):
    """[TaskResults > task-results:count > int] count the number of task results"""

    subcommand = "task-results:count"

    def add_arguments(self, parser):
        pass

    def __call__(self, args):
        print(TaskResults.from_json(input()).count())
        return 0


class TaskResultsSortCommand(SubParser):
    """[TaskResults > task-results:sort > TaskResults] sort the task results"""

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


class TaskResultsPipeCommand(SubParser):
    """[TaskResults > task-results:pipe HANDLER *ARGS > ?] pipe the task results to the given handler"""

    subcommand = "task-results:pipe"

    def add_arguments(self, parser):
        parser.add_argument("handler", type=func)
        parser.add_argument(
            "args", nargs="*", help="arguments to be passed to the filter"
        )

    def __call__(self, args) -> int:
        TaskResults.from_json(input()).pipe(args.handler, *args.args)
        return 0


class TaskResultsHostsCommand(SubParser):
    """[TaskResults > task-results:hosts > Hosts] get the hosts from the task results"""

    subcommand = "task-results:hosts"

    def add_arguments(self, parser):
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args):
        print(TaskResults.from_json(input()).hosts().to_json(indent=args.indent))
        return 0


class TaskResultsByTaskCommand(SubParser):
    """[Task > task-results:by-task > TaskResults] get the past task results of given task"""

    subcommand = "task-results:by-task"

    def add_arguments(self, parser):
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args):
        print(TaskResults.by_task(Task.from_json(input())).to_json(indent=args.indent))
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
    TaskResultsCommand.attach_to(subparsers)

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
    HostsTaskResultsCommand.attach_to(subparsers)

    # Task runners commands
    TaskRunnersFilterCommand.attach_to(subparsers)
    TaskRunnersCountCommand.attach_to(subparsers)
    TaskRunnersSortCommand.attach_to(subparsers)
    TaskRunnersPipeCommand.attach_to(subparsers)

    TaskRunnersRunCommand.attach_to(subparsers)
    TaskRunnersHostsCommand.attach_to(subparsers)

    # Task results commands
    TaskResultsFilterCommand.attach_to(subparsers)
    TaskResultsCountCommand.attach_to(subparsers)
    TaskResultsSortCommand.attach_to(subparsers)
    TaskResultsPipeCommand.attach_to(subparsers)

    TaskResultsHostsCommand.attach_to(subparsers)
    TaskResultsByTaskCommand.attach_to(subparsers)

    args = parser.parse_args()

    if not hasattr(args, "_handler"):
        parser.print_usage()
        return 2

    try:
        return args._handler(args)
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        if args.debug:
            print(traceback.format_exc(), file=sys.stderr)
        return 1
