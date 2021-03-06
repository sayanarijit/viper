"""The Viper Command-line Interface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Concept
^^^^^^^^^^^

After we define the tasks, actions, jobs etc. in the workspace,
we need a way to execute them. Dropping into a Python shell and
using the Python API is one way to do that. However, that might
not be the most preferred approach for everyone.

Viper provides a command-line interface through the ``viper``
command to interact with the Python API without dropping into
a Python shell.


Similarity Between the Python API and Command-line Interface
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The CLI interface closely follows the Python API. Each of the
subcommands with a colon (``:``) represents a method of a class or
object. When we run ``viper --help``, we can see the signatures of
the methods/subcommands.

For example, the subcommand ``viper hosts:from-file`` represents the
class method :py:meth:`viper.Hosts.from_file`,

In the help menu the signature of this subcommand is defined as
``[Hosts]`` which means that it returns a text (JSON)
representation of a :py:class:`~viper.Hosts`, object which can be
passed (piped) to another subcommand that expects the same via
standard input.

On the other hand, the ``results:order-by`` has the signature
``[Results -> Results]``. The subcommand represents the method
:py:meth:`viper.Results.order_by` and the signature
``[Results -> Results]`` means that the subcommand expects the text
(JSON) representation of a :py:class:`~viper.Results` object.


Example: Output Piping as Method Chaining
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    viper hosts:from-file("hosts.csv") \\
            | viper hosts:task task.ping \\
            | viper runners:run --max-workers 50 \\
            | viper results:final \\
            | viper results:order-by host.hostname host.ip \\
            | viper results:to-file results.csv \\
            | viper results:format "{host.hostname}: {stdout}"

In the above example, following things are happening:

- The ``hosts:from-file`` subcommand with signature
  ``[Hosts]`` returns the text representation of a :py:class:`~viper.Hosts` object.

- ``hosts:task`` reads the output of ``hosts:from-file`` from standard input
  as it has the signature of ``[Hosts -> Runners]`` and returns
  :py:class:`~viper.Runners`.

- Then the ``runners:run`` subcommand with signature ``[Runners -> Results]``
  reads the output of ``hosts:task`` from standard input and returns
  :py:class:`~viper.Results`.

- Finally ``results:format`` with signature ``[Results -> str]`` turns the
  :py:class:`~viper.Results` into a string which cannot be passed (piped) to any
  further subcommand.


The data flow diagram:

    ``hosts:from-file`` -> :py:class:`~viper.Hosts` | ``hosts:task`` -> :py:class:`~viper.Runners`
    | ``runners:run`` -> :py:class:`~viper.Results` | ``results:final`` -> :py:class:`~viper.Results`
    | ``results:order-by`` -> :py:class:`~viper.Results` | ``results:to-file`` ->
    :py:class:`~viper.Results` | ``results:format`` -> `str`

The above CLI example is equivalent to the following Python example:

.. code-block:: python

    from viper import Hosts
    import task

    print(
        Hosts.from_file("hosts.csv")
        .task(task.ping())
        .run(max_workers=50)
        .final()
        .order_by("host.hostname", "host.ip")
        .to_file("results.csv")
        .format("{host.hostname}: {stdout}")
    )

.. tip:: Refer to :doc:`getting_started` to see how ``task.ping`` and ``hosts.csv`` are written.


Defining Actions
^^^^^^^^^^^^^^^^

Actions are simple Python functions that can be invoked using the ``viper lets`` subcommand.

Example:

Define an action in ``action.py``:

.. code-block:: bash

    cat > action.py << EOF

.. code-block:: python

    def add_them(a, b):
        return int(a) + int(b)

.. code-block:: bash

    EOF

Now invoke the action:

.. code-block:: bash

    viper lets action.add_them 5 10

Output: ::

    15


Defining Viper Objects: Hosts, Task
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Similar to actions, we can also define functions that return an instance of
:py:class:`~viper.Task` or :py:class:`~viper.Hosts`. The ``*:from-func``
subcommands will invoke the function to get the object it returns.

Example: Define a host group in ``hosts.py``

.. code-block:: bash

    cat > hosts.py << EOF

.. code-block:: python

    from viper import Hosts, Host

    def group1():
        return Hosts.from_items(
            Host("192.168.0.11", hostname="host11"),
            Host("192.168.0.12", hostname="host12"),
            Host("192.168.0.13", hostname="host13"),
            Host("192.168.0.14", hostname="host14"),
            Host("192.168.0.15", hostname="host15"),
        )

.. code-block:: bash

    EOF

Get the hosts count in terminal:

.. code-block:: bash

    viper hosts hosts.group1 | viper hosts:count

Output: ::

    5


.. note::

    ``viper hosts`` is an alias of ``viper hosts:from-func``.
    Similarly, ``viper task`` is an alias of ``viper task:from-func``.

    However, ``viper results`` is an alias of ``viper results:from-history``
    as there's no reason to write results ourselves. It should come from
    the database.

    So there's no ``results:from-func``, neither ``runners:from-func`` and so on.


.. tip::

    Refer to :doc:`getting_started` to find the example of task and job definitions.


Defining Utilities: Handlers, Filters, Sort Keys
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Defining handlers, filters and sort keys are similar to
defining actions but the first argument of the defined function
is reserved for an instance of viper data type which
it receives from the standard input.

Example:

Define a general handler in ``handler.py`` that operates on
all :py:class:`~viper.collections.Items` instances:

.. code-block:: bash

    cat > handler.py << EOF

.. code-block:: python

    import sys

    def log_count(items, arg1):
        print(f"There are {items.count()} {arg1}.", file=sys.stderr)
        return items

.. code-block:: bash

    EOF

Use the handler:

.. code-block:: bash

    viper hosts hosts.group1 \\
            | viper hosts:pipe handler.log_count hosts \\
            | viper hosts:count

Output: ::

    There are 5 hosts.
    5


.. note:: Here ``arg1`` recieves the second argument passed to ``hosts:pipe`` i.e. "hosts".


Similarly filters and sort keys can be defined using functions having
the first argument reserved for the object it will operate on, and the
subsequent arguments for the variables that will be passed while invoking
the ``*:filter`` and ``*:sort`` subcommands.

However, we hardly will need to really define filters and sort keys like this
as most of the requirements of sorting and filtering should be satisfied with
the ``*:order-by`` and ``*:where`` subcommands respectively.
"""


from argparse import ArgumentParser
from argparse import Namespace
from pydoc import locate
from types import FunctionType
from viper import __version__
from viper import Hosts
from viper import Results
from viper import Runners
from viper import Task
from viper.cli_base import SubCommand
from viper.collections import Collection as ViperCollection
from viper.collections import WhereConditions
from viper.const import Config
from viper.db import ViperDB

import os
import sqlite3
import sys
import traceback
import typing as t

__all__ = ["func", "run"]


def func(objpath: str) -> FunctionType:
    """Resolved Python function from given string."""

    funcobj = locate(objpath)
    if not func:
        raise ValueError(f"could not resolve {repr(objpath)}.")

    if not isinstance(funcobj, FunctionType):
        raise ValueError(f"{repr(objpath)} is not a valid function.")

    return funcobj


class AutocompleteCommand(SubCommand):
    """generate the auto completion script"""

    name = "autocomplete"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "shell", help="the target shell", choices=["bash", "tcsh", "zsh", "fish"]
        )

    def __call__(self, args: Namespace) -> int:
        import subprocess

        try:
            import argcomplete  # noqa F401
        except ImportError:
            raise RuntimeError(
                '"argcomplete" is missing! run `pip install -U "viper-infra-commander[autocomplete]"`'
            )

        _shell = "bash" if args.shell == "zsh" else args.shell
        script = subprocess.run(
            ["register-python-argcomplete", "viper", "-s", _shell],
            stdout=subprocess.PIPE,
            check=True,
        ).stdout.decode("latin1")

        if args.shell == "zsh":
            script = f"autoload bashcompinit\nbashcompinit\n{script}"

        print(script)
        return 0


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


class LetsCommand(SubCommand):
    """perform any defined action"""

    name = "lets"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("action", type=func, help="action definition location")
        parser.add_argument("args", nargs="*", help="optional arguments for the action")

    def __call__(self, args: Namespace) -> int:
        res = args.action(*args.args)
        if res is not None:
            print("\n".join(map(str, res)) if isinstance(res, tuple) else res)
        return 0


class RunJobCommand(SubCommand):
    """[Hosts -> Results] run a job on the given hosts"""

    name = "run-job"
    aliases = ("run",)

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("job", type=func, help="job definition location")
        parser.add_argument("args", nargs="*", help="arguments to be passed to the job")
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        results = args.job(Hosts.from_json(input()), *args.args)
        if not isinstance(results, Results):
            raise ValueError(
                f"a job must return {Results} object but got {type(results)}"
            )
        print(results.to_json(indent=args.indent))
        return 0


class TaskFromFuncCommand(SubCommand):
    """[Task] get the task from a Python function location"""

    name = "task:from-func"
    aliases = ("task",)

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "func", type=Task.from_func, help="load task from a Python function"
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
    """[Hosts] get a group of hosts from a Python function location"""

    name = "hosts:from-func"
    aliases = ("hosts",)

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "func", type=Hosts.from_func, help="load hosts from a Python function"
        )
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(args.func.to_json(indent=args.indent))
        return 0


class HostsFromFileCommand(SubCommand):
    """[Hosts] get a group of hosts from a file"""

    name = "hosts:from-file"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("filepath")
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(Hosts.from_file(args.filepath).to_json(indent=args.indent))
        return 0


class HostsToFileCommand(SubCommand):
    """[Hosts -> Hosts] export the group of hosts to a file"""

    name = "hosts:to-file"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("filepath")
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(
            Hosts.from_json(input()).to_file(args.filepath).to_json(indent=args.indent)
        )
        return 0


class HostsTaskCommand(SubCommand):
    """[Hosts -> Runners] assign a task to each host"""

    name = "hosts:task"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "task", type=Task.from_func, help="load task from Python function"
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
            "task", type=Task.from_func, help="load task from a Python function"
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


class HostsOrderByCommand(SubCommand):
    """[Hosts -> Hosts] sort the hosts by the given properties"""

    name = "hosts:order-by"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "properties", nargs="*", help="items will be sorted in order"
        )
        parser.add_argument(
            "--reverse", action="store_true", help="reverse the order after sort"
        )
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(
            Hosts.from_json(input())
            .order_by(*args.properties, reverse=args.reverse)
            .to_json(indent=args.indent)
        )
        return 0


class HostsSortCommand(SubCommand):
    """[Hosts -> Hosts] sort the hosts by the given function"""

    name = "hosts:sort"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--key", type=func, help="the sorting function")
        parser.add_argument(
            "--reverse", action="store_true", help="reverse the order after sort"
        )
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(
            Hosts.from_json(input())
            .sort(key=args.key, reverse=args.reverse)
            .to_json(indent=args.indent)
        )
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
        obj: t.Any = Hosts.from_json(input()).pipe(args.handler, *args.args)

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
            "condition", choices=[o.value for o in WhereConditions],
        )
        parser.add_argument("values", nargs="*")
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(
            Hosts.from_json(input())
            .where(args.key, WhereConditions(args.condition), args.values)
            .to_json(indent=args.indent)
        )
        return 0


class HostsHeadCommand(SubCommand):
    """[Hosts -> Hosts] get the first 'n' hosts"""

    name = "hosts:head"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("-n", type=int, help="number of hosts", default=10)
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(Hosts.from_json(input()).head(args.n).to_json(indent=args.indent))
        return 0


class HostsTailCommand(SubCommand):
    """[Hosts -> Hosts] get the last 'n' hosts"""

    name = "hosts:tail"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("-n", type=int, help="number of hosts", default=10)
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(Hosts.from_json(input()).tail(args.n).to_json(indent=args.indent))
        return 0


class HostsResultsCommand(SubCommand):
    """[Hosts -> Results] get the past results of the hosts"""

    name = "hosts:results"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(Hosts.from_json(input()).results().to_json(indent=args.indent))
        return 0


class RunnersFromFileCommand(SubCommand):
    """[Runners] get a group of runners from a file"""

    name = "runners:from-file"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("filepath")
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(Runners.from_file(args.filepath).to_json(indent=args.indent))
        return 0


class RunnersToFileCommand(SubCommand):
    """[Runners -> Runners] export the group of runners to a file"""

    name = "runners:to-file"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("filepath")
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(
            Runners.from_json(input())
            .to_file(args.filepath)
            .to_json(indent=args.indent)
        )
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


class RunnersOrderByCommand(SubCommand):
    """[Runners -> Runners] sort the runners by the given properties"""

    name = "runners:order-by"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "properties", nargs="*", help="items will be sorted in order"
        )
        parser.add_argument(
            "--reverse", action="store_true", help="reverse the order after sort"
        )
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(
            Runners.from_json(input())
            .order_by(*args.properties, reverse=args.reverse)
            .to_json(indent=args.indent)
        )
        return 0


class RunnersSortCommand(SubCommand):
    """[Runners -> Runners] sort the runners by the given funtion"""

    name = "runners:sort"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--key", type=func)
        parser.add_argument(
            "--reverse", action="store_true", help="reverse the order after sort"
        )
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(
            Runners.from_json(input())
            .sort(key=args.key, reverse=args.reverse)
            .to_json(indent=args.indent)
        )
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
        obj: t.Any = Runners.from_json(input()).pipe(args.handler, *args.args)

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
        return 0


class RunnersWhereCommand(SubCommand):
    """[Runners -> Runners] select runners matching the given query"""

    name = "runners:where"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("key", help="property name/path of each item")
        parser.add_argument(
            "condition", choices=[o.value for o in WhereConditions],
        )
        parser.add_argument("values", nargs="*")
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(
            Runners.from_json(input())
            .where(args.key, WhereConditions(args.condition), args.values)
            .to_json(indent=args.indent)
        )
        return 0


class RunnersHeadCommand(SubCommand):
    """[Runners -> Runners] get the first 'n' runners"""

    name = "runners:head"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("-n", type=int, help="number of hosts", default=10)
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(Runners.from_json(input()).head(args.n).to_json(indent=args.indent))
        return 0


class RunnersTailCommand(SubCommand):
    """[Runners -> Runners] get the last 'n' runners"""

    name = "runners:tail"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("-n", type=int, help="number of hosts", default=10)
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(Runners.from_json(input()).tail(args.n).to_json(indent=args.indent))
        return 0


class RunnersRunCommand(SubCommand):
    """[Runners -> Results] run the assigned tasks"""

    name = "runners:run"

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


class RunnersHostsCommand(SubCommand):
    """[Runners -> Hosts] get the hosts from the runners"""

    name = "runners:hosts"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(Runners.from_json(input()).hosts().to_json(indent=args.indent))
        return 0


class ResultsFromHistoryCommand(SubCommand):
    """[Results] get the past results from database"""

    name = "results:from-history"
    aliases = ("results",)

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "--final",
            action="store_true",
            help="get the final results only (shortcut to `viper results | viper results:final`)",
        )
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(Results.from_history(final=args.final).to_json(indent=args.indent))
        return 0


class ResultsFromFileCommand(SubCommand):
    """[Results] get a group of results from a file"""

    name = "results:from-file"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("filepath")
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(Results.from_file(args.filepath).to_json(indent=args.indent))
        return 0


class ResultsToFileCommand(SubCommand):
    """[Results -> Results] export the group of results to a file"""

    name = "results:to-file"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("filepath")
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(
            Results.from_json(input())
            .to_file(args.filepath)
            .to_json(indent=args.indent)
        )
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


class ResultsOrderByCommand(SubCommand):
    """[Results -> Results] sort the results by the given properties"""

    name = "results:order-by"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "properties", nargs="*", help="items will be sorted in order"
        )
        parser.add_argument(
            "--reverse", action="store_true", help="reverse the order after sort"
        )
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(
            Results.from_json(input())
            .order_by(*args.properties, reverse=args.reverse)
            .to_json(indent=args.indent)
        )
        return 0


class ResultsSortCommand(SubCommand):
    """[Results -> Results] sort the results by the given function"""

    name = "results:sort"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--key", type=func)
        parser.add_argument(
            "--reverse", action="store_true", help="reverse the order after sort"
        )
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(
            Results.from_json(input())
            .sort(key=args.key, reverse=args.reverse)
            .to_json(indent=args.indent)
        )
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
        obj: t.Any = Results.from_json(input()).pipe(args.handler, *args.args)

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
        parser.add_argument("key", help="property name of each item")
        parser.add_argument(
            "condition",
            choices=[o.value for o in WhereConditions],
            help="condition to apply",
        )
        parser.add_argument("values", nargs="*", help="values for the key")
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(
            Results.from_json(input())
            .where(args.key, WhereConditions(args.condition), args.values)
            .to_json(indent=args.indent)
        )
        return 0


class ResultsHeadCommand(SubCommand):
    """[Results -> Results] get the first 'n' results"""

    name = "results:head"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("-n", type=int, help="number of hosts", default=10)
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(Results.from_json(input()).head(args.n).to_json(indent=args.indent))
        return 0


class ResultsTailCommand(SubCommand):
    """[Results -> Results] get the last 'n' results"""

    name = "results:tail"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("-n", type=int, help="number of hosts", default=10)
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(Results.from_json(input()).tail(args.n).to_json(indent=args.indent))
        return 0


class ResultsHostsCommand(SubCommand):
    """[Results -> Hosts] get the hosts from the results"""

    name = "results:hosts"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(Results.from_json(input()).hosts().to_json(indent=args.indent))
        return 0


class ResultsRunnersCommand(SubCommand):
    """[Results -> Runners] recreate the runners from the results"""

    name = "results:runners"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(Results.from_json(input()).runners().to_json(indent=args.indent))
        return 0


class ResultsReRunCommand(SubCommand):
    """[Results -> Results] recreate the runners from the results and run again"""

    name = "results:re-run"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--max-workers", type=int, default=Config.max_workers.value)
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(
            Results.from_json(input())
            .runners()
            .run(max_workers=args.max_workers)
            .to_json(indent=args.indent)
        )
        return 0


class ResultsByTaskCommand(SubCommand):
    """[Task -> Results] get the past results of given task"""

    name = "results:by-task"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(Results.by_task(Task.from_json(input())).to_json(indent=args.indent))
        return 0


class ResultsFinal(SubCommand):
    """[Results -> Results] get the final results only (ignoring the previous retries)"""

    name = "results:final"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("-i", "--indent", type=int, default=None)

    def __call__(self, args: Namespace) -> int:
        print(Results.from_json(input()).final().to_json(indent=args.indent))
        return 0


def run() -> int:
    parser = ArgumentParser(
        "viper", description=f"Viper Infrastructure Commander {__version__}"
    )
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument(
        "--debug",
        action="store_true",
        help="show traceback information when an exception is raised",
    )
    subparsers = parser.add_subparsers()

    # Autocomplete command
    AutocompleteCommand.attach_to(subparsers)

    # Init command
    InitCommand.attach_to(subparsers)

    # Init command
    LetsCommand.attach_to(subparsers)

    # Job run command
    RunJobCommand.attach_to(subparsers)

    # Task commands
    TaskFromFuncCommand.attach_to(subparsers)
    TaskResultsCommand.attach_to(subparsers)
    TaskFormatCommand.attach_to(subparsers)

    # Hosts commands
    HostsFromFuncCommand.attach_to(subparsers)

    HostsFromFileCommand.attach_to(subparsers)
    HostsToFileCommand.attach_to(subparsers)
    HostsWhereCommand.attach_to(subparsers)
    HostsFilterCommand.attach_to(subparsers)
    HostsOrderByCommand.attach_to(subparsers)
    HostsSortCommand.attach_to(subparsers)
    HostsCountCommand.attach_to(subparsers)
    HostsPipeCommand.attach_to(subparsers)
    HostsFormatCommand.attach_to(subparsers)
    HostsHeadCommand.attach_to(subparsers)
    HostsTailCommand.attach_to(subparsers)

    HostsTaskCommand.attach_to(subparsers)
    HostsRunTaskCommand.attach_to(subparsers)
    HostsResultsCommand.attach_to(subparsers)

    # Task runners commands
    RunnersFromFileCommand.attach_to(subparsers)
    RunnersToFileCommand.attach_to(subparsers)
    RunnersWhereCommand.attach_to(subparsers)
    RunnersFilterCommand.attach_to(subparsers)
    RunnersOrderByCommand.attach_to(subparsers)
    RunnersSortCommand.attach_to(subparsers)
    RunnersCountCommand.attach_to(subparsers)
    RunnersPipeCommand.attach_to(subparsers)
    RunnersFormatCommand.attach_to(subparsers)
    RunnersHeadCommand.attach_to(subparsers)
    RunnersTailCommand.attach_to(subparsers)

    RunnersRunCommand.attach_to(subparsers)
    RunnersHostsCommand.attach_to(subparsers)

    # Task results commands
    ResultsFromHistoryCommand.attach_to(subparsers)

    ResultsFromFileCommand.attach_to(subparsers)
    ResultsToFileCommand.attach_to(subparsers)
    ResultsWhereCommand.attach_to(subparsers)
    ResultsFilterCommand.attach_to(subparsers)
    ResultsOrderByCommand.attach_to(subparsers)
    ResultsSortCommand.attach_to(subparsers)
    ResultsCountCommand.attach_to(subparsers)
    ResultsPipeCommand.attach_to(subparsers)
    ResultsFormatCommand.attach_to(subparsers)
    ResultsHeadCommand.attach_to(subparsers)
    ResultsTailCommand.attach_to(subparsers)

    ResultsFinal.attach_to(subparsers)
    ResultsHostsCommand.attach_to(subparsers)
    ResultsRunnersCommand.attach_to(subparsers)
    ResultsReRunCommand.attach_to(subparsers)
    ResultsByTaskCommand.attach_to(subparsers)

    # Add the modules path
    sys.path.insert(0, os.path.realpath(Config.modules_path.value))

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

    try:
        # Add support for auto completion
        import argcomplete

        argcomplete.autocomplete(parser)
    except ImportError:
        pass

    args = parser.parse_args()

    if not hasattr(args, "_handler"):
        parser.print_usage()
        return 1

    try:
        return int(args._handler(args))
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        if args.debug:
            print(traceback.format_exc(), file=sys.stderr)
        return 1
