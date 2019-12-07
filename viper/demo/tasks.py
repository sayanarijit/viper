"""Viper Tasks Demo
~~~~~~~~~~~~~~~~~~~
A :py:class:`viper.Task` contains the necessary things that :py:class:`viper.Runner` uses to
generate the command to execute, call the `pre run` and `post run` callbacks,
format the `stdout` and `stderr`, and also time out and retry the execution.

.. tip:: See :py:class:`viper.collections.Task` for more details.
"""

from viper import Task
from viper.demo.callbacks import log_command
from viper.demo.callbacks import log_status
from viper.demo.commands import df_command
from viper.demo.commands import ping_command
from viper.demo.commands import remote_execute_command
from viper.demo.processors import text_stripper


def ping() -> Task:
    """Ping the host one time.

    :rtype: viper.collections.Task
    :example:

    Run the task

    .. code-block:: bash

        viper hosts viper.demo.hosts.group1 \\
                | viper hosts:run-task viper.demo.tasks.ping --max-workers 50 -i 2

    Output

    ::

        8.8.8.8: ('ping', '-c', '1', '8.8.8.8')
        8.8.8.8: OK
        127.0.0.1: ('ping', '-c', '1', '127.0.0.1')
        127.0.0.1: FAILED
        127.0.0.1: ('ping', '-c', '1', '127.0.0.1')
        ...
    """

    return Task(
        "Ping",
        ping_command,
        stdout_processor=text_stripper,
        stderr_processor=text_stripper,
        timeout=5,
        retry=1,
        pre_run=log_command,
        post_run=log_status,
    )


def remote_execute() -> Task:
    """Execute a command on the host.

    :rtype: viper.collections.Task
    :example:

    Run the task

    .. code-block:: bash

        viper hosts viper.demo.hosts.group1 \\
                | viper hosts:run-task viper.demo.tasks.remote_execute "df -h" --max-workers 50 -i 2
    """

    return Task(
        "Remote execute",
        remote_execute_command,
        stdout_processor=text_stripper,
        stderr_processor=text_stripper,
        timeout=300,
        retry=0,
        pre_run=log_command,
        post_run=log_status,
    )


def disk_usage() -> Task:
    """Get the local disk usage of the host

    :rtype: viper.collections.Task
    :example:

    Run the task

    .. code-block:: bash

        viper hosts viper.demo.hosts.group1 \\
                | viper hosts:run-task viper.demo.tasks.disk_usage --max-workers 50 -i 2
    """

    return Task(
        name="Disk Usage",
        command_factory=df_command,
        stdout_processor=text_stripper,
        stderr_processor=text_stripper,
        timeout=5,
        retry=1,
        pre_run=log_command,
        post_run=log_status,
    )
