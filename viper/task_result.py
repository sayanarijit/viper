from __future__ import annotations

import typing as t
from dataclasses import dataclass
from json import dumps as dumpjson
from json import loads as loadjson

from viper import host, task
from viper.collections import Item
from viper.db import ViperDB


@dataclass(frozen=True, order=True)
class TaskResult(Item):
    """The result of an executed task."""

    task: task.Task
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
    def from_dict(cls, dict_: t.Dict[str, t.Any]) -> task.Task:
        """Overloading from_dict()."""

        return cls(
            **dict(
                dict_,
                command=tuple(dict_["command"]),
                task=task.Task.from_dict(dict_["task"]),
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
