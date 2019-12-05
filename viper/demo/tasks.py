'''Viper Tasks Demo
~~~~~~~~~~~~~~~~~~~
A :py:class:`viper.Task` contains the necessary things that :py:class:`viper.Runner` uses to
generate the command to execute, call the `pre run` and `post run` callbacks,
format the `stdout` and `stderr`, and also time out and retry the execution.

.. tip:: See :py:class:`viper.Task` for more details.


Viper Task Definition Structure
-------------------------------
Here's an example of a viper task definition.

.. code-block:: python

    def remote_execute() -> Task:
        """Execute a command on the host"""

        return Task(
            name="Execute Command Remotely",
            command_factory=remote_execute_command,
            timeout=5,
            retry=1,
            pre_run=log_command,
            post_run=log_status,
        )

Where the `remote_execute_command` is defined as

.. code-block:: python

    def remote_execute_command(host: Host, command: str) -> t.Sequence[str]:
        """Basic SSH command generator."""

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


Task CLI Usage Example
----------------------

.. code-block:: bash

    # See he task CLI options
    viper task --help

    # See the task details
    viper task viper.demo.tasks.remote_execute --indent 4

    # Execute the task
    viper hosts viper.demo.hosts.group1 | \\
            viper hosts:task viper.demo.tasks.remote_execute "df -lh" | \\
            viper runners:run --indent 4

    # Or skip a step
    viper hosts viper.demo.hosts.group1 | \\
            viper hosts:run-task viper.demo.tasks.remote_execute "df -lh" -i 4

.. note::
    The `pre_run` and `post_run` arguments are callbacks that are run before and after
    the command execution respectively.

    See :py:func:`viper.demo.callbacks.log_command` and :py:func:`viper.demo.callbacks.log_status`.
'''

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
