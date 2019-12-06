"""Viper Jobs Demo
~~~~~~~~~~~~~~~~~~
A viper job is a custom defined workflow. Unlike task, a job may contain
multiple tasks connected together with handlers, filters etc.

A job recieves a :py:class:`viper.collections.Hosts` object (read from stdin)
and should always return a :py:class:`viper.collections.Results` object. You can define arguments
which will be passed as `str` when you run it. You define what to do with the args
in the function body and then return the result.


Viper Job Definition Structure
------------------------------

.. code-block:: python

    def job_name(hosts, *args: str) -> Results:
        # Do something and return Results

You can run it with

.. code-block:: bash

    cat hosts.json | viper run job_name
"""

from viper import Hosts
from viper import Results
from viper.demo.handlers import export_csv
from viper.demo.tasks import ping
from viper.demo.tasks import remote_execute


def ping_then_execute(hosts: Hosts, command: str, resultsfile: str) -> Results:
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
        hosts.run_task(ping(), max_workers=50)
        .filter(lambda result: result.ok())
        .hosts()
        .run_task(remote_execute(), command, max_workers=50)
        .pipe(export_csv, resultsfile)
    )
