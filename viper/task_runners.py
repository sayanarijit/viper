from __future__ import annotations

import typing as t
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field

from viper import task as _task
from viper import task_results as _task_results
from viper import task_runner as _task_runner
from viper.collections import Items


@dataclass(frozen=True)
class TaskRunners(Items):
    _item_factory: t.Type[_task_runner.TaskRunner] = field(
        init=False, default=_task_runner.TaskRunner
    )

    def run(self, max_workers=0) -> _task_results.TaskResults:
        """Run the tasks."""

        if max_workers <= 1:
            # Run in sequence
            return _task_results.TaskResults.from_items(*(r.run() for r in self._all))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Run in parallel
            futures = [executor.submit(r.run) for r in self._all]
            results = [f.result() for f in as_completed(futures)]

        return _task_results.TaskResults.from_items(*results)
