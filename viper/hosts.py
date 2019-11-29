from __future__ import annotations

import typing as t
from dataclasses import dataclass, field

from viper.collections import Items
from viper.host import Host
from viper.task import Task, TaskRunner
from viper.task_results import TaskResults
from viper.task_runners import TaskRunners


@dataclass(frozen=True)
class Hosts(Items):
    """Hosts manager."""

    _item_factory: t.Type[Host] = field(init=False, default=Host)

    @classmethod
    def from_file(
        cls, filepath: str, loader: t.Callable[[t.TextIO], "Hosts"] = None
    ) -> Hosts:
        """Initialize hosts reading from a file."""

        if loader is None:

            def _loader(f: t.TextIO):
                return cls.from_items(
                    *(Host(ip.strip()) for ip in f.read().strip().split())
                )

            loader = _loader

        with open(filepath) as f:
            return loader(f)

    def task(self, task: Task) -> TaskRunners:
        """Assigns a task to be run on all the hosts."""

        return TaskRunners.from_items(
            *(TaskRunner(task=task, host=h) for h in self._all)
        )

    def run_task(self, task: Task, max_workers=0) -> TaskResults:
        """Run a task to be run on all hosts and then run it."""

        return self.task(task).run(max_workers=max_workers)
