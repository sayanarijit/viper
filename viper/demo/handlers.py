"""Viper Handlers Demo
~~~~~~~~~~~~~~~~~~~~~~
This module contains demo handlers for :py:meth:`viper.collections.pipe`.

Each handler is a function that expects a :py:class:`viper.collections.Collection`
instance as it's first argument.

You then define what to to with that object in that function body.

It's a best practice to return something that can be piped to other commands.
"""

from viper import Hosts
from viper import Results


def hosts_to_csv(hosts: Hosts) -> None:
    """Print the hosts in CSV format

    :param viper.collections.Hosts hosts: The groups of hosts.

    This handler expects a :py:class:`viper.collections.Hosts`
    object and prints the hosts in it in CSV format.

    .. note::
        This handler returns `None`. Thus we won't get any output
        that we can pipe to some other handler or command. This
        is just a demo. Best practice is to always return some
        instance of :py:class:`viper.collections.Collection`.
    """

    print("ip,hostname,domain,port,login_name,identity_file")
    for host in hosts.all():
        print(
            host.ip,
            host.hostname or "",
            host.domain or "",
            host.port or "",
            host.login_name or "",
            host.identity_file or "",
            sep=",",
        )


def print_status(results: Results) -> None:
    """Print the status of the results in the terminal.

    :param viper.collections.Results results: The groups of result.

    This handler expects a :py:class:`viper.collections.Result`
    object and prints the results in it in CSV format.

    .. note::
        This handler also returns `None`. Thus we won't get any output
        that we can pipe to some other handler or command. This
        is just a demo. Best practice is to always return some
        instance of :py:class:`viper.collections.Collection`.
    """

    for result in results.all():
        if result.errored():
            print(f"{result.task.name}: {result.host.ip} FAILED")
        else:
            print(f"{result.task.name}: {result.host.ip} PASSED")


def export_csv(results: Results, csv_file: str) -> Results:
    """Export the result to a CSV file location.

    :param viper.collections.Results results: The groups of result.

    This handler expects a :py:class:`viper.collections.Result`
    object and prints the results in it in CSV format.

    .. note::
        Unlike :py:class:`viper.demo.handlers.print_status`, this
        handlers returns an instance of `viper.collections.Results`
        object with can be piped to further commands and handlers.

        This is the recommended way to defile handlers.
    """

    import csv
    from time import ctime

    with open(csv_file, "w", newline="") as f:
        writer = csv.writer(f)
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

    # Let's return the result to stdout so that it can be piped to other commands
    return results
