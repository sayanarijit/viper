"""Base collection classes are defined here."""

from __future__ import annotations
from concurrent.futures import as_completed
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from dataclasses import field
from json import dumps as dumpjson
from json import loads as loadjson
from pydoc import locate
from time import time
from viper.const import Config
from viper.db import ViperDB

import subprocess
import typing as t

ItemType = t.TypeVar("ItemType", bound="Item")
ItemsType = t.TypeVar("ItemsType", bound="Items")

__all__ = [
    "Item",
    "Items",
    "Host",
    "Hosts",
    "Task",
    "Runner",
    "Runners",
    "Result",
    "Results",
    "Item",
    "Items",
    "Host",
    "Hosts",
    "Runner",
    "Runners",
    "Result",
    "Results",
]


class HandlerType:
    """TODO: This should be a protocol"""

    pass


class FilterType:
    """TODO: This should be a protocol"""

    pass


@dataclass(frozen=True, order=True)
class Item:
    """A single item."""

    @classmethod
    def from_dict(cls: t.Type[ItemType], dict_: t.Dict[str, object]) -> ItemType:
        """Initialize item from given dict."""

        try:
            return cls(**dict_)
        except Exception:
            raise ValueError(f"invalid input data for {cls.__name__}")

    def to_dict(self) -> t.Dict[str, object]:
        """Represent the item as dict."""

        return vars(self)

    @classmethod
    def from_json(
        cls: t.Type[ItemType], json: str, *args: object, **kwargs: object
    ) -> ItemType:
        """Initialize item from given JSON data."""

        return cls.from_dict(loadjson(json))

    def to_json(self, *args: object, **kwargs: object) -> str:
        """Represent the item as JSON data."""

        return dumpjson(self.to_dict(), *args, **kwargs)

    @classmethod
    def from_func(cls: t.Type[ItemType], funcpath: str) -> ItemType:
        """Load the item from the given Python function."""

        func: t.Optional[t.Callable[[], ItemsType]] = locate(funcpath)

        if not func:
            raise ValueError(f"could not resolve {repr(funcpath)}.")

        item = func()
        if not isinstance(item, cls):
            raise ValueError(
                f"{repr(funcpath)} does not produce a valid {cls} instance."
            )

        return item

    def hash(self: ItemType) -> int:
        """Get the hash value"""
        return hash(self)

    def pipe(self: ItemType, handler: HandlerType, *args: str) -> object:
        """Pipe this object to the given function"""
        return handler(self, *args)


@dataclass(frozen=True)
class Items:
    """A collection of similar items."""

    _all: t.Sequence[t.ItemType] = ()
    _item_factory: t.Type[ItemType] = field(init=False, default=Item)

    @classmethod
    def from_items(cls: t.Type[ItemType], *items: ItemType) -> ItemsType:
        """Initialize items from given items."""
        return cls(tuple(set(items)))

    @classmethod
    def from_list(
        cls: t.Type[ItemsType], list_: t.Sequence[t.Dict[str, object]]
    ) -> ItemsType:
        """Initialize items from given list."""

        if cls._item_factory is None:
            raise NotImplementedError()

        try:
            return cls.from_items(*map(cls._item_factory.from_dict, list_))
        except Exception:
            raise ValueError(f"invalid input data for {cls.__name__}")

    def to_list(self: ItemsType) -> t.List[t.Dict[str, object]]:
        """Represent the items as list."""

        return [i.to_dict() for i in self._all]

    @classmethod
    def from_json(
        cls: t.Type[ItemsType], json: str, *args: object, **kwargs: object
    ) -> ItemsType:
        """Initialize items from given JSON data."""

        return cls.from_list(loadjson(json))

    def to_json(self: ItemsType, *args: object, **kwargs: object) -> str:
        """Represent the item as JSON data."""

        return dumpjson(self.to_list(), *args, **kwargs)

    @classmethod
    def from_func(cls: t.Type[ItemsType], funcpath: str) -> ItemsType:
        """Load the items from the given Python function."""

        func: t.Optional[t.Callable[[], ItemsType]] = locate(funcpath)
        if not func:
            raise ValueError(f"could not resolve {repr(funcpath)}.")

        items = func()
        if not isinstance(items, cls):
            raise ValueError(f"{repr(funcpath)} does not produce a {cls} instance.")

        return items

    def __getitem__(self: ItemsType, key: int) -> Item:
        return self._all[key]

    def __len__(self: ItemsType) -> int:
        """Count the number of items."""
        return len(self._all)

    def count(self: ItemsType) -> int:
        """Count the number of items."""
        return len(self._all)

    def first(self: ItemsType) -> Item:
        """Get the first item from the list."""
        return self.index(0)

    def last(self: ItemsType) -> Item:
        """Get the last item from the list."""
        return self.index(-1)

    def index(self: ItemsType, index: int) -> Item:
        """The the item from a given index."""
        return self._all[index]

    def sort(
        self: ItemsType, key: t.Optional[t.Callable[[Item], object]] = None
    ) -> ItemsType:
        """Sort the items by given key/function."""
        return type(self)(tuple(sorted(self._all, key=key)))

    def filter(self: ItemsType, filter_: FilterType, *args: str) -> ItemsType:
        """Filter the items by a giver function."""
        return type(self)(tuple(filter(lambda i: filter_(i, *args), self._all)))

    def all(self: ItemsType) -> t.Sequence[Item]:
        """Get a tuple of all the items."""
        return self._all

    def hash(self: ItemsType) -> int:
        """Get the hash value"""
        return hash(self)

    def pipe(self: ItemsType, func: HandlerType, *args: str) -> object:
        """Pipe this object to the given function"""
        return func(self, *args)


@dataclass(frozen=True, order=True)
class Host(Item):
    """Viper Host class."""

    ip: str
    hostname: t.Optional[str] = None
    domain: t.Optional[str] = None
    port: int = 22
    login_name: t.Optional[str] = None
    identity_file: t.Optional[str] = None
    meta: t.Sequence[t.Tuple[object, object]] = ()

    def __hash__(self) -> int:
        return hash(self.ip)

    def __eq__(self, value):
        return type(self) == type(value) and self.ip == value.ip

    @classmethod
    def from_dict(cls, dict_):
        """Overriding to_json"""
        return cls(**dict(dict_, meta=tuple(dict_.get("meta", {}).items())))

    def to_dict(self):
        """Overriding to_json"""
        return dict(vars(self), meta=dict(self.meta))

    def fqdn(self) -> str:
        """Get the FQDN from hostname and domainname."""

        if not self.hostname and not self.domain:
            raise AttributeError("hostname and domain not set")

        if not self.hostname:
            raise AttributeError("hostname not set")

        if not self.domain:
            raise AttributeError("domain not set")

        return f"{self.hostname}.{self.domain}"

    def task(self, task: Task) -> Runner:
        """Assigns a task to be run."""

        return Runner(task=task, host=self)

    def run_task(self, task: Task) -> Result:
        """Assign the task to the host and then run it."""

        return self.task(task).run()

    def results(self) -> Results:
        """Fetch recent results of current host from database."""
        return self.pipe(Results.by_host)


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

            def _loader(f: t.TextIO) -> Hosts:
                return cls.from_items(
                    *(Host(ip.strip()) for ip in f.read().strip().split())
                )

            loader = _loader

        with open(filepath) as f:
            return loader(f)

    def task(self, task: Task) -> Runners:
        """Assigns a task to be run on all the hosts."""

        return Runners.from_items(*(Runner(task=task, host=h) for h in self._all))

    def run_task(self, task: Task, max_workers=Config.max_workers.value) -> Results:
        """Run a task to be run on all hosts and then run it."""

        return self.task(task).run(max_workers=max_workers)

    def run_task_then_pipe(
        self,
        task: Task,
        handler: HandlerType,
        *args,
        max_workers=Config.max_workers.value,
    ) -> object:
        """Assign the task to the host and then run it."""

        return self.run_task(task, max_workers=max_workers).pipe(handler, *args)

    def results(self) -> Results:
        results = []
        for h in self._all:
            for r in h.results():
                results.append(r)
        return Results.from_items(*results)


@dataclass(frozen=True, order=True)
class Task(Item):
    """An infra task."""

    name: str
    command_factory: t.Callable[[Host], t.Sequence[str]]
    timeout: t.Optional[int] = None
    retry: int = 0
    stdout_processor: t.Optional[t.Callable[[str], str]] = None
    stderr_processor: t.Optional[t.Callable[[str], str]] = None
    pre_run: t.Optional[t.Callable[[Runner], None]] = None
    post_run: t.Optional[t.Callable[[Result], None]] = None
    meta: t.Sequence[t.Tuple[object, object]] = ()

    @classmethod
    def from_dict(cls, dict_: t.Dict[str, object]) -> Task:
        """Overriding from_dict()."""

        outp = dict_.get("stdout_processor")
        errp = dict_.get("stderr_processor")
        pre = dict_.get("pre_run")
        post = dict_.get("post_run")

        return cls(
            **dict(
                dict_,
                command_factory=locate(dict_["command_factory"]),
                stdout_processor=locate(outp) if outp else None,
                stderr_processor=locate(errp) if errp else None,
                pre_run=locate(pre) if pre else None,
                post_run=locate(post) if post else None,
                meta=tuple(dict_.get("meta", {}).items()),
            )
        )

    def to_dict(self) -> t.Dict[str, object]:
        """Overriding to_dict()."""

        cf = self.command_factory
        outp = self.stdout_processor
        errp = self.stderr_processor
        pre = self.pre_run
        post = self.post_run

        return dict(
            vars(self),
            command_factory=f"{cf.__module__}.{cf.__qualname__}",
            stdout_processor=f"{outp.__module__}.{outp.__qualname__}" if outp else None,
            stderr_processor=f"{errp.__module__}.{errp.__qualname__}" if errp else None,
            pre_run=f"{pre.__module__}.{pre.__qualname__}" if pre else None,
            post_run=f"{post.__module__}.{post.__qualname__}" if post else None,
            meta=dict(self.meta),
        )

    def results(self) -> Results:
        """Get the past results of this task."""

        return self.pipe(Results.by_task)


@dataclass(frozen=True, order=True)
class Runner(Item):
    """A runner."""

    host: Host
    task: Task

    @classmethod
    def from_dict(cls, dict_: t.Dict[str, object]) -> Runner:
        """Overriding from_dict()."""

        return cls(
            **dict(
                dict_,
                task=Task.from_dict(dict_["task"]),
                host=Host.from_dict(dict_["host"]),
            )
        )

    def to_dict(self) -> t.Dict[str, object]:
        """Overriding to_dict()."""

        return dict(vars(self), task=self.task.to_dict(), host=self.host.to_dict())

    def run(self, retry: int = 0) -> Result:
        """Run the task on the host."""

        if self.task.pre_run:
            self.task.pre_run(self)

        command = self.task.command_factory(self.host)
        start = time()

        try:
            r = subprocess.run(
                command,
                timeout=self.task.timeout,
                encoding="latin1",
                capture_output=True,
            )
            stdout, stderr, returncode = r.stdout, r.stderr, r.returncode
        except Exception as e:
            stdout, stderr, returncode = "", str(e), 123

        end = time()

        if self.task.stderr_processor:
            stdout = self.task.stdout_processor(stdout)

        if self.task.stderr_processor:
            stderr = self.task.stderr_processor(stderr)

        result = Result(
            self.task, self.host, command, stdout, stderr, returncode, start, end, retry
        ).save()

        if self.task.post_run:
            self.task.post_run(result)

        if result.errored() and result.retry_left():
            return self.run(retry=retry + 1)

        return result

    def results(self) -> Results:
        """Fetch recent results of current runner from database."""
        return self.pipe(Results.by_runner)


@dataclass(frozen=True)
class Runners(Items):
    _item_factory: t.Type[Runner] = field(init=False, default=Runner)

    def run(self, max_workers=Config.max_workers.value) -> Results:
        """Run the tasks."""

        if max_workers <= 1:
            # Run in sequence
            return Results.from_items(*(r.run() for r in self._all))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Run in parallel
            futures = [executor.submit(r.run) for r in self._all]
            results = [f.result() for f in as_completed(futures)]

        return Results.from_items(*results)

    def hosts(self) -> Hosts:
        """Get the list of hosts from the runners."""
        return Hosts.from_items(*(t.host for t in self._all))


@dataclass(frozen=True, order=True)
class Result(Item):
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
    def by_hash(cls, hash_: int) -> Result:
        with ViperDB(ViperDB.url) as conn:

            data = next(
                conn.execute(
                    """
                    SELECT
                        task, host, command, stdout, stderr, returncode, start, end, retry
                    FROM results WHERE hash = ?
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
    def from_dict(cls, dict_: t.Dict[str, object]) -> Task:
        """Overriding from_dict()."""

        return cls(
            **dict(
                dict_,
                command=tuple(dict_["command"]),
                task=Task.from_dict(dict_["task"]),
                host=Host.from_dict(dict_["host"]),
            )
        )

    def to_dict(self) -> t.Dict[str, object]:
        """Overriding to_dict()."""

        return dict(vars(self), task=self.task.to_dict(), host=self.host.to_dict())

    def ok(self) -> bool:
        """If the result is success."""
        return self.returncode == 0

    def errored(self) -> bool:
        """If the result is failure."""
        return self.returncode != 0

    def retry_left(self) -> int:
        """Get how many retries are left."""
        return self.task.retry - self.retry

    def save(self) -> Result:
        """Save the result dump."""

        with ViperDB() as conn:
            conn.execute(
                """
                INSERT INTO results (
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


@dataclass(frozen=True)
class Results(Items):
    _item_factory: t.Type[Results] = field(init=False, default=Result)

    @classmethod
    def by_host(cls, host: Host) -> Results:
        with ViperDB(ViperDB.url) as conn:
            rows = conn.execute(
                f"""
                SELECT hash FROM results
                WHERE JSON_EXTRACT(host, '$.ip') = ?
                ORDER BY start DESC
                """,
                (host.ip,),
            )
            results = [cls._item_factory.by_hash(r[0]) for r in rows]

        return cls.from_items(*results)

    @classmethod
    def by_task(cls, task: Task) -> Results:
        with ViperDB(ViperDB.url) as conn:
            rows = conn.execute(
                f"""
                SELECT hash FROM results
                WHERE JSON_EXTRACT(task, '$.name') = ?
                ORDER BY start DESC
                """,
                (task.name,),
            )
            results = [cls._item_factory.by_hash(r[0]) for r in rows]

        return cls.from_items(*results)

    @classmethod
    def by_runner(cls, runner: Runner) -> Results:
        with ViperDB(ViperDB.url) as conn:
            rows = conn.execute(
                f"""
                SELECT hash FROM results
                WHERE JSON_EXTRACT(host, '$.ip') = ?
                    AND JSON_EXTRACT(task, '$.name') = ?
                ORDER BY start DESC
                """,
                (runner.host.ip, runner.task.name),
            )
            results = [cls._item_factory.by_hash(r[0]) for r in rows]

        return cls.from_items(*results)

    def hosts(self) -> Hosts:
        """Get the list of hosts from the results."""
        return Hosts.from_items(*(r.host for r in self._all))
