# Viper Infrastructure Commander

[![PyPI version](https://img.shields.io/pypi/v/viper-infra-commander.svg)](https://pypi.org/project/viper-infra-commander)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/viper-infra-commander.svg)](https://pypi.org/project/viper-infra-commander)
[![Build Status](https://travis-ci.org/sayanarijit/viper.svg?branch=master)](https://travis-ci.org/sayanarijit/viper)
[![codecov](https://codecov.io/gh/sayanarijit/viper/branch/master/graph/badge.svg)](https://codecov.io/gh/sayanarijit/viper)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)

## Installation

```
pip install -U viper-infra-commander
```

Viper is a handy tool for easily running infrastructure management tasks and commands.

## Viper CLI Examples.

### Initialize current workspace (creates a `viperdb.sqlite3` file)

    viper init

    # or remove or overwrite existing data with "-f" / "--force"

    viper init -f


### Load hosts from file

    viper hosts:from-file tests/data/hosts.csv --indent 4

    # or with a custom loader

    viper hosts:from-file tests/data/hosts.json --loader viper.demo.loaders.json --indent 4


### Load hosts from Python object

    viper hosts:from-obj viper.demo.hosts.group1 --indent 4


### Let's save the hosts

    viper hosts:from-obj viper.demo.hosts.group1 > /tmp/hosts.json


### Filter hosts

    cat /tmp/hosts.json | viper hosts:filter viper.demo.filters.ip_starts_with_2 --indent 4


### Assign tasks to the given hosts

    cat /tmp/hosts.json | viper hosts:task viper.demo.tasks.ping --indent 4


### Run the assigned tasks

    cat /tmp/hosts.json | viper hosts:task viper.demo.tasks.ping | viper task-runners:run --indent 4

    # or use a shortcut

    cat /tmp/hosts.json | viper hosts:run-task viper.demo.tasks.ping --indent 4


### Run tasks in parallel using multiple workers

    cat /tmp/hosts.json | viper hosts:run-task viper.demo.tasks.ping --max-workers 50 --indent 4


### Get the past task results of the hosts from DB

    cat /tmp/hosts.json | viper hosts:task-results --indent 4 --debug


### Or get the past task results by task

    viper task:from-obj viper.demo.tasks.ping | viper task-results:by-task -i 4

    # Or

    viper task:from-obj viper.demo.tasks.ping | viper task:results -i 4


### Let's save the result

    viper task:from-obj viper.demo.tasks.ping | viper task:results > /tmp/results.json


### Now filter the results by their status

    # success
    cat /tmp/results.json | viper task-results:filter viper.demo.filters.result_ok -i 4

    # failed
    cat /tmp/results.json | viper task-results:filter viper.demo.filters.result_errored -i 4


### Pipe the results to a custom handler

    cat /tmp/results.json | viper task-results:pipe viper.demo.handlers.print_status



## Viper CLI Reference

```
usage: viper [-h] [--version] [--debug]
             {init,task:from-obj,task:results,hosts:from-file,hosts:from-obj,hosts:filter,hosts:count,hosts:sort,hosts:pipe,hosts:task,hosts:run-task,hosts:task-results,task-runners:filter,task-runners:count,task-runners:sort,task-runners:pipe,task-runners:run,task-runners:hosts,task-results:filter,task-results:count,task-results:sort,task-results:pipe,task-results:hosts,task-results:by-task}
             ...

Viper CLI v0.0.0

positional arguments:
  {init,task:from-obj,task:results,hosts:from-file,hosts:from-obj,hosts:filter,hosts:count,hosts:sort,hosts:pipe,hosts:task,hosts:run-task,hosts:task-results,task-runners:filter,task-runners:count,task-runners:sort,task-runners:pipe,task-runners:run,task-runners:hosts,task-results:filter,task-results:count,task-results:sort,task-results:pipe,task-results:hosts,task-results:by-task}
    init                initialize the current workspace
    task:from-obj       get the task from a python object location
    task:results        get the past task results of given task
    hosts:from-file     get a group of hosts from a file
    hosts:from-obj      get a group of hosts from a python object location
    hosts:filter        filter hosts by a given function
    hosts:count         count the number of hosts
    hosts:sort          sort the hosts
    hosts:pipe          pipe the hosts to the given function
    hosts:task          assign a task to each host
    hosts:run-task      assign a task to each host and run
    hosts:task-results  get the past task results of the hosts
    task-runners:filter
                        filter task runners by a given function
    task-runners:count  count the number of task runners
    task-runners:sort   sort the task runners
    task-runners:pipe   pipe the task runners to the given function
    task-runners:run    run the assigned tasks
    task-runners:hosts  get the hohsts from the task runners
    task-results:filter
                        filter task results by a given function
    task-results:count  count the number of task results
    task-results:sort   sort the task results
    task-results:pipe   pipe the task results to the given function
    task-results:hosts  get the hosts from the task results
    task-results:by-task
                        get the past task results of given task

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --debug               show traceback information when an exception is raised
```
