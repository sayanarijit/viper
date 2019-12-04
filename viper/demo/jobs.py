"""Viper Jobs Demo
~~~~~~~~~~~~~~~~~~
A viper job is a custom defined workflow. Unlike task, a job may contain
multiple tasks connected together with handlers, filters, callbacks etc.

A job receives the data as `str` from stdin which should be the
first argument of the job function. You can then define rest of the arguments
which will be passed as `str` when you run it. You define what to do with them
in the function body. You can return anything and that will be printed
in the stdout or you can return None if you don't want it to print anything.


Job definition structure:
-------------------------

.. code-block:: python

    def job_name(data: str, *args: str) -> object:
        # Do something and return anything

You can run it with

.. code-block:: bash

    viper run-job job_name
"""

from viper import Hosts
from viper import Results
from viper.demo.handlers import export_csv
from viper.demo.tasks import ping
from viper.demo.tasks import remote_execute


def ping_then_execute(data: str, command: str, resultsfile: str) -> Results:
    """First ping the hosts, then run the given command of pingable hosts.

    :param str data: Input data as `str`.
    :param str command: Command to execute.
    :param str resultsfile: Results will be saved in this file in CSV format.

    :rtype: viper.Results

    :example:

    .. code-block:: bash

        viper hosts viper.demo.hosts.group1 \\
                | viper run-job viper.demo.jobs.ping_then_execute "df -h" results.csv
    """
    return (
        Hosts.from_json(data)
        .run_task(ping(), max_workers=50)
        .filter(lambda result: result.ok())
        .hosts()
        .run_task(remote_execute(), command, max_workers=50)
        .pipe(export_csv, resultsfile)
    )
