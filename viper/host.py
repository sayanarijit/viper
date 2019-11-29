"""Host class is defined here."""

from __future__ import annotations

import typing as t
from dataclasses import dataclass

from viper import task as task_
from viper import task_result as _task_result
from viper import task_results as _task_results
from viper import task_runner as _task_runner
from viper.collections import Item


@dataclass(frozen=True, order=True)
class Host(Item):
    """Viper Host class."""

    ip: str
    hostname: t.Optional[str] = None
    domain: t.Optional[str] = None
    port: int = 22
    login_name: t.Optional[str] = None
    identity_file: t.Optional[str] = None

    def fqdn(self) -> str:
        """Get the FQDN from hostname and domainname."""

        if not self.hostname and not self.domain:
            raise AttributeError("hostname and domain not set")

        if not self.hostname:
            raise AttributeError("hostname not set")

        if not self.domain:
            raise AttributeError("domain not set")

        return f"{self.hostname}.{self.domain}"

    def task(self, task: task_.Task) -> _task_runner.TaskRunner:
        """Assigns a task to be run."""

        return _task_runner.TaskRunner(task=task, host=self)

    def run_task(self, task: task_.Task) -> _task_result.TaskResult:
        """Assign the task to the host and then run it."""

        return self.task(task).run()

    def task_results(self) -> _task_results.TaskResults:
        """Fetch recent task results of current host from database."""
        return _task_results.TaskResults.by_host(self)
