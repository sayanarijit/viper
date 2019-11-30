# Viper Infrastructure Commander

[![PyPI version](https://img.shields.io/pypi/v/viper-infra-commander.svg)](https://pypi.org/project/viper-infra-commander)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/viper-infra-commander.svg)](https://pypi.org/project/viper-infra-commander)
[![Build Status](https://travis-ci.com/sayanarijit/viper.svg?branch=master)](https://travis-ci.com/sayanarijit/viper)
[![codecov](https://codecov.io/gh/sayanarijit/viper/branch/master/graph/badge.svg)](https://codecov.io/gh/sayanarijit/viper)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)

Viper is a handy tool for easily running infrastructure management tasks and commands.


## Installation

```
pip install -U viper-infra-commander
```


## Viper CLI Examples.

### Initialize current workspace (creates a `viperdb.sqlite3` file)

    viper init

    # or remove or overwrite existing data with "-f" / "--force"

    viper init -f


### Load hosts from file

    viper hosts:from-file tests/data/hosts.csv --indent 4

    # or with a custom loader

    viper hosts:from-file tests/data/hosts.json --loader viper.demo.loaders.json --indent 4


### Load hosts from a Python function

    viper hosts viper.demo.hosts.group1 --indent 4


### Let's save the hosts

    viper hosts viper.demo.hosts.group1 > /tmp/hosts.json


### Filter hosts

    cat /tmp/hosts.json | viper hosts:filter viper.demo.filters.ip_is 8.8.8.8 --indent 4


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

    viper task viper.demo.tasks.ping | viper task-results:by-task -i 4

    # or

    viper task viper.demo.tasks.ping | viper task:results -i 4


### Let's save the result

    viper task viper.demo.tasks.ping | viper task:results > /tmp/results.json


### Now filter the results by their status

    # success
    cat /tmp/results.json | viper task-results:filter viper.demo.filters.result_ok -i 4

    # failed
    cat /tmp/results.json | viper task-results:filter viper.demo.filters.result_errored -i 4


### Pipe the results to a custom handler

    # print the status to terminal
    cat /tmp/results.json | viper task-results:pipe viper.demo.handlers.print_status

    # export the results to a csv file
    cat /tmp/results.json | viper task-results:pipe viper.demo.handlers.export_csv /tmp/results.csv


### Let's do that again in one go
    viper hosts viper.demo.hosts.group1 | viper hosts:rttp viper.demo.tasks.ping viper.demo.handlers.export_csv /tmp/results.csv



## Viper CLI Reference

```
usage: viper [-h] [--version] [--debug]
             {init,task:from-func,task,task:results,hosts:from-file,hosts:from-func,hosts,hosts:filter,hosts:count,hosts:sort,hosts:pipe,hosts:task,hosts:run-task,hosts:run-task-then-pipe,hosts:rttp,hosts:task-results,task-runners:filter,task-runners:count,task-runners:sort,task-runners:pipe,task-runners:run,task-runners:hosts,task-results:filter,task-results:count,task-results:sort,task-results:pipe,task-results:hosts,task-results:by-task}
             ...

Viper CLI v0.2.0

positional arguments:
  {init,task:from-func,task,task:results,hosts:from-file,hosts:from-func,hosts,hosts:filter,hosts:count,hosts:sort,hosts:pipe,hosts:task,hosts:run-task,hosts:run-task-then-pipe,hosts:rttp,hosts:task-results,task-runners:filter,task-runners:count,task-runners:sort,task-runners:pipe,task-runners:run,task-runners:hosts,task-results:filter,task-results:count,task-results:sort,task-results:pipe,task-results:hosts,task-results:by-task}
    init                initialize the current workspace
    task:from-func      [task:from-func FUNC > Task] get the task from a
                        Python function location
    task                alias of 'task:from-func'
    task:results        [Task > task:results > TaskResults] get the past task
                        results of given task
    hosts:from-file     [hosts:from-file FILE > Hosts] get a group of hosts
                        from a file
    hosts:from-func     [hosts:from-func FUNC > Hosts] get a group of hosts
                        from a Python function location
    hosts               alias of 'hosts:from-func'
    hosts:filter        [Hosts > hosts:filter FILTER *AGS > Hosts] filter
                        hosts by a given function
    hosts:count         [Hosts > hosts:count > int] count the number of hosts
    hosts:sort          [Hosts > hosts:sort > Hosts] sort the hosts
    hosts:pipe          [Hosts > hosts:pipe HANDLER *ARGS > ?] pipe the hosts
                        to the given handler
    hosts:task          [Hosts > hosts:task TASK > TaskRunners] assign a task
                        to each host
    hosts:run-task      [Hosts > hosts:run-task > TaskRunners] assign a task
                        to each host and run
    hosts:run-task-then-pipe
                        [Hosts > hosts:run-task-then-pipe TASK HANDLER *ARGS >
                        ?] run the task on hosts and pipe the results to a
                        handler
    hosts:rttp          alias of 'hosts:run-task-then-pipe'
    hosts:task-results  [Hosts > hosts:task-results > TaskResults] get the
                        past task results of the hosts
    task-runners:filter
                        [TaskRunners > task-runners:filter FILTER *ARGS >
                        TaskRunners] filter task runners by a given function
    task-runners:count  [TaskRunners > task-runners:count > int] count the
                        number of task runners
    task-runners:sort   [TaskRunners > task-runners:sort > TaskRunners] sort
                        the task runners
    task-runners:pipe   [TaskRunners > task-runners:pipe HANDLER *ARGS > ?]
                        pipe the task runners to the given handler
    task-runners:run    [TaskRunners > task-runners:run > TaskResults] run the
                        assigned tasks
    task-runners:hosts  [TaskRunners > task-runners:hosts > Hosts] get the
                        hohsts from the task runners
    task-results:filter
                        [TaskResults > task-results:filter FILTER *ARGS >
                        TaskResults] filter task results by a given handler
    task-results:count  [TaskResults > task-results:count > int] count the
                        number of task results
    task-results:sort   [TaskResults > task-results:sort > TaskResults] sort
                        the task results
    task-results:pipe   [TaskResults > task-results:pipe HANDLER *ARGS> ?]
                        pipe the task results to the given handler
    task-results:hosts  [TaskResults > task-results:hosts > Hosts] get the
                        hosts from the task results
    task-results:by-task
                        [Task > task-results:by-task > TaskResults] get the
                        past task results of given task

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --debug               show traceback information when an exception is raised
```
