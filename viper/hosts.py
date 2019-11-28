from __future__ import annotations

import typing as t
from dataclasses import dataclass, field

from viper.collections import Items
from viper.host import Host
from viper.task import Task
from viper.tasks import TasksRunner


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

    def task(self, task: Task) -> TasksRunner:
        """Assigns a task to be run on all the hosts."""

        return TasksRunner.from_items(*(h.task(task) for h in self._all))
