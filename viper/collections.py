"""Base collection classes are defined here."""

from __future__ import annotations

import time
import typing as t
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from json import dumps as dumpjson
from json import loads as loadjson
from pydoc import locate
from subprocess import PIPE, Popen, TimeoutExpired

from viper.db import ViperDB


@dataclass(frozen=True, order=True)
class Item:
    """A single item."""

    @classmethod
    def from_dict(cls, dict_: t.Dict[str, t.Any]) -> Item:
        """Initialize item from given dict."""

        try:
            return cls(**dict_)
        except Exception:
            raise ValueError(f"invalid input data for {cls.__name__}")

    def to_dict(self) -> t.Dict[str, t.Any]:
        """Represent the item as dict."""

        return vars(self)

    @classmethod
    def from_json(cls, json: str, *args: t.Any, **kwargs: t.Any) -> Item:
        """Initialize item from given JSON data."""

        return cls.from_dict(loadjson(json))

    def to_json(self, *args: t.Any, **kwargs: t.Any) -> str:
        """Represent the item as JSON data."""

        return dumpjson(self.to_dict(), *args, **kwargs)

    @classmethod
    def from_obj(cls, objpath: str) -> Item:
        """Load the item from the given Python object path."""

        item = locate(objpath)
        if not item:
            raise ValueError(f"could not resolve {repr(objpath)}.")

        if not isinstance(item, cls):
            raise ValueError(f"{repr(objpath)} is not a valid {cls} instance.")

        return item

    def hash(self):
        """Get the hash value"""
        return hash(self)


@dataclass(frozen=True)
class Items:
    """A collection of similar items."""

    _all: t.Sequence[Item] = ()
    _item_factory: t.Type[Item] = field(init=False, default=Item)

    @classmethod
    def from_items(cls, *items: Item) -> Items:
        """Initialize items from given items."""
        return cls(tuple(set(items)))

    @classmethod
    def from_list(cls, list_: t.Sequence[t.Dict[str, t.Any]]) -> Items:
        """Initialize items from given list."""

        if cls._item_factory is None:
            raise NotImplementedError()

        try:
            return cls.from_items(*map(cls._item_factory.from_dict, list_))
        except Exception:
            raise ValueError(f"invalid input data for {cls.__name__}")

    def to_list(self) -> t.List[t.Dict[str, t.Any]]:
        """Represent the items as list."""

        return [i.to_dict() for i in self._all]

    @classmethod
    def from_json(cls, json: str, *args: t.Any, **kwargs: t.Any) -> Items:
        """Initialize items from given JSON data."""

        return cls.from_list(loadjson(json))

    def to_json(self, *args: t.Any, **kwargs: t.Any) -> str:
        """Represent the item as JSON data."""

        return dumpjson(self.to_list(), *args, **kwargs)

    @classmethod
    def from_obj(cls, objpath: str) -> Items:
        """Load the items from the given Python object path."""

        items = locate(objpath)
        if not items:
            raise ValueError(f"could not resolve {repr(objpath)}.")

        if not isinstance(items, cls):
            raise ValueError(f"{repr(objpath)} is not a valid {cls} instance.")

        return items

    def __getitem__(self, key: int) -> Item:
        return self._all[key]

    def __len__(self) -> int:
        """Count the number of items."""
        return len(self._all)

    def count(self) -> int:
        """Count the number of items."""
        return len(self._all)

    def first(self) -> Item:
        """Get the first item from the list."""
        return self._all[0]

    def last(self) -> Item:
        """Get the last item from the list."""
        return self._all[-1]

    def index(self, index: int) -> Item:
        """The the item from a given index."""
        return self._all[index]

    def sort(self, key: t.Optional[t.Callable[[Item], t.Any]] = None) -> Items:
        """Sort the items by given key/function."""
        return type(self)(tuple(sorted(self._all, key=key)))

    def filter(self, func: t.Callable[[Item], bool]) -> Items:
        """Filter the items by a giver function."""
        return type(self)(tuple(filter(func, self._all)))

    def get(self, func: t.Callable[[Item], bool]) -> Item:
        """Get one unique item by a filter function."""

        items = self.filter(func)

        if items.count() == 0:
            raise LookupError("could not find any item.")

        if items.count() > 1:
            raise LookupError("multiple item found.")

        return items.first()

    def all(self) -> t.Sequence[Item]:
        """Get a tuple of all the items."""
        return self._all

    def hash(self):
        """Get the hash value"""
        return hash(self)


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

    def task(self, task: Task) -> TaskRunner:
        """Assigns a task to be run."""

        return TaskRunner(task=task, host=self)

    def run_task(self, task: Task) -> TaskResult:
        """Assign the task to the host and then run it."""

        return self.task(task).run()

    def task_results(self) -> TaskResults:
        """Fetch recent task results of current host from database."""
        return TaskResults.by_host(self)


@dataclass(frozen=True)
class Hosts(Items):
    """Hosts manager."""

    _item_factory: t.Type[Host] = field(init=False, default=Host)

    @classmethod
    def from_file(
        cls, filepath: str, loader: t.Callable[[t.TextIO], "Hosts"] = None
    ) -> Hosts:
        """Initialize hosts reading from a file."""

        if loader is None:

            def _loader(f: t.TextIO):
                return cls.from_items(
                    *(Host(ip.strip()) for ip in f.read().strip().split())
                )

            loader = _loader

        with open(filepath) as f:
            return loader(f)

    def task(self, task: Task) -> TaskRunners:
        """Assigns a task to be run on all the hosts."""

        return TaskRunners.from_items(
            *(TaskRunner(task=task, host=h) for h in self._all)
        )

    def run_task(self, task: Task, max_workers=0) -> TaskResults:
        """Run a task to be run on all hosts and then run it."""

        return self.task(task).run(max_workers=max_workers)


@dataclass(frozen=True, order=True)
class Task(Item):
    """An infra task."""

    name: str
    command_factory: t.Callable[[Host], t.Sequence[str]]
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
class TaskRunner(Item):
    """A task runner."""

    host: Host
    task: Task

    @classmethod
    def from_dict(cls, dict_: t.Dict[str, t.Any]) -> TaskRunner:
        """Overloading from_dict()."""

        return cls(
            **dict(
                dict_,
                task=Task.from_dict(dict_["task"]),
                host=Host.from_dict(dict_["host"]),
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

    def task_results(self) -> TaskResults:
        """Fetch recent task results of current task runner from database."""
        return TaskResults.by_task_runner(self)


@dataclass(frozen=True)
class TaskRunners(Items):
    _item_factory: t.Type[TaskRunner] = field(init=False, default=TaskRunner)

    def run(self, max_workers=0) -> TaskResults:
        """Run the tasks."""

        if max_workers <= 1:
            # Run in sequence
            return TaskResults.from_items(*(r.run() for r in self._all))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Run in parallel
            futures = [executor.submit(r.run) for r in self._all]
            results = [f.result() for f in as_completed(futures)]

        return TaskResults.from_items(*results)

    def hosts(self) -> Hosts:
        """Get the list of hosts from the runners."""
        return Hosts.from_items(*(t.host for t in self._all))


@dataclass(frozen=True, order=True)
class TaskResult(Item):
    """The result of an executed task."""

    task: Task
    host: Host
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
                host=Host.from_dict(dict_["host"]),
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


@dataclass(frozen=True)
class TaskResults(Items):
    _item_factory: t.Type[TaskResult] = field(init=False, default=TaskResult)

    @classmethod
    def by_host(cls, host: Host) -> TaskResults:
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
    def by_task(cls, task: Task) -> TaskResults:
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
    def by_task_runner(cls, runner: TaskRunner) -> TaskResults:
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

    def hosts(self) -> Hosts:
        """Get the list of hosts from the results."""
        return Hosts.from_items(*(r.host for r in self._all))
