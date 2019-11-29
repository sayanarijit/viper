__author__ = "Arijit Basu"
__description__ = "Viper is a handy tool for easily running infrastructure management tasks and commands."
__email__ = "sayanarijit@gmail.com"
__homepage__ = "https://github.com/sayanarijit/viper"
__license__ = "MIT"
__version__ = "v0.0.1"

from viper.host import Host
from viper.hosts import Hosts
from viper.task import Task, TaskResult, TaskRunner
from viper.task_runners import TaskRunners
from viper.task_results import TaskResults
from viper.demo import __doc__ as __viper_cli_examples__

__doc__ = f"""# Viper Infrastructure Commander

{__description__}

{__viper_cli_examples__}
"""
