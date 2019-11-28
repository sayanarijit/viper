from __future__ import annotations

import typing as t
from dataclasses import dataclass, field

from viper.collections import Items
from viper.task import TaskResult, TaskRunner


@dataclass(frozen=True)
class TasksRunner(Items):
    _item_factory: t.Type[TaskResult] = field(init=False, default=TaskRunner)

    def run_in_sequence(self) -> t.Sequence[TaskResult]:
        """Run the tasks in sequence."""
        return tuple(r.run() for r in self._all)

    def run_in_parallel(self) -> t.Sequence[TaskResult]:
        """Run the tasks in sequence."""
        return tuple(r.run() for r in self._all)
