"""Viper tasks
--------------
A viper task can be defined using `viper.Task(name, command_factory)`
where name is the name of the task which should help easily recognise the
purpose of the task and `command_factory` generates the command (see `viper.demo.commands`).

We can also pass optional arguments `timeout`, `retry`, `pre_run` and `post_run`.

`timeout` is applied to the duration of execution of the command generated
by the `command_factory`. If `retry` is more than 0, the task will re-run itself.

`pre_run` and `post_run` are callbacks. `pre_run` is run just before the command
if about to execute. `post_run` is run after the result of the task is saved in the DB
but before retry in case the command fails (see `viper.demo.callbacks`).
"""

from viper import Task
from viper.demo.callbacks import log_command
from viper.demo.callbacks import log_status
from viper.demo.commands import df_command
from viper.demo.commands import ping_command
from viper.demo.commands import remote_execute_command


def ping() -> Task:
    """Ping the host one time"""

    return Task(
        "Ping",
        ping_command,
        timeout=5,
        retry=1,
        pre_run=log_command,
        post_run=log_status,
    )


def remote_execute() -> Task:
    """Execute a command on the host"""

    return Task(
        "Remote execute",
        remote_execute_command,
        timeout=300,
        retry=0,
        pre_run=log_command,
        post_run=log_status,
    )


def disk_usage() -> Task:
    """Get the local disk usage of the host"""

    return Task(
        name="Disk Usage",
        command_factory=df_command,
        timeout=5,
        retry=1,
        pre_run=log_command,
        post_run=log_status,
    )
