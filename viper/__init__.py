__author__ = "Arijit Basu"
__description__ = "Viper provides a simple API (Python and CLI) to easily manage large infrastructures."
__email__ = "sayanarijit@gmail.com"
__homepage__ = "https://github.com/sayanarijit/viper"
__license__ = "MIT"
__version__ = "v0.28.3"

from viper.collections import Host  # noqa: F401
from viper.collections import Hosts  # noqa: F401
from viper.collections import meta  # noqa: F401
from viper.collections import Result  # noqa: F401
from viper.collections import Results  # noqa: F401
from viper.collections import Runner  # noqa: F401
from viper.collections import Runners  # noqa: F401
from viper.collections import Task  # noqa: F401
from viper.collections import WhereConditions  # noqa: F401

__all__ = [
    "meta",
    "Host",
    "Hosts",
    "Result",
    "Results",
    "Runner",
    "Runners",
    "Task",
    "WhereConditions",
]
__doc__ = f"""{__description__}

::

     ▄   ▄█ █ ▄▄  ▄███▄   █▄▄▄▄   ▄█    ▄   ▄████  █▄▄▄▄ ██     ▄█▄    ████▄ █▀▄▀█ █▀▄▀█ ██      ▄   ██▄   ▄███▄   █▄▄▄▄
      █  ██ █   █ █▀   ▀  █  ▄▀   ██     █  █▀   ▀ █  ▄▀ █ █    █▀ ▀▄  █   █ █ █ █ █ █ █ █ █      █  █  █  █▀   ▀  █  ▄▀
 █     █ ██ █▀▀▀  ██▄▄    █▀▀▌    ██ ██   █ █▀▀    █▀▀▌  █▄▄█   █   ▀  █   █ █ ▄ █ █ ▄ █ █▄▄█ ██   █ █   █ ██▄▄    █▀▀▌
  █    █ ▐█ █     █▄   ▄▀ █  █    ▐█ █ █  █ █      █  █  █  █   █▄  ▄▀ ▀████ █   █ █   █ █  █ █ █  █ █  █  █▄   ▄▀ █  █
   █  █   ▐  █    ▀███▀     █      ▐ █  █ █  █       █      █   ▀███▀           █     █     █ █  █ █ ███▀  ▀███▀     █
    █▐        ▀            ▀         █   ██   ▀     ▀      █                   ▀     ▀     █  █   ██                ▀
    ▐                                                     ▀                               ▀


Getting Started
~~~~~~~~~~~~~~~

Installation
^^^^^^^^^^^^

.. code-block:: bash

    pip install -U viper-infra-commander

    # Or install with batteries included

    pip install -U "viper-infra-commander[batteries]"


Initialization
^^^^^^^^^^^^^^

Viper needs to initialize a SQLite DB in the present working directory (the workspace).

.. code-block:: bash

    # (Optional) enable tab auto completion
    eval "$(viper autocomplete $(basename $SHELL))"


    # Initialize SQLite DB
    viper init -f


Viper in Action (Basic Mode)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Define a set of hosts in csv format (json and yml are also supported) in ``hosts.csv``:

.. code-block:: bash

    cat > hosts.csv << EOF

.. code-block::

    ip,hostname,login_name,identity_file
    192.168.0.11,host11,root,/root/.ssh/id_rsa.pub
    192.168.0.12,host12,root,/root/.ssh/id_rsa.pub
    192.168.0.13,host13,root,/root/.ssh/id_rsa.pub
    192.168.0.14,host14,root,/root/.ssh/id_rsa.pub
    192.168.0.15,host15,root,/root/.ssh/id_rsa.pub

.. code-block:: bash

    EOF


Define a task in ``task.py``:

.. code-block:: bash

    cat > task.py << EOF

.. code-block:: python

    from viper import Task

    def ping_command(host):
        return "ping", "-c", "1", host.ip

    def ping():
        return Task(
            name="Ping once",
            command_factory=ping_command
        )

.. code-block:: bash

    EOF

Perform the following actions:

- Run the ping task on the set of hosts in parallel with 5 workers
- Then filter only the results where the task failed
- Re-run the task on the filtered set of hosts
- Store all the results

.. code-block:: bash

    viper hosts:from-file hosts.csv \\
            | viper hosts:run-task task.ping --max-worker 5 \\
            | viper results:where returncode IS_NOT 0 \\
            | viper results:re-run --indent 4


The results are stored in the DB as history.
To see the stdout of the final results from history:

.. code-block:: bash

    viper results \\
            | viper results:final \\
            | viper results:format "{{host.hostname}}: {{stdout}}"


Export the results to a csv file:

.. code-block:: bash

    viper results --final \\
            | viper results:to-file results.csv --indent 4


Define a job using the Python API (CLI and Python API are almost similar):

.. code-block:: bash

    cat > job.py << EOF

.. code-block:: python

    from viper import WhereConditions
    from task import ping

    def ping_and_export(hosts):
        return (
            hosts.task(ping())
            .run(max_workers=5)
            .final()
            .to_file("results.csv")
        )

.. code-block:: bash

    EOF


Run the job using CLI:

.. code-block:: bash

    viper hosts:from-file hosts.csv \\
            | viper run job.ping_and_export \\
            | viper results:format "{{host.hostname}}: {{stdout}}"


Viperfile in Action (Advanced Mode)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Define a project with custom subcommands in viperfile:

.. code-block:: bash

    cat > viperfile.py << EOF

.. code-block:: python


    from viper import Hosts, Task
    from viper.project import Project, arg


    foo = Project(prefix="foo")


    @foo.hostgroup(args=[arg("-f", "--file", default="hosts.csv")])
    def allhosts(args):
        return Hosts.from_file(args.file)


    def remote_exec_command(host, command):
        return (
            "ssh",
            "-i",
            host.identity_file,
            "-l",
            host.login_name,
            "-p",
            str(host.port),
            "-o",
            "StrictHostKeyChecking=no",
            "-o",
            "PubkeyAuthentication=yes",
            host.ip,
            command,
        )


    @foo.job(
        args=[
            arg("command", help="command to execute"),
            arg("-w", "--workers", type=int, default=1),
        ]
    )
    def remote_exec(hosts, args):
        return (
            hosts.task(
                Task(
                    name="Remote execute command",
                    command_factory=remote_exec_command,
                    timeout=5,
                ),
                args.command,
            )
            .run(max_workers=args.workers)
            .final()
        )

.. code-block:: bash

    EOF


See the auto generated custom subcommands:

.. code-block:: bash

    viper --help
    # Will show the subcommands: "@foo:allhosts" and "@foo:remote_exec"


Run the job, export the results in a file, and format the output:

.. code-block:: bash

    viper @foo:allhosts \\
            | viper @foo:remote_exec "uname -a" --workers 5 \\
            | viper results:to-file results.csv \\
            | viper results:format "{{task.name}} [{{host.hostname}}]: {{returncode}}: {{stdout}}"
"""
