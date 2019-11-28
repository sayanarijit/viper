from __future__ import annotations

import os
import time
import typing as t
from dataclasses import dataclass
from pydoc import locate
from subprocess import PIPE, Popen

from viper import host
from viper.collections import Item
from viper.const import DB_LOCATION


@dataclass(frozen=True, order=True)
class Task(Item):
    """An infra task."""

    name: str
    command_factory: t.Callable[[host.Host], t.Tuple[str]]
    timeout: t.Optional[int] = None
    max_threads: t.Optional[int] = None
    stdout_processor: t.Optional[t.Callable[[str], str]] = None
    stderr_processor: t.Optional[t.Callable[[str], str]] = None

    @classmethod
    def from_dict(cls, dict_: t.Dict[str, t.Any]) -> Task:
        """Overloading from_dict()."""

        outp = dict_.get("stdout_processor")
        errp = dict_.get("stderr_processor")

        return cls(
            **dict(
                dict_,
                command_factory=locate(dict_["command_factory"]),
                stdout_processor=locate(outp) if outp else None,
                stderr_processor=locate(errp) if errp else None,
            )
        )

    def to_dict(self) -> t.Dict[str, t.Any]:
        """Overloading to_dict()."""

        cf = self.command_factory
        outp = self.stdout_processor
        errp = self.stderr_processor

        return dict(
            vars(self),
            command_factory=f"{cf.__module__}.{cf.__qualname__}",
            stdout_processor=f"{outp.__module__}.{outp.__qualname__}" if outp else None,
            stderr_processor=f"{errp.__module__}.{errp.__qualname__}" if errp else None,
        )


@dataclass(frozen=True, order=True)
class TaskResult(Item):
    """The result of an executed task."""

    task: Task
    host: host.Host
    command: t.Sequence[str]
    stdout: str
    stderr: str
    returncode: int
    start: float
    end: float

    @classmethod
    def from_file(cls, filepath: str) -> TaskResult:
        with open(filepath, "rb") as f:
            return cls.from_json(f.read().decode())

    @classmethod
    def from_hash(cls, hash_: str) -> TaskResult:
        return cls.from_file(os.path.join(DB_LOCATION, f"{hash_}.json"))

    @classmethod
    def from_dict(cls, dict_: t.Dict[str, t.Any]) -> Task:
        """Overloading from_dict()."""

        return cls(
            **dict(
                dict_,
                command=tuple(dict_["command"]),
                task=Task.from_dict(dict_["task"]),
                host=host.Host.from_dict(dict_["host"]),
            )
        )

    def to_dict(self) -> t.Dict[str, t.Any]:
        """Overloading to_dict()."""

        return dict(vars(self), task=self.task.to_dict(), host=self.host.to_dict(),)

    def ok(self) -> bool:
        """If the result is success."""
        return self.returncode == 0

    def errored(self) -> bool:
        """If the result is failure."""
        return self.returncode != 0

    def dump_location(self) -> str:
        """Get the data dump location."""
        return os.path.join(DB_LOCATION, f"{hash(self)}.json")

    def save(self) -> TaskResult:
        """Save the result dump."""

        with open(self.dump_location(), "wb") as f:
            f.write(self.to_json().encode())

        return self


@dataclass(frozen=True, order=True)
class TaskRunner(Item):
    """A task runner."""

    host: host.Host
    task: Task

    @classmethod
    def from_dict(cls, dict_: t.Dict[str, t.Any]) -> Task:
        """Overloading from_dict()."""

        return cls(
            **dict(
                dict_,
                task=Task.from_dict(dict_["task"]),
                host=host.Host.from_dict(dict_["host"]),
            )
        )

    def to_dict(self) -> t.Dict[str, t.Any]:
        """Overloading to_dict()."""

        return dict(vars(self), task=self.task.to_dict(), host=self.host.to_dict())

    def run(self) -> TaskResult:
        """Run the task on the host."""
        command = self.task.command_factory(self.host)

        p = Popen(command, stdout=PIPE, stderr=PIPE)

        start = time.time()
        out, err = p.communicate(timeout=self.task.timeout)
        end = time.time()
        stdout, stderr = out.decode(), err.decode()

        if self.task.stderr_processor:
            stdout = self.task.stdout_processor(stdout)

        if self.task.stderr_processor:
            stderr = self.task.stderr_processor(stderr)

        return TaskResult(
            self.task, self.host, command, stdout, stderr, p.returncode, start, end
        ).save()
