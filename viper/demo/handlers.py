from viper import TaskResults
from viper.demo import __doc__


def print_status(results: TaskResults) -> str:
    """Print the status of the results in the terminal."""

    for result in results.all():
        if result.errored():
            print(f"{result.task.name}: {result.host.ip} FAILED")
        else:
            print(f"{result.task.name}: {result.host.ip} PASSED")
