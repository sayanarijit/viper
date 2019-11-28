from __future__ import annotations

import typing as t
from dataclasses import dataclass, field

from viper.collections import Items
from viper.task import TaskResult


@dataclass(frozen=True)
class TaskResults(Items):
    _item_factory: t.Type[TaskResult] = field(init=False, default=TaskResult)
