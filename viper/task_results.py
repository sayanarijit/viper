from __future__ import annotations

import typing as t
from dataclasses import dataclass, field

from viper import host as _host
from viper import task as _task
from viper import task_result as _task_result
from viper import task_runner as _task_runner
from viper.collections import Items
from viper.db import ViperDB


@dataclass(frozen=True)
class TaskResults(Items):
    _item_factory: t.Type[_task_result.TaskResult] = field(
        init=False, default=_task_result.TaskResult
    )

    @classmethod
    def by_host(cls, host: _host.Host) -> TaskResults:
        with ViperDB(ViperDB.url) as conn:
            rows = conn.execute(
                f"""
                SELECT hash FROM task_results
                WHERE JSON_EXTRACT(host, '$.ip') = ?
                ORDER BY start DESC
                """,
                (host.ip,),
            )
            results = [cls._item_factory.from_hash(r[0]) for r in rows]

        return cls.from_items(*results)

    @classmethod
    def by_task(cls, task: _task.Task) -> TaskResults:
        with ViperDB(ViperDB.url) as conn:
            rows = conn.execute(
                f"""
                SELECT hash FROM task_results
                WHERE JSON_EXTRACT(task, '$.name') = ?
                ORDER BY start DESC
                """,
                (task.name,),
            )
            results = [cls._item_factory.from_hash(r[0]) for r in rows]

        return cls.from_items(*results)

    @classmethod
    def by_task_runner(cls, runner: _task_runner.TaskRunner) -> TaskResults:
        with ViperDB(ViperDB.url) as conn:
            rows = conn.execute(
                f"""
                SELECT hash FROM task_results
                WHERE JSON_EXTRACT(host, '$.ip') = ?
                    AND JSON_EXTRACT(task, '$.name') = ?
                ORDER BY start DESC
                """,
                (runner.host.ip, runner.task.name,),
            )
            results = [cls._item_factory.from_hash(r[0]) for r in rows]

        return cls.from_items(*results)
