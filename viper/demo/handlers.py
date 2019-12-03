from viper import Hosts
from viper import Results

"""Viper handlers."""


def hosts_to_csv(hosts: Hosts) -> None:
    """Print the hosts in CSV format"""

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
    """Print the status of the results in the terminal."""

    for result in results.all():
        if result.errored():
            print(f"{result.task.name}: {result.host.ip} FAILED")
        else:
            print(f"{result.task.name}: {result.host.ip} PASSED")

    # Since this handler returns None, it won't print
    # anything else in the terminal.


def export_csv(results: Results, csv_file: str) -> Results:
    """Export the result to a CSV file location"""

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
