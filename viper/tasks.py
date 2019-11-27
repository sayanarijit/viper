from __future__ import annotations

import typing as t
from dataclasses import dataclass

from viper.task import TaskResult, TaskRunner


@dataclass(frozen=True)
class TasksRunner:
    _task_runner_list: t.Sequence[TaskRunner]

    @classmethod
    def from_items(cls, *tasks_runners: TaskRunner) -> TasksRunner:
        """Initialize runners from given runners."""
        return cls(tuple(set(tasks_runners)))

    def __getitem__(self, key: int) -> TaskRunner:
        return self._task_runner_list[key]

    def __len__(self) -> int:
        """Count the number of runners."""
        return len(self._task_runner_list)

    def count(self) -> int:
        """Count the number of runners."""
        return len(self._task_runner_list)

    def first(self) -> TaskRunner:
        """Get the first runner from the list."""
        return self._task_runner_list[0]

    def last(self) -> TaskRunner:
        """Get the last runner from the list."""
        return self._task_runner_list[-1]

    def index(self, index: int) -> TaskRunner:
        """The the runner from a given index."""
        return self._task_runner_list[index]

    def sort(
        self, key: t.Optional[t.Callable[[TaskRunner], t.Any]] = None
    ) -> TasksRunner:
        """Sort the runners by given key/function."""
        return TasksRunner(tuple(sorted(self._task_runner_list, key=key)))

    def filter(self, func: t.Callable[[TaskRunner], bool]) -> TasksRunner:
        """Filter the runners by a giver function."""

        return TasksRunner(tuple(filter(func, self._task_runner_list)))

    def get(self, func: t.Callable[[TaskRunner], bool]) -> TaskRunner:
        """Get one unique runner by a filter function."""

        runners = self.filter(func)

        if runners.count() == 0:
            raise LookupError("could not find any runner.")

        if runners.count() > 1:
            raise LookupError("multiple runner found.")

        return runners.first()

    def all(self) -> t.Sequence[TaskRunner]:
        """Get a tuple of all the runners."""
        return self._task_runner_list

    def run_in_sequence(self) -> t.Sequence[TaskResult]:
        """Run the tasks in sequence."""
        return tuple(r.run() for r in self._task_runner_list)

    def run_in_parallel(self) -> t.Sequence[TaskResult]:
        """Run the tasks in sequence."""
        return tuple(r.run() for r in self._task_runner_list)
