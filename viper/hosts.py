from __future__ import annotations

import typing as t
from dataclasses import dataclass

from viper.host import Host
from viper.task import Task
from viper.tasks import TasksRunner


@dataclass(frozen=True)
class Hosts:
    """Hosts manager."""

    _host_list: t.Sequence[Host] = ()

    @classmethod
    def from_items(cls, *hosts: Host) -> Hosts:
        """Initialize hosts from given hosts."""
        return cls(tuple(set(hosts)))

    @classmethod
    def from_dicts(cls, *dicts: t.Dict[str, t.Any]):
        return cls.from_items(*(Host.from_dict(d) for d in dicts))

    @classmethod
    def from_file(
        cls, filepath: str, loader: t.Callable[[t.TextIO], "Hosts"] = None
    ) -> Hosts:
        """Initialize hosts reading from a file."""

        if loader is None:

            def loader(f: t.TextIO):
                return cls.from_items(
                    *(Host(ip.strip()) for ip in f.read().strip().split())
                )

        with open(filepath) as f:
            return loader(f)

    def __getitem__(self, key: int) -> Host:
        return self._host_list[key]

    def __len__(self) -> int:
        """Count the number of hosts."""
        return len(self._host_list)

    def count(self) -> int:
        """Count the number of hosts."""
        return len(self._host_list)

    def first(self) -> Host:
        """Get the first host from the list."""
        return self._host_list[0]

    def last(self) -> Host:
        """Get the last host from the list."""
        return self._host_list[-1]

    def index(self, index: int) -> Host:
        """The the host from a given index."""
        return self._host_list[index]

    def sort(self, key: t.Optional[t.Callable[[Host], t.Any]] = None) -> Hosts:
        """Sort the hosts by given key/function."""
        return Hosts(tuple(sorted(self._host_list, key=key)))

    def filter(self, func: t.Callable[[Host], bool]) -> Hosts:
        """Filter the hosts by a giver function."""

        return Hosts(tuple(filter(func, self._host_list)))

    def get(self, func: t.Callable[[Host], bool]) -> Host:
        """Get one unique host by a filter function."""

        hosts = self.filter(func)

        if hosts.count() == 0:
            raise LookupError("could not find any host.")

        if hosts.count() > 1:
            raise LookupError("multiple host found.")

        return hosts.first()

    def all(self) -> t.Sequence[Host]:
        """Get a tuple of all the hosts."""
        return self._host_list

    def task(self, task: Task) -> TasksRunner:
        """Assigns a task to be run on all the hosts."""

        return TasksRunner.from_items(*(h.task(task) for h in self._host_list))
