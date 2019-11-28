from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor, as_completed

import typing as t
from dataclasses import dataclass, field

from viper import task
from viper.collections import Items
from viper.task_results import TaskResults
from viper.const import Config


@dataclass(frozen=True)
class TaskRunners(Items):
    _item_factory: t.Type[task.TaskRunner] = field(init=False, default=task.TaskRunner)

    def run_in_sequence(self) -> TaskResults:
        """Run the tasks in sequence."""
        return TaskResults.from_items(*(r.run() for r in self._all))

    def run_in_parallel(self, max_workers=Config.max_workers.value) -> TaskResults:
        """Run the tasks in parallel."""

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(r.run) for r in self._all]
            results = [f.result() for f in as_completed(futures)]

        return TaskResults.from_items(*results)
