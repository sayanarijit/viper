from __future__ import annotations

import os
import pickle
import typing as t
from dataclasses import dataclass
from datetime import datetime
from subprocess import PIPE, Popen

from viper import host
from viper.const import DB_LOCATION


@dataclass(frozen=True, order=True)
class Task:
    """An infra task."""

    name: str
    command_factory: t.Callable[[host.Host], t.Tuple[str]]
    timeout: t.Optional[int] = None
    max_threads: t.Optional[int] = None
    stdout_processor: t.Optional[t.Callable[[str], str]] = None
    stderr_processor: t.Optional[t.Callable[[str], str]] = None


@dataclass(frozen=True, order=True)
class TaskResult:
    """The result of an executed task."""

    task: Task
    host: host.Host
    command: t.Sequence[str]
    stdout: str
    stderr: str
    returncode: int
    start: datetime
    end: datetime

    @classmethod
    def from_file(cls, filepath: str) -> TaskResult:
        with open(filepath, "rb") as f:
            return pickle.load(f)

    @classmethod
    def from_hash(cls, hash_: str) -> TaskResult:
        with open(os.path.join(DB_LOCATION, hash_), "rb") as f:
            return pickle.load(f)

    def ok(self) -> bool:
        """If the result is success."""
        return self.returncode == 0

    def errored(self) -> bool:
        """If the result is failure."""
        return self.returncode != 0

    def dump_location(self) -> str:
        """Get the data dump location."""
        return os.path.join(DB_LOCATION, f"{hash(self)}.pickle")

    def save(self) -> TaskResult:
        """Save the result dump."""

        with open(self.dump_location(), "wb") as f:
            pickle.dump(self, f)

        return self


@dataclass(frozen=True, order=True)
class TaskRunner:
    """A task runner."""

    host: host.Host
    task: Task

    def run(self) -> TaskResult:
        """Run the task on the host."""
        command = self.task.command_factory(self.host)

        p = Popen(command, stdout=PIPE, stderr=PIPE)

        start = datetime.now()
        out, err = p.communicate(timeout=self.task.timeout)
        end = datetime.now()
        stdout, stderr = out.decode(), err.decode()

        if self.task.stderr_processor:
            stdout = self.task.stdout_processor(stdout)

        if self.task.stderr_processor:
            stderr = self.task.stderr_processor(stderr)

        return TaskResult(
            self.task, self.host, command, stdout, stderr, p.returncode, start, end
        ).save()
