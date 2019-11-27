from __future__ import annotations

import typing as t
from dataclasses import dataclass

from viper.task import Task, TaskRunner


@dataclass(frozen=True, order=True)
class Host:
    """Infra host class."""

    ip: str
    hostname: t.Optional[str] = None
    domain: t.Optional[str] = None
    port: int = 22
    login_name: t.Optional[str] = None
    identity_file: t.Optional[str] = None

    @classmethod
    def from_dict(cls, dict_: t.Dict[str, t.Any]) -> Host:
        """Initialize host from given dict."""
        return cls(**dict_)

    def fqdn(self) -> str:
        """Get the FQDN from hostname and domainname."""
        if not self.hostname and not self.domain:
            raise UnboundLocalError("hostname and domain not set")

        if not self.hostname:
            raise UnboundLocalError("hostname not set")

        if not self.domain:
            raise UnboundLocalError("domain not set")

        return f"{self.hostname}.{self.domain}"

    def task(self, task: Task) -> TaskRunner:
        """Assigns a task to be run."""
        return TaskRunner(self, task)
