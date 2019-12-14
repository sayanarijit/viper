"""Viperfile Demo
~~~~~~~~~~~~~~~~~
A ``viperfile.py`` let's you extend the Viper CLI commands and options.
The host groups, filters, handlers, jobs etc. you define in the file,
will be added to the Viper CLI's command list for easy access and documentation.

The ``viperfile.py`` file should be in your current working directory.


Example Viperfile CLI Usage
---------------------------

.. code-block:: bash

    viper --help

    viper @myproj:allhosts --help

    viper @myproj:allhosts | \\
            viper @myproj:hosts_by ip 127.0.0.1 | \\
            viper @myproj:remote_exec "df -h" results.csv --max-workers 50

.. tip:: See :py:mod:`viper.project` for more details on available project APIs.
"""

from argparse import FileType
from argparse import Namespace
from time import ctime
from viper import Host
from viper import Hosts
from viper import Result
from viper import Results
from viper import Runner
from viper import Task
from viper.project import arg
from viper.project import Project

import csv
import json
import sys
import typing as t

myproj = Project(prefix="myproj")


def log_command_callback(runner: Runner) -> None:
    """Log the command before run.

    :param viper.collections.Runner runner: Pre-run callbacks are given this object.
    :rtype: None
    """

    command = runner.task.command_factory(runner.host, *runner.args)
    print(runner.host.ip, command, file=sys.stderr, sep=": ")


def log_status_callback(result: Result) -> None:
    """Log the status after task run.

    :param viper.collections.Result result: Post-run callbacks are given this object.
    :rtype: None
    """

    if result.ok():
        print(result.host.ip, "OK", file=sys.stderr, sep=": ")
        return

    print(result.host.ip, "FAILED", file=sys.stderr, sep=": ")


def text_stripper(txt: str) -> str:
    """This is a stdout/stderr processor that strips the given text.

    :param str txt: The text to be stripped
    :rtype: str
    """
    return txt.strip()


@myproj.hostgroup(
    args=[
        arg("-f", "--file", type=FileType("r"), default="hosts.json"),
        arg("-I", "--identity_file", default="/root/.ssh/id_rsa.pub"),
    ]
)
def allhosts(args: Namespace) -> Hosts:
    """Get all the myproj hosts

    :param Namespace args: The parsed arguments.
    :rtype: viper.collections.Hosts
    :example:

    .. code-block:: bash

        viper @myproj:allhosts
    """

    data = json.load(args.file)

    return Hosts.from_items(
        Host(
            ip=d["ip"],
            hostname=d["name"],
            login_name="root",
            identity_file=args.identity_file,
            meta=tuple(d.items()),
        )
        for d in data
    )


@myproj.filter(objtype=Hosts, args=[arg("key"), arg("val")])
def hosts_by(host: Host, args: Namespace) -> bool:
    """Filter hosts by key and metadata

    :param viper.collections.Host host: Host filters are given this object.
    :param Namespace args: The parsed arguments.
    :rtype: bool
    :example:

    .. code-block:: bash

        viper @myproj:allhosts \\
                | viper @myproj:hosts_by ip 1.1.1.1

    .. note: We can also use the `hosts:where` command.
    """

    return str(dict(host.meta)[args.key]) == args.val


@myproj.filter(objtype=Results, args=[arg("key"), arg("val")])
def results_by(result: Result, args: Namespace) -> bool:
    """Filter hosts by IP address

    :param viper.collections.Result result: Result filters are given this object.
    :param Namespace args: The parsed arguments.
    :rtype: bool
    :example:

    .. code-block:: bash

        viper results \\
                | viper @myproj:results_by returncode 0

    .. note: We can also use the `results:where` command.
    """

    return (
        hasattr(result, args.key) and str(getattr(result, args.key)).strip() == args.val
    )


@myproj.handler(fromtype=Hosts, totype=Hosts, args=[arg("file", type=FileType("w"))])
def hosts2csv(hosts: Hosts, args: Namespace) -> Hosts:
    """Export the hosts to a CSV file

    :param viper.collections.Hosts hosts: This will be read from stdin.
    :param Namespace args: The parsed arguments.
    :rtype: viper.collections.Hosts
    :example:

    .. code-block:: bash

        viper @myproj:allhosts \\
                | viper @myproj:hosts2csv hosts.csv
    """

    writer = csv.writer(args.file)
    writer.writerow(list(dict(hosts.all()[0].meta).keys()))
    for host in hosts.all():
        writer.writerow(list(dict(host.meta).values()))
    args.file.flush()
    args.file.close()

    return hosts


@myproj.handler(
    fromtype=Results, totype=Results, args=[arg("file", type=FileType("w"))]
)
def results2csv(results: Results, args: Namespace) -> Results:
    """Export the results to a CSV file

    :param viper.collections.Results results: This will be read from stdin.
    :param Namespace args: The parsed arguments.
    :rtype: viper.collections.Results
    :example:

    .. code-block:: bash

        viper results \\
                | viper @myproj:results2csv results.csv
    """

    writer = csv.writer(args.file)
    writer.writerow(
        [
            "task",
            "ip",
            "hostname",
            "command",
            "returncode",
            "success",
            "start",
            "end",
            "retry",
            "stdout",
            "stderr",
        ]
    )

    for r in results.all():
        writer.writerow(
            [
                r.task.name,
                r.host.ip,
                r.host.hostname,
                r.command,
                r.returncode,
                r.ok(),
                ctime(r.start),
                ctime(r.end),
                r.retry,
                r.stdout,
                r.stderr,
            ]
        )
    args.file.flush()
    args.file.close()

    # Printing JSON to terminal to that it can be piped to further commands
    return results


def remote_exec_command(host: Host, command: str) -> t.Sequence[str]:
    """Command for the `remote_exec` job

    :param viper.collections.Host host: This will be passed by the task.
    :param str command: The command to execute.
    :rtype: tuple
    """
    if not host.login_name:
        raise ValueError(f"{host}: 'login_name' is not set")

    if not host.identity_file:
        raise ValueError(f"{host}: 'identity_file' is not set")

    return (
        "ssh",
        "-l",
        host.login_name,
        "-i",
        host.identity_file,
        "-o",
        "StrictHostKeyChecking=no",
        host.ip,
        command,
    )


@myproj.job(
    args=[
        arg("command"),
        arg("file", type=FileType("w"), help="CSV file path for the result"),
        arg("--max-workers", default=0, type=int),
    ],
)
def remote_exec(hosts: Hosts, args: Namespace) -> Results:
    """Execute command on a remote host via SSH

    :param viper.collections.Host host: This will be read from stdin.
    :param Namespace args: The parsed arguments.
    :rtype: viper.collections.Results
    :example:

    .. code-block:: bash

        viper @myproj:allhosts \\
                | viper @myproj:remote_exec "df -h" results.csv --max-workers 50
    """
    return (
        hosts.task(
            Task(
                "Remote execute",
                remote_exec_command,
                timeout=300,
                retry=0,
                pre_run=log_command_callback,
                post_run=log_status_callback,
            ),
            args.command,
        )
        .run(max_workers=args.max_workers)
        .final()  # Filter only the final results
        .pipe(lambda results: results2csv(results, args))
    )


def app_version_command(host: Host, app: str) -> t.Sequence[str]:
    """Command for the `app_version` job

    :param viper.collections.Host host: This will be given by the task.
    :param str app: The application binary name.
    :rtype: tuple
    """
    return remote_exec_command(host, f"{app} --version")


@myproj.job(
    args=[
        arg("app"),
        arg("file", type=FileType("w"), help="CSV file path for the result"),
        arg("--max-workers", default=0, type=int),
    ],
)
def app_version(hosts: Hosts, args: Namespace) -> Results:
    """Gets the version of an application installed on a remote host

    :param viper.collections.Host: Jobs are given hosts read from stdin.
    :param Namespace args: The parsed arguments.
    :rtype: viper.collections.Results
    :example:

    .. code-block:: bash

        viper @myproj:allhosts \\
                | viper @myproj:app_version python results.csv --max-workers 50
    """
    return (
        hosts.task(
            Task(
                "Get app version",
                app_version_command,
                timeout=10,
                retry=3,
                pre_run=log_command_callback,
                post_run=log_status_callback,
            ),
            args.app,
        )
        .run(max_workers=args.max_workers)
        .final()  # Filter only the final results
        .pipe(lambda results: results2csv(results, args))
    )


def install_via_apt_command(host: Host, app: str, version: str) -> t.Sequence[str]:
    """Generates command for the `install_via_apt` job

    :param viper.collections.Host host: This will be given by the task.
    :param str app: The target application name.
    :param str app: The target application version.
    :rtype: tuple
    """
    return remote_exec_command(host, f"apt-get install -f {app}-{version}")


@myproj.job(
    args=[
        arg("app"),
        arg("version"),
        arg("file", type=FileType("w"), help="CSV file path for the result"),
        arg("--max-workers", default=0, type=int),
    ],
)
def install_via_apt(hosts: Hosts, args: Namespace) -> Results:
    """First checks if the specific version of app is installed, if not, installs it

    :param viper.collections.Host host: This will be given by the task.
    :param Namespace args: The parsed arguments.
    :rtype: viper.collections.Results
    :example:

    .. code-block::

        viper @myproj:allhosts \\
                | viper @myproj:install_via_apt python 3.8.0 results.csv --max-workers 50
    """
    return (
        hosts.task(
            Task(
                "Get app version",
                app_version_command,
                timeout=10,
                retry=3,
                pre_run=log_command_callback,
                post_run=log_status_callback,
            ),
            args.app,
        )
        .run(max_workers=args.max_workers)
        .final()  # Filter only the final results
        .filter(lambda results: results.ok() and args.version not in results.stdout)
        .hosts()
        .task(
            Task(
                "Install app with specific version",
                install_via_apt_command,
                timeout=300,
                retry=5,
                pre_run=log_command_callback,
                post_run=log_status_callback,
            ),
            args.app,
            args.version,
        )
        .run(max_workers=args.max_workers)
        .final()  # Filter only the final results
        .pipe(lambda results: results2csv(results, args))
    )


@myproj.action()
def get_triggers(args: Namespace) -> t.Sequence[float]:
    """Get the unique trigger times from history"""

    results = Results.from_history(final=True).all()
    triggers = set(x.trigger_time for x in results)
    return tuple(sorted(triggers))
