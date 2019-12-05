"""Viperfile Demo
~~~~~~~~~~~~~~~~~
This module is an example of the structure of ``viperfile.py``.

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
            viper @myproj:hosts_by name vele | \\
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
    """Log the command before run."""

    command = runner.task.command_factory(runner.host, *runner.args)
    print(runner.host.ip, command, file=sys.stderr, sep=": ")


def log_status_callback(result: Result) -> None:
    """Log the status after task run."""

    if result.ok():
        print(result.host.ip, "OK", file=sys.stderr, sep=": ")
        return

    print(result.host.ip, "FAILED", file=sys.stderr, sep=": ")


@myproj.hostgroup(
    args=[
        arg("-f", "--file", type=FileType("r"), default="hosts.json"),
        arg("-I", "--identity_file", default="/root/.ssh/id_rsa.pub"),
    ]
)
def allhosts(args) -> Hosts:
    """Get all the myproj hosts."""

    data = json.load(args.file)

    return Hosts.from_items(
        *(
            Host(
                ip=d["ip"],
                hostname=d["name"],
                login_name="root",
                identity_file=args.identity_file,
                meta=tuple(d.items()),
            )
            for d in data
        )
    )


@myproj.filter(objtype=Hosts, args=[arg("key"), arg("val")])
def hosts_by(host: Host, args: Namespace) -> bool:
    """Filter hosts by key and metadata"""

    return str(dict(host.meta)[args.key]) == args.val


@myproj.filter(objtype=Results, args=[arg("key"), arg("val")])
def results_by(result: Result, args: Namespace) -> bool:
    """Filter hosts by IP address"""

    return (
        hasattr(result, args.key) and str(getattr(result, args.key)).strip() == args.val
    )


@myproj.handler(fromtype=Hosts, totype=Hosts, args=[arg("file", type=FileType("w"))])
def hosts2csv(hosts: Hosts, args: Namespace) -> Hosts:
    """Export csv formatted hosts to file"""

    if hosts.count() > 0:
        writer = csv.writer(args.file)
        writer.writerow(list(dict(hosts[0].meta).keys()))
        for host in hosts.all():
            writer.writerow(list(dict(host.meta).values()))
    args.file.flush()
    args.file.close()

    # Printing JSON to terminal to that it can be piped to further commands
    return hosts


@myproj.handler(
    fromtype=Results, totype=Results, args=[arg("file", type=FileType("w"))]
)
def results2csv(results: Results, args: Namespace) -> Results:
    """Export csv formatted results to file"""

    if results.count() > 0:
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


def app_version_command(host: Host, app: str) -> t.Sequence[str]:
    return remote_exec_command(host, f"{app} --version")


@myproj.job(
    fromtype=Hosts,
    totype=Results,
    args=[
        arg("app"),
        arg("file", type=FileType("w"), help="CSV file path for the result"),
        arg("--max-workers", default=0, type=int),
    ],
)
def app_version(hosts: Hosts, args: Namespace) -> Results:
    """Get application version."""
    return hosts.run_task(
        Task(
            "Get app version",
            app_version_command,
            timeout=10,
            retry=3,
            pre_run=log_command_callback,
            post_run=log_status_callback,
        ),
        args.app,
        max_workers=args.max_workers,
    ).pipe(lambda results: results2csv(results, args))


def update_via_apt_command(host: Host, app: str) -> t.Sequence[str]:
    return remote_exec_command(host, f"cronly --version && echo updating {app}")


@myproj.job(
    fromtype=Hosts,
    totype=Results,
    args=[
        arg("app"),
        arg("version"),
        arg("file", type=FileType("w"), help="CSV file path for the result"),
        arg("--max-workers", default=0, type=int),
    ],
)
def update_via_apt(hosts: Hosts, args: Namespace) -> Results:
    """Update application via apt."""
    return (
        hosts.run_task(
            Task(
                "Get app version",
                app_version_command,
                timeout=10,
                retry=3,
                pre_run=log_command_callback,
                post_run=log_status_callback,
            ),
            args.app,
            max_workers=args.max_workers,
        )
        .filter(lambda results: results.ok() and args.version not in results.stdout)
        .hosts()
        .run_task(
            Task(
                "Update app version",
                update_via_apt_command,
                timeout=300,
                retry=5,
                pre_run=log_command_callback,
                post_run=log_status_callback,
            ),
            args.app,
            max_workers=args.max_workers,
        )
        .pipe(lambda results: results2csv(results, args))
    )
