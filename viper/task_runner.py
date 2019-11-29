from __future__ import annotations

import time
import typing as t
from dataclasses import dataclass
from subprocess import PIPE, Popen, TimeoutExpired

from viper import host, task
from viper import task_result as _task_result
from viper import task_results as _task_results
from viper.collections import Item


@dataclass(frozen=True, order=True)
class TaskRunner(Item):
    """A task runner."""

    host: host.Host
    task: task.Task

    @classmethod
    def from_dict(cls, dict_: t.Dict[str, t.Any]) -> TaskRunner:
        """Overloading from_dict()."""

        return cls(
            **dict(
                dict_,
                task=task.Task.from_dict(dict_["task"]),
                host=host.Host.from_dict(dict_["host"]),
            )
        )

    def to_dict(self) -> t.Dict[str, t.Any]:
        """Overloading to_dict()."""

        return dict(vars(self), task=self.task.to_dict(), host=self.host.to_dict())

    def run(self, retry=0) -> _task_result.TaskResult:
        """Run the task on the host."""
        command = self.task.command_factory(self.host)

        p = Popen(command, stdout=PIPE, stderr=PIPE)

        start = time.time()
        try:
            out, err = p.communicate(timeout=self.task.timeout)
            stdout, stderr = out.decode("latin1"), err.decode("latin1")
        except TimeoutExpired as e:
            stdout, stderr, p.returncode = "", str(e), 123
        end = time.time()

        if self.task.stderr_processor:
            stdout = self.task.stdout_processor(stdout)

        if self.task.stderr_processor:
            stderr = self.task.stderr_processor(stderr)

        result = _task_result.TaskResult(
            self.task,
            self.host,
            command,
            stdout,
            stderr,
            p.returncode,
            start,
            end,
            retry,
        ).save()

        if result.errored() and self.task.retry > retry:
            return self.run(retry=retry + 1)

        return result

    def task_results(self) -> _task_results.TaskResults:
        """Fetch recent task results of current task runner from database."""
        return _task_results.TaskResults.by_task_runner(self)
