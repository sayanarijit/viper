"""Viper CLI Examples
=====================

Initialize current workspace (creates a `viperdb.sqlite3` file)
---------------------------------------------------------------

    viper init -f


Load hosts from file
--------------------

    viper hosts:from-file tests/data/hosts.csv --indent 4

    # or with a custom loader

    viper hosts:from-file tests/data/hosts.json --loader viper.demo.loaders.json --indent 4


Load hosts from a Python function
---------------------------------

    viper hosts viper.demo.hosts.group1 --indent 4


Count the number of hosts
-------------------------

    viper hosts viper.demo.hosts.group1 | viper hosts:count


Sort the hosts by custom logic
------------------------------

    viper hosts viper.demo.hosts.group1 | viper hosts:sort --key viper.demo.sort.by_ip -i 4


Pipe the hosts to a custom handler that formats the hosts to CSV
----------------------------------------------------------------

    viper hosts viper.demo.hosts.group1 | viper hosts:pipe viper.demo.handlers.hosts_to_csv


Let's save the hosts
--------------------

    viper hosts viper.demo.hosts.group1 > /tmp/hosts.json


Filter hosts
------------


    cat /tmp/hosts.json | viper hosts:filter viper.demo.filters.ip_is 8.8.8.8 --indent 4


Assign tasks to the given hosts
-------------------------------

    cat /tmp/hosts.json | viper hosts:task viper.demo.tasks.ping --indent 4


Run the assigned tasks
----------------------

    cat /tmp/hosts.json | viper hosts:task viper.demo.tasks.ping | viper runners:run --indent 4

    # or use a shortcut

    cat /tmp/hosts.json | viper hosts:run-task viper.demo.tasks.ping --indent 4


Run tasks in parallel using multiple workers
--------------------------------------------

    cat /tmp/hosts.json | viper hosts:run-task viper.demo.tasks.ping --max-workers 50 --indent 4


Get the past results from DB
----------------------------

    viper results


Or get the past results by hosts
--------------------------------
    cat /tmp/hosts.json | viper hosts:results --indent 4 --debug


Or get the past results by task
-------------------------------

    viper task viper.demo.tasks.ping | viper results:by-task -i 4

    # or

    viper task viper.demo.tasks.ping | viper task:results -i 4


Let's save the result
---------------------

    viper task viper.demo.tasks.ping | viper task:results > /tmp/results.json


Now filter the results by their status
--------------------------------------

    # success
    cat /tmp/results.json | viper results:filter viper.demo.filters.result_ok -i 4

    # failed
    cat /tmp/results.json | viper results:filter viper.demo.filters.result_errored -i 4


Pipe the results to a custom handler
------------------------------------

    # print the status to terminal
    cat /tmp/results.json | viper results:pipe viper.demo.handlers.print_status

    # export the results to a csv file
    cat /tmp/results.json | viper results:pipe viper.demo.handlers.export_csv /tmp/results.csv


Let's do that again in one go
-----------------------------

    viper hosts viper.demo.hosts.group1 | viper hosts:run-task viper.demo.tasks.ping | viper results:pipe viper.demo.handlers.export_csv /tmp/results.csv
"""
