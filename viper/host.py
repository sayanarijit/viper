from __future__ import annotations

import typing as t
from dataclasses import dataclass

from viper import task as task_
from viper.collections import Item


@dataclass(frozen=True, order=True)
class Host(Item):
    """Infra host class."""

    ip: str
    hostname: t.Optional[str] = None
    domain: t.Optional[str] = None
    port: int = 22
    login_name: t.Optional[str] = None
    identity_file: t.Optional[str] = None

    def fqdn(self) -> str:
        """Get the FQDN from hostname and domainname."""

        if not self.hostname and not self.domain:
            raise UnboundLocalError("hostname and domain not set")

        if not self.hostname:
            raise UnboundLocalError("hostname not set")

        if not self.domain:
            raise UnboundLocalError("domain not set")

        return f"{self.hostname}.{self.domain}"

    def task(self, task: task_.Task) -> task_.TaskRunner:
        """Assigns a task to be run."""

        return task_.TaskRunner(task=task, host=self)

    def run_task(self, task: task_.Task) -> task_.TaskResult:
        """Assign the task to the host and then run it."""

        return self.task(task).run()

    def recent_task_results(
        self, task: task_.Task, limit: int, offset: t.Optional[int] = None,
    ):
        """Fetch recent task results of current host from database."""
        pass
