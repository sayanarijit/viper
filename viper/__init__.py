__author__ = "Arijit Basu"
__description__ = "Viper is a handy tool for easily running infrastructure management tasks and commands."
__email__ = "sayanarijit@gmail.com"
__homepage__ = "https://github.com/sayanarijit/viper"
__license__ = "MIT"
__version__ = "v0.3.0"

from viper.collections import (
    Host,
    Hosts,
    Task,
    Result,
    Results,
    Runner,
    Runners,
)
from viper.demo import __doc__ as __viper_cli_examples__

__doc__ = f"""{__description__}


## Installation

```
pip install -U viper-infra-commander
```


{__viper_cli_examples__}
"""
