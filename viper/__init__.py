__author__ = "Arijit Basu"
__description__ = "Viper is a handy tool for easily running infrastructure management tasks and commands."
__email__ = "sayanarijit@gmail.com"
__homepage__ = "https://github.com/sayanarijit/viper"
__license__ = "MIT"
__version__ = "v0.26.1"

from viper.collections import Host  # noqa: F401
from viper.collections import Hosts  # noqa: F401
from viper.collections import Result  # noqa: F401
from viper.collections import Results  # noqa: F401
from viper.collections import Runner  # noqa: F401
from viper.collections import Runners  # noqa: F401
from viper.collections import Task  # noqa: F401
from viper.collections import WhereConditions  # noqa: F401

__all__ = [
    "Host",
    "Hosts",
    "Result",
    "Results",
    "Runner",
    "Runners",
    "Task",
    "WhereConditions",
]
__doc__ = f"""::

     ▄   ▄█ █ ▄▄  ▄███▄   █▄▄▄▄   ▄█    ▄   ▄████  █▄▄▄▄ ██     ▄█▄    ████▄ █▀▄▀█ █▀▄▀█ ██      ▄   ██▄   ▄███▄   █▄▄▄▄
      █  ██ █   █ █▀   ▀  █  ▄▀   ██     █  █▀   ▀ █  ▄▀ █ █    █▀ ▀▄  █   █ █ █ █ █ █ █ █ █      █  █  █  █▀   ▀  █  ▄▀
 █     █ ██ █▀▀▀  ██▄▄    █▀▀▌    ██ ██   █ █▀▀    █▀▀▌  █▄▄█   █   ▀  █   █ █ ▄ █ █ ▄ █ █▄▄█ ██   █ █   █ ██▄▄    █▀▀▌
  █    █ ▐█ █     █▄   ▄▀ █  █    ▐█ █ █  █ █      █  █  █  █   █▄  ▄▀ ▀████ █   █ █   █ █  █ █ █  █ █  █  █▄   ▄▀ █  █
   █  █   ▐  █    ▀███▀     █      ▐ █  █ █  █       █      █   ▀███▀           █     █     █ █  █ █ ███▀  ▀███▀     █
    █▐        ▀            ▀         █   ██   ▀     ▀      █                   ▀     ▀     █  █   ██                ▀
    ▐                                                     ▀                               ▀


.. image:: https://img.shields.io/pypi/v/viper-infra-commander.svg
    :target: https://pypi.org/project/viper-infra-commander

.. image:: https://img.shields.io/pypi/pyversions/viper-infra-commander.svg
    :target: https://pypi.org/project/viper-infra-commander

.. image:: https://travis-ci.com/sayanarijit/viper.svg?branch=master
    :target: https://travis-ci.com/sayanarijit/viper

.. image:: https://codecov.io/gh/sayanarijit/viper/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/sayanarijit/viper

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/python/black

.. image:: https://readthedocs.org/projects/viper-infrastructure-commander/badge/?version=latest
    :target: https://viper-infrastructure-commander.readthedocs.io


{__description__}


Installation
~~~~~~~~~~~~

.. code-block:: bash

    pip install -U viper-infra-commander

    # Or with tab autocomplete support

    pip install -U "viper-infra-commander[autocomplete]"


Getting Started
~~~~~~~~~~~~~~~

.. code-block:: bash

    # See the help menu
    viper -h

    # Initialize SQLite DB
    viper init -f

    # Run a job on a defined list of hosts
    viper hosts viper.demo.hosts.group1 \\
            | viper run-job viper.demo.jobs.ping_then_execute "df -h" results.csv


Further Readings
~~~~~~~~~~~~~~~~
**API Docs with Examples ☞** https://viper-infrastructure-commander.readthedocs.io


Contributing To Viper
~~~~~~~~~~~~~~~~~~~~~
**Contribution Guidelines ☞** https://github.com/sayanarijit/viper/blob/master/CONTRIBUTING.md
"""
