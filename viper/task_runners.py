from __future__ import annotations

import typing as t
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field

from viper import task
from viper.collections import Items
from viper.task_results import TaskResults


@dataclass(frozen=True)
class TaskRunners(Items):
    _item_factory: t.Type[task.TaskRunner] = field(init=False, default=task.TaskRunner)

    def run(self, max_workers=0) -> TaskResults:
        """Run the tasks in sequence."""

        if max_workers < 1:
            # Run in sequence
            return TaskResults.from_items(*(r.run() for r in self._all))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Run in parallel
            futures = [executor.submit(r.run) for r in self._all]
            results = [f.result() for f in as_completed(futures)]

        return TaskResults.from_items(*results)
