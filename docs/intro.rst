::

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


Viper is a handy tool for easily running infrastructure management tasks and commands.


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
    viper hosts viper.demo.hosts.group1 \
            | viper run-job viper.demo.jobs.ping_then_execute "df -h" results.csv


Further Readings
~~~~~~~~~~~~~~~~
**API Docs with Examples ☞** https://viper-infrastructure-commander.readthedocs.io


Contributing To Viper
~~~~~~~~~~~~~~~~~~~~~
**Contribution Guidelines ☞** https://github.com/sayanarijit/viper/blob/master/CONTRIBUTING.md
