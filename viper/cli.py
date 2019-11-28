from argparse import ArgumentParser
import sys
from viper import Hosts, Task, TaskRunners
from pydoc import locate
import typing as t
from viper import __version__
import traceback


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
                        alias, help=f"alias of {repr(cls.subcommand)}."
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


class HostsFromObj(SubParser):
    """get a list of hosts from a Python object location"""

    subcommand = "hosts:from_obj"
    aliases = ("from_obj",)

    def add_arguments(self, parser):
        parser.add_argument(
            "obj", type=Hosts.from_obj, help=Hosts.from_obj.__doc__.lower()
        )
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args) -> int:
        print(args.obj.to_json(indent=args.indent))
        return 0


class HostsFromFileCommand(SubParser):
    """get a list of hosts from a file"""

    subcommand = "hosts:from_file"
    aliases = ("from_file",)

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
    """assign a task to the given list of hosts"""

    subcommand = "hosts:task"
    aliases = ("task",)

    def add_arguments(self, parser):
        parser.add_argument(
            "task", type=Task.from_obj, help=Task.from_obj.__doc__.lower()
        )
        parser.add_argument("-", "--stdin", action="store_true")
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args) -> int:

        task = args.task

        if args.stdin:
            data = input()
            print(Hosts.from_json(data).task(args.task).to_json(indent=args.indent))
            return 0

        print(task.to_json())

        return 0


class TasksRunCommand(SubParser):
    """run the assigned tasks"""

    subcommand = "tasks:run"
    aliases = ("run",)

    def add_arguments(self, parser):
        parser.add_argument("-", "--stdin", action="store_true")
        parser.add_argument("--max-workers", type=int, default=0)
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args) -> int:

        if not args.stdin:
            raise RuntimeError("use `-` or `--stdin`")

        data = input()
        print(
            TaskRunners.from_json(data)
            .run(max_workers=args.max_workers)
            .to_json(indent=args.indent)
        )
        return 0


class HostsFilterCommand(SubParser):
    """filter hosts by custom logic"""

    subcommand = "hosts:filter"
    aliases = ("filter",)

    def add_arguments(self, parser):
        parser.add_argument("filter", type=func)
        parser.add_argument("-", "--stdin", action="store_true")
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args):

        if not args.stdin:
            print(f"{repr(args.filter)} {args.filter.__doc__}")
            return 0

        data = input()
        print(Hosts.from_json(data).filter(args.filter).to_json(indent=args.indent))
        return 0


def run() -> int:
    parser = ArgumentParser("viper", description="Viper CLI")
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("--debug", action="store_true")
    subparsers = parser.add_subparsers()

    HostsFromFileCommand.attach_to(subparsers)
    HostsFromObj.attach_to(subparsers)
    HostsTaskCommand.attach_to(subparsers)
    HostsFilterCommand.attach_to(subparsers)
    TasksRunCommand.attach_to(subparsers)

    args = parser.parse_args()

    try:
        return args.handler(args)
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        if args.debug:
            print(traceback.format_exc(), file=sys.stderr)
        return 1
