from __future__ import annotations

import time
import typing as t
from dataclasses import dataclass
from json import dumps as dumpjson
from json import loads as loadjson
from pydoc import locate
from subprocess import PIPE, Popen, TimeoutExpired

from viper import host
from viper.collections import Item
from viper.db import ViperDB


@dataclass(frozen=True, order=True)
class Task(Item):
    """An infra task."""

    name: str
    command_factory: t.Callable[[host.Host], t.Sequence[str]]
    timeout: t.Optional[int] = None
    retry: int = 0
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
    retry: int

    @classmethod
    def from_hash(cls, hash_: int) -> TaskResult:
        with ViperDB(ViperDB.url) as conn:

            data = next(
                conn.execute(
                    """
                    SELECT
                        task, host, command, stdout, stderr, returncode, start, end, retry
                    FROM task_results WHERE hash = ?
                    """,
                    (hash_,),
                )
            )
        return cls.from_dict(
            dict(
                task=loadjson(data[0]),
                host=loadjson(data[1]),
                command=loadjson(data[2]),
                stdout=data[3],
                stderr=data[4],
                returncode=data[5],
                start=data[6],
                end=data[7],
                retry=data[8],
            )
        )

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

    def save(self) -> TaskResult:
        """Save the result dump."""

        with ViperDB() as conn:
            conn.execute(
                """
                INSERT INTO task_results (
                    hash, task, host, command, stdout, stderr, returncode, start, end, retry
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    self.hash(),
                    self.task.to_json(),
                    self.host.to_json(),
                    dumpjson(self.command),
                    self.stdout,
                    self.stderr,
                    self.returncode,
                    self.start,
                    self.end,
                    self.retry,
                ),
            )

        return self

    def then(self, func: t.Callable[[TaskResult], t.Any]) -> t.Any:
        return func(self)


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

    def run(self, retry=0) -> TaskResult:
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

        result = TaskResult(
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
