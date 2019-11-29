from __future__ import annotations

import typing as t
from dataclasses import dataclass, field

from viper import host as _host
from viper import task as _task
from viper import task_runner as _task_runner
from viper import task_runners as _task_runners
from viper.collections import Items


@dataclass(frozen=True)
class Hosts(Items):
    """Hosts manager."""

    _item_factory: t.Type[_host.Host] = field(init=False, default=_host.Host)

    @classmethod
    def from_file(
        cls, filepath: str, loader: t.Callable[[t.TextIO], "Hosts"] = None
    ) -> Hosts:
        """Initialize hosts reading from a file."""

        if loader is None:

            def _loader(f: t.TextIO):
                return cls.from_items(
                    *(_host.Host(ip.strip()) for ip in f.read().strip().split())
                )

            loader = _loader

        with open(filepath) as f:
            return loader(f)

    def task(self, task: _task.Task) -> _task_runners.TaskRunners:
        """Assigns a task to be run on all the hosts."""

        return _task_runners.TaskRunners.from_items(
            *(_task_runner.TaskRunner(task=task, host=h) for h in self._all)
        )

    def run_task(self, task: _task.Task, max_workers=0) -> _task_results.TaskResults:
        """Run a task to be run on all hosts and then run it."""

        return self.task(task).run(max_workers=max_workers)
