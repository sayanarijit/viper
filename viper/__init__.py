__author__ = "Arijit Basu"
__description__ = "Viper is a handy tool for easily running infrastructure management tasks and commands."
__email__ = "sayanarijit@gmail.com"
__homepage__ = "https://github.com/sayanarijit/viper"
__license__ = "MIT"
__version__ = "v0.18.0"

from viper.collections import Host  # noqa: F401
from viper.collections import Hosts  # noqa: F401
from viper.collections import Result  # noqa: F401
from viper.collections import Results  # noqa: F401
from viper.collections import Runner  # noqa: F401
from viper.collections import Runners  # noqa: F401
from viper.collections import Task  # noqa: F401

__all__ = ["Host", "Hosts", "Result", "Results", "Runner", "Runners", "Task"]
__doc__ = f"""{__description__}


Installation
============

    pip install -U viper-infra-commander


Documentations
==============
Getting Started Guide: https://viper-infrastructure-commander.readthedocs.io/en/latest/viper.demo.html#viper-cli-examples


Viperfile Examples and Use Cases: https://viper-infrastructure-commander.readthedocs.io/en/latest/viper.html#viper-project-apis-the-viperfile-py
"""
