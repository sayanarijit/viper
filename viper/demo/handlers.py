from viper import Results
from viper.demo import __doc__


def print_status(results: Results) -> None:
    """Print the status of the results in the terminal."""

    for result in results.all():
        if result.errored():
            print(f"{result.task.name}: {result.host.ip} FAILED")
        else:
            print(f"{result.task.name}: {result.host.ip} PASSED")


def export_csv(results: Results, csv_file: str) -> None:
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

        # Let's print the result to stdout so that it can be
        # piped to other commands
        print(results.to_json())
