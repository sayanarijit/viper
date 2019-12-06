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


Documentations
==============
Getting Started Guide: https://viper-infrastructure-commander.readthedocs.io/en/latest/viper.demo.html#viper-cli-examples


Viperfile Examples and Use Cases: https://viper-infrastructure-commander.readthedocs.io/en/latest/viper.html#viper-project-apis-the-viperfile-py


Viper CLI Reference
===================
```
usage: viper [-h] [--version] [--debug]
             {init,run-job,run,task:from-func,task,task:results,task:format,hosts:from-file,hosts:from-func,hosts,hosts:filter,hosts:count,hosts:sort,hosts:pipe,hosts:format,hosts:task,hosts:run-task,hosts:results,runners:filter,runners:count,runners:sort,runners:pipe,runners:format,runners:run,runners:hosts,results:from-history,results,results:filter,results:count,results:sort,results:pipe,results:format,results:hosts,results:by-task}
             ...

Viper CLI v0.17.0

positional arguments:
  {init,run-job,run,task:from-func,task,task:results,task:format,hosts:from-file,hosts:from-func,hosts,hosts:filter,hosts:count,hosts:sort,hosts:pipe,hosts:format,hosts:task,hosts:run-task,hosts:results,runners:filter,runners:count,runners:sort,runners:pipe,runners:format,runners:run,runners:hosts,results:from-history,results,results:filter,results:count,results:sort,results:pipe,results:format,results:hosts,results:by-task}
    init                initialize the current workspace
    run-job             [? -> ?] run a custom defined job
    run                 alias of 'run-job'
    task:from-func      [-> Task] get the task from a Python function location
    task                alias of 'task:from-func'
    task:results        [Task -> Results] get the past results of given task
    task:format         [Task -> str] format the data in a using the given
                        template.
    hosts:from-file     [-> Hosts] get a group of hosts from a file
    hosts:from-func     [-> Hosts] get a group of hosts from a Python function
                        location
    hosts               alias of 'hosts:from-func'
    hosts:filter        [Hosts -> Hosts] filter hosts by a given function
    hosts:count         [Hosts -> int] count the number of hosts
    hosts:sort          [Hosts -> Hosts] sort the hosts
    hosts:pipe          [Hosts -> ?] pipe the hosts to the given handler
    hosts:format        [Hosts -> str] format the data in a using the given
                        template.
    hosts:task          [Hosts -> Runners] assign a task to each host
    hosts:run-task      [Hosts -> Results] assign a task to each host and run
    hosts:results       [Hosts -> Results] get the past results of the hosts
    runners:filter      [Runners -> Runners] filter runners by a given
                        function
    runners:count       [Runners -> int] count the number of runners
    runners:sort        [Runners -> Runners] sort the runners
    runners:pipe        [Runners -> ?] pipe the runners to the given handler
    runners:format      [Runners -> str] format the data in a using the given
                        template.
    runners:run         [Runners -> Results] run the assigned tasks
    runners:hosts       [Runners -> Hosts] get the hosts from the runners
    results:from-history
                        [-> Results] get the past results from database
    results             alias of 'results:from-history'
    results:filter      [Results -> Results] filter results by a given handler
    results:count       [Results -> int] count the number of results
    results:sort        [Results -> Results] sort the results
    results:pipe        [Results -> ?] pipe the results to the given handler
    results:format      [Results -> str] format the data in a using the given
                        template.
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
