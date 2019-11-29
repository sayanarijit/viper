from __future__ import annotations

import typing as t
from dataclasses import dataclass
from pydoc import locate

from viper import host as _host
from viper.collections import Item


@dataclass(frozen=True, order=True)
class Task(Item):
    """An infra task."""

    name: str
    command_factory: t.Callable[[_host.Host], t.Sequence[str]]
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
