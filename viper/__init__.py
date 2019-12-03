__author__ = "Arijit Basu"
__description__ = "Viper is a handy tool for easily running infrastructure management tasks and commands."
__email__ = "sayanarijit@gmail.com"
__homepage__ = "https://github.com/sayanarijit/viper"
__license__ = "MIT"
__version__ = "v0.13.0"

from viper.collections import Host  # noqa: F401
from viper.collections import Hosts  # noqa: F401
from viper.collections import Result  # noqa: F401
from viper.collections import Results  # noqa: F401
from viper.collections import Runner  # noqa: F401
from viper.collections import Runners  # noqa: F401
from viper.collections import Task  # noqa: F401
from viper.demo import __doc__ as __viper_cli_examples__

__all__ = ["Host", "Hosts", "Result", "Results", "Runner", "Runners", "Task"]
__doc__ = f"""{__description__}


Installation
============

    pip install -U viper-infra-commander



{__viper_cli_examples__}
"""
