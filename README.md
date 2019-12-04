Viper Infrastructure Commander
==============================
[![PyPI version](https://img.shields.io/pypi/v/viper-infra-commander.svg)](https://pypi.org/project/viper-infra-commander)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/viper-infra-commander.svg)](https://pypi.org/project/viper-infra-commander)
[![Build Status](https://travis-ci.com/sayanarijit/viper.svg?branch=master)](https://travis-ci.com/sayanarijit/viper)
[![codecov](https://codecov.io/gh/sayanarijit/viper/branch/master/graph/badge.svg)](https://codecov.io/gh/sayanarijit/viper)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)
[![Documentation Status](https://readthedocs.org/projects/viper-infrastructure-commander/badge/?version=latest)](https://viper-infrastructure-commander.readthedocs.io)

Viper is a handy tool for easily running infrastructure management tasks and commands.


Installation
============

    pip install -U viper-infra-commander



Viper CLI Examples
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



Viper CLI Reference
===================
```
usage: viper [-h] [--version] [--debug]
             {init,run-job,run,task:from-func,task,task:results,hosts:from-file,hosts:from-func,hosts,hosts:filter,hosts:count,hosts:sort,hosts:pipe,hosts:task,hosts:run-task,hosts:results,runners:filter,runners:count,runners:sort,runners:pipe,runners:run,runners:hosts,results:from-history,results,results:filter,results:count,results:sort,results:pipe,results:hosts,results:by-task}
             ...

Viper CLI v0.15.0

positional arguments:
  {init,run-job,run,task:from-func,task,task:results,hosts:from-file,hosts:from-func,hosts,hosts:filter,hosts:count,hosts:sort,hosts:pipe,hosts:task,hosts:run-task,hosts:results,runners:filter,runners:count,runners:sort,runners:pipe,runners:run,runners:hosts,results:from-history,results,results:filter,results:count,results:sort,results:pipe,results:hosts,results:by-task}
    init                initialize the current workspace
    run-job             [? -> ?] run a custom defined job
    run                 alias of 'run-job'
    task:from-func      [-> Task] get the task from a Python function location
    task                alias of 'task:from-func'
    task:results        [Task -> Results] get the past results of given task
    hosts:from-file     [-> Hosts] get a group of hosts from a file
    hosts:from-func     [-> Hosts] get a group of hosts from a Python function
                        location
    hosts               alias of 'hosts:from-func'
    hosts:filter        [Hosts -> Hosts] filter hosts by a given function
    hosts:count         [Hosts -> int] count the number of hosts
    hosts:sort          [Hosts -> Hosts] sort the hosts
    hosts:pipe          [Hosts -> ?] pipe the hosts to the given handler
    hosts:task          [Hosts -> Runners] assign a task to each host
    hosts:run-task      [Hosts -> Results] assign a task to each host and run
    hosts:results       [Hosts -> Results] get the past results of the hosts
    runners:filter      [Runners -> Runners] filter runners by a given
                        function
    runners:count       [Runners -> int] count the number of runners
    runners:sort        [Runners -> Runners] sort the runners
    runners:pipe        [Runners -> ?] pipe the runners to the given handler
    runners:run         [Runners -> Results] run the assigned tasks
    runners:hosts       [Runners -> Hosts] get the hosts from the runners
    results:from-history
                        [-> Results] get the past results from database
    results             alias of 'results:from-history'
    results:filter      [Results -> Results] filter results by a given handler
    results:count       [Results -> int] count the number of results
    results:sort        [Results -> Results] sort the results
    results:pipe        [Results -> ?] pipe the results to the given handler
    results:hosts       [Results -> Hosts] get the hosts from the results
    results:by-task     [Task -> Results] get the past results of given task

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --debug               show traceback information when an exception is raised
```

Contributing to Viper
=====================
See the [contribution guidelines](https://github.com/sayanarijit/viper/blob/master/CONTRIBUTING.md).

---

NOTE: This file is generated by running "make readme"
