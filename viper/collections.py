"""Datatypes for Viper Objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The data types for Viper objects are defined here.
"""

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
import sys
import traceback
import typing as t

CollectionType = t.TypeVar("CollectionType", bound="Item")
ItemType = t.TypeVar("ItemType", bound="Item")
ItemsType = t.TypeVar("ItemsType", bound="Items")

__all__ = [
    "Collection",
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

    def __call__(self, obj: object, *args: object) -> object:
        pass


class FilterType:
    """TODO: This should be a protocol"""

    def __call__(self, obj: object, *args: object) -> bool:
        pass


class CommandFactoryType:
    """TODO: This should be a protocol"""

    pass


@dataclass(frozen=True, order=True)
class Collection:
    """The base collection class.

    This is the parent class for all Viper native objects such as
    :py:class:`viper.collections.Host`, :py:class:`viper.collections.Results` etc.
    """

    def __str__(self):
        return self.to_json()

    def from_json(
        cls: t.Type[CollectionType], json: str, *args: object, **kwargs: object
    ) -> CollectionType:
        """Initialise a new object of this class from the given JSON string.

        :param str json: The JSON data to parse.
        :param object args and kwargs: These will be passed to `json.laods`.

        :rtype: viper.collections.Collection

        :example:

        .. code-block:: python

            Hosts.from_json('[{"ip": "1.1.1.1"}]')
        """
        raise NotImplementedError()

    def to_json(self, *args: object, **kwargs: object) -> str:
        """Represent the collection as JSON data.

        :param object args and kwargs: These will be passed to `json.laods`.

        :rtype: str

        :example:

        .. code-block:: python

            Host("1.2.3.4").to_json(indent=4)
        """
        raise NotImplementedError()

    @classmethod
    def from_func(cls: t.Type[CollectionType], funcpath: str) -> CollectionType:
        """Load the object from the given Python function.

        :param str funcpath: The path to a Python function that returns an
            instance of this class.

        :rtype: Collection

        :example:

        .. code-block:: python

            Task.from_func(ping)

        .. tip:: See :py:class:`viper.demo.tasks.ping`
        """

        func: t.Optional[t.Callable[[], CollectionType]] = locate(funcpath)

        if not func:
            raise ValueError(f"could not resolve {repr(funcpath)}.")

        obj = func()
        if not isinstance(obj, cls):
            raise ValueError(
                f"{repr(funcpath)} does not produce a valid {cls} instance."
            )

        return obj

    def pipe(self: CollectionType, handler: HandlerType, *args: object) -> object:
        """Pipe this object to the given function.

        :param callable handler: A callable that expects this object.
        :param object args: Arguments to be passed to the handler for decision making.

        :example:

        .. code-block:: python

            Hosts.from_items(Host("1.2.3.4")).pipe(hosts2csv)

        .. tip:: See :py:func:`viper.demo.handlers.hosts2csv`
        """
        return handler(self, *args)

    def hash(self: CollectionType) -> int:
        """Get the hash value.

        By convention all Viper native objects are frozen and thus hashable.

        :rtype: int
        """
        return hash(self)


@dataclass(frozen=True, order=True)
class Item(Collection):
    """The base class for a single Viper object.

    :py:class:`viper.collections.Host`, :py:class:`viper.collections.Task` etc. inherits this base class.
    """

    @classmethod
    def from_dict(cls: t.Type[ItemType], dict_: t.Dict[str, object]) -> ItemType:
        """Initialize item from the given dict.

        :param dict dict_: The dictionary containing the properties for this object.

        :rtype: viper.collections.Item

        :example:

        .. code-block:: python

            Host.from_dict({"ip": "1.2.3.4"})
        """

        try:
            return cls(**dict_)
        except Exception:
            raise ValueError(f"invalid input data for {cls.__name__}")

    def to_dict(self: ItemType) -> t.Dict[str, object]:
        """Represent the item as dict.

        :rtype: dict

        :example:

        .. code-block:: python

            Host("1.2.3.4").to_dict()
        """
        return vars(self)

    @classmethod
    def from_json(cls: t.Type[ItemType], json, *args, **kwargs) -> ItemType:
        return cls.from_dict(loadjson(json, *args, **kwargs))

    def to_json(self: ItemType, *args, **kwargs) -> str:
        return dumpjson(self.to_dict(), *args, **kwargs)

    def format(self: Item, template: str) -> str:
        """Get a custom string representation of this object.

        :param str template: The template to be used as `"template".format(**self.to_dict())`
        :rtype: str

        :example:

        .. code-block:: python

            Host("1.2.3.4").format("{ip} {hostname} {meta[tag]}")
        """
        return template.format(**self.to_dict())


@dataclass(frozen=True)
class Items(Collection):
    """The base class for collection objects for a group of similar items.

    :py:class:`viper.collections.Hosts`, :py:class:`viper.collections.Results` etc. inherits this base class.
    """

    _all: t.Sequence[Item] = ()
    _item_factory: t.Type[Item] = field(init=False)

    @classmethod
    def from_items(cls: t.Type[Item], *items: Item) -> ItemsType:
        """Create this an instance of this object using the given items.

        :param viper.collections.Item items: The group of items to hold.

        :rtype: viper.collections.Items

        .. note::
            Classes that inherits from :py:class:`Items` should not be
            initialized directly (e.g. ``Hosts(Host("1.2.3.4"))``). Factory
            methods such as this should be used instead.

        :example:

        .. code:: python

            Hosts.from_items(Host("1.2.3.4"))
        """
        return cls(tuple(set(items)))

    @classmethod
    def from_list(
        cls: t.Type[ItemsType], list_: t.Sequence[t.Dict[str, object]]
    ) -> ItemsType:
        """Initialize items from given list of dictiionaries.

        :param list list_: The list of dictiionaries containing the item properties.

        :rtype: viper.collections.Items

        This is used for loading JSON data into an instance of this class.

        :example:

        .. code:: python

            Hosts.from_list([{"ip": "1.2.3.4"}])
        """

        if cls._item_factory is None:
            raise NotImplementedError()

        try:
            return cls.from_items(*map(cls._item_factory.from_dict, list_))
        except Exception:
            raise ValueError(f"invalid input data for {cls.__name__}")

    def to_list(self: ItemsType) -> t.List[t.Dict[str, object]]:
        """Represent the items as a list of dictiionaries.

        This is used for dumping an instance of this object as JSON data.

        :rtype: list

        :example:

        .. code:: python

            Hosts.from_items(Host("1.2.3.4")).to_list()
        """

        return [i.to_dict() for i in self._all]

    @classmethod
    def from_json(
        cls: t.Type[ItemsType], json: str, *args: object, **kwargs: object
    ) -> ItemsType:

        return cls.from_list(loadjson(json))

    def to_json(self: ItemsType, *args: object, **kwargs: object) -> str:

        return dumpjson(self.to_list(), *args, **kwargs)

    def __getitem__(self: ItemsType, key: int) -> Item:
        return self._all[key]

    def __len__(self: ItemsType) -> int:
        return len(self._all)

    def count(self: ItemsType) -> int:
        """Count the number of items.

        :rtype: int
        """
        return len(self)

    def first(self: ItemsType) -> Item:
        """Get the first item from the group of items.

        :rtype: viper.collections.Item
        """
        return self[0]

    def last(self: ItemsType) -> Item:
        """Get the last item from the group of items.

        :rtype: viper.collections.Item
        """
        return self[-1]

    def index(self: ItemsType, index: int) -> Item:
        """The the item from a given index.

        :param int index: Index number.

        :rtype: viper.collections.Item
        """
        return self[index]

    def range(
        self: ItemsType, i: t.Optional[int] = None, j: t.Optional[int] = None
    ) -> t.Sequence[Item]:
        """get the items in given range.

        :param int i (optional): The first index.
        :param int j (optional): The last index.

        :rtype: tuple

        This has the same behaviour as Python's [i:j]
        """
        return self._all[i:j]

    def sort(
        self: ItemsType, key: t.Optional[t.Callable[[Item], object]] = None
    ) -> ItemsType:
        """Sort the items by given key/function.

        :param callable key: A function similar to the one passed to the built-in `sorted()`.
        """
        return type(self)(tuple(sorted(self._all, key=key)))

    def filter(self: ItemsType, filter_: FilterType, *args: object) -> ItemsType:
        """Filter the items by a given function.

        :param callable filter_: A function that returns either True or False.
        :param object args: Arguments to be passed to the filter to manipulate the decision making.
        """
        return type(self)(tuple(filter(lambda i: filter_(i, *args), self._all)))

    def all(self: ItemsType) -> t.Sequence[Item]:
        """Get a tuple of all the items.

        :rtype: tuple
        """
        return self._all

    def format(self: ItemsType, template: str, sep="\n") -> str:
        """Get a custom string representation of this list of objects.

        :param str template: The template to be used as `"template".format(**item.to_dict())`
        :param str sep: The separator used to separate all the items.

        :rtype: str

        :example:

        .. code-block:: python

            Hosts.from_items(Host("1.2.3.4")).format("{ip} {hostname} {meta[tag]}")
        """
        return sep.join(template.format(**x.to_dict()) for x in self._all)


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
        return cls(**dict(dict_, meta=tuple(dict_.get("meta", {}).items())))

    def to_dict(self):
        return dict(vars(self), meta=dict(self.meta))

    def fqdn(self) -> str:
        """Get the FQDN from hostname and domain name.

        :rtype: str

        :raises ValueError: If either of hostname or domain name is not set.
        """

        if not self.hostname and not self.domain:
            raise AttributeError("hostname and domain not set")

        if not self.hostname:
            raise AttributeError("hostname not set")

        if not self.domain:
            raise AttributeError("domain not set")

        return f"{self.hostname}.{self.domain}"

    def task(self, task: Task, *args: str) -> Runner:
        """Assigns a task to be run.

        :param viper.collections.Task task: The task to be assigned.
        :param str args: The arguments to be used to create the command from `command_factory`.

        :rtype: viper.collections.Runner

        :example:

        .. code-block:: python

            Host("1.2.3.4").task(ping)

        .. tip:: See :py:class:`viper.demo.tasks.ping`
        """

        return Runner(task=task, host=self, args=args)

    def run_task(self, task: Task, *args: str) -> Result:
        """Assign the task to the host and then run it.

        :param viper.collections.Task task: The task to be assigned.
        :param str args: The arguments to be used to create the command
            from :py:attr:`viper.collections.Task.command_factory`.

        :rtype: viper.collections.Result

        :example:

        .. code-block:: python

            Host("1.2.3.4").task_task(ping)

        .. tip:: See :py:class:`viper.demo.tasks.ping`
        """

        return self.task(task, *args).run()

    def results(self) -> Results:
        """Fetch recent results of current host from database."""
        return self.pipe(Results.by_host)


@dataclass(frozen=True)
class Hosts(Items):
    """A group of :py:class:`viper.collections.Host` objects.

    .. tip:: See :py:mod:`viper.demo.hosts`
    """

    _item_factory: t.Type[Host] = field(init=False, default=Host)

    @classmethod
    def from_file(
        cls, filepath: str, loader: t.Optional[t.Callable[[t.TextIO], "Hosts"]] = None
    ) -> Hosts:
        """Initialize hosts by reading data from a file.

        :param filepath str: The path for the file to read from.
        :param callable loader (optional): A custom loader.

        :rtype: viper.collections.Hosts

        :example:

        .. code-block:: python

            Host("1.2.3.4").from_file("/path/to/file/hosts.json", loader=viper.demo.loader.json)

        .. tip:: See :py:func:`viper.demo.loaders.json`
        """

        if loader is None:

            def _loader(f: t.TextIO) -> Hosts:
                return cls.from_items(
                    *(Host(ip.strip()) for ip in f.read().strip().split())
                )

            loader = _loader

        with open(filepath) as f:
            return loader(f)

    def task(self, task: Task, *args: str) -> Runners:
        """Assigns a task to be run on each host in the group.

        :param viper.collections.Task task: The task to be assigned.
        :param str args: The arguments to be used to create the command from `command_factory`.

        :rtype: viper.collections.Runners

        :example:

        .. code-block:: python

            Hosts.from_items(Host("1.2.3.4")).task(ping)

        .. tip:: See :py:class:`viper.demo.tasks.ping`
        """

        return Runners.from_items(
            *(Runner(task=task, host=h, args=args) for h in self._all)
        )

    def run_task(
        self, task: Task, *args: str, max_workers=Config.max_workers.value
    ) -> Results:
        """Assign the task to the host and then run it.

        :param viper.collections.Task task: The task to be assigned.
        :param str args: The arguments to be used to create the command
            from :py:attr:`viper.collections.Task.command_factory`.
        :param int max_workers: Maximum number of thread workers.
            if the value is <= 1, tasks will run in sequence.

        :rtype: viper.collections.Results

        :example:

        .. code-block:: python

            Hosts.from_items(Host("1.2.3.4")).task_task(ping)

        .. tip:: See :py:class:`viper.demo.tasks.ping`
        """
        return self.task(task, *args).run(max_workers=max_workers)

    def results(self) -> Results:
        """Get the past results of this group of hosts from history.

        :rtype: viper.collections.Results
        """
        results = []
        for h in self._all:
            for r in h.results():
                results.append(r)
        return Results.from_items(*results)


@dataclass(frozen=True, order=True)
class Task(Item):
    """A task is a definition of a single operation.

    A task must contain name and a **named function** to generate the
    command.

    .. tip:: See :py:mod:`viper.demo.tasks`
    """

    name: str
    command_factory: CommandFactoryType
    timeout: t.Optional[int] = None
    retry: int = 0
    stdout_processor: t.Optional[t.Callable[[str], str]] = None
    stderr_processor: t.Optional[t.Callable[[str], str]] = None
    pre_run: t.Optional[t.Callable[[Runner], None]] = None
    post_run: t.Optional[t.Callable[[Result], None]] = None
    meta: t.Sequence[t.Tuple[object, object]] = ()

    @classmethod
    def from_dict(cls, dict_: t.Dict[str, object]) -> Task:
        outp = dict_.get("stdout_processor")
        errp = dict_.get("stderr_processor")
        pre = dict_.get("pre_run")
        post = dict_.get("post_run")
        cf = locate(dict_["command_factory"])
        if not cf:
            raise ValueError(f"could not locate {repr(dict_['command_factory'])}")

        return cls(
            **dict(
                dict_,
                command_factory=cf,
                stdout_processor=locate(outp) if outp else None,
                stderr_processor=locate(errp) if errp else None,
                pre_run=locate(pre) if pre else None,
                post_run=locate(post) if post else None,
                meta=tuple(dict_.get("meta", {}).items()),
            )
        )

    def to_dict(self) -> t.Dict[str, object]:
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
        """Get the past results of this task.

        :rtype: Rviper.collections.esults
        """
        return self.pipe(Results.by_task)


@dataclass(frozen=True, order=True)
class Runner(Item):
    """A single task runner.

    A runner owns the responsibility of actually generating and running
    the command, store the result, calling, retrying, etc.
    We generally do not use it directly.
    """

    host: Host
    task: Task
    args: t.Sequence[str] = ()

    @classmethod
    def from_dict(cls, dict_: t.Dict[str, object]) -> Runner:
        return cls(
            **dict(
                dict_,
                task=Task.from_dict(dict_["task"]),
                host=Host.from_dict(dict_["host"]),
                args=tuple(dict_.get("args", [])),
            )
        )

    def to_dict(self) -> t.Dict[str, object]:
        return dict(vars(self), task=self.task.to_dict(), host=self.host.to_dict())

    def run(self, retry: int = 0, trigger_time: t.Optional[float] = None) -> Result:
        """Run the task on the host.

        :param int retry: Count of retries used.
        :param float trigger_time (optional): The trigger time used for grouping (auto generated).

        :rtype: viper.collections.Result
        """
        if not trigger_time:
            trigger_time = time()

        if not all(isinstance(a, str) for a in self.args):
            raise ValueError("{self.args}: args must be a list/tuple of strings.")

        command = self.task.command_factory(self.host, *self.args)

        if not command:
            raise ValueError(
                f"{self.task.command_factory} generated empty command ({command})."
            )

        if not all(isinstance(c, str) for c in command):
            raise ValueError(f"{command}: command must be a list/tuple of strings.")

        if self.task.pre_run:
            self.task.pre_run(self)

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
            trigger_time,
            self.task,
            self.host,
            self.args,
            command,
            stdout,
            stderr,
            returncode,
            start,
            end,
            retry,
        ).save()

        if self.task.post_run:
            self.task.post_run(result)

        if result.errored() and result.retry_left():
            return self.run(trigger_time=trigger_time, retry=retry + 1)

        return result

    def results(self) -> Results:
        """Fetch recent results of current runner from database.

        :rtype: viper.collections.Results
        """
        return self.pipe(Results.by_runner)


@dataclass(frozen=True)
class Runners(Items):
    _item_factory: t.Type[Runner] = field(init=False, default=Runner)

    def run(self, max_workers: int = Config.max_workers.value) -> Results:
        """Run the tasks.

        :param int max_workers: Maximum number of thread workers to use.

        :rtype: viper.collections.Results
        """

        trigger_time = time()

        if max_workers <= 1:
            # Run in sequence
            results = []
            for r in self.all():
                try:
                    results.append(r.run(trigger_time=trigger_time))
                except Exception:
                    print(traceback.format_exc(), file=sys.stderr)
            return Results.from_items(*results)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Run in parallel
            futures = [executor.submit(r.run) for r in self._all]
            results = []
            for f in as_completed(futures):
                try:
                    results.append(f.result())
                except Exception:
                    print(traceback.format_exc(), file=sys.stderr)

        return Results.from_items(*results)

    def hosts(self) -> Hosts:
        """Get the list of hosts from the runners.

        :rtype: viper.collections.Hosts
        """
        return Hosts.from_items(*(t.host for t in self._all))


@dataclass(frozen=True, order=True)
class Result(Item):
    """The result of an executed task."""

    trigger_time: float
    task: Task
    host: Host
    args: t.Sequence[str]
    command: t.Sequence[str]
    stdout: str
    stderr: str
    returncode: int
    start: float
    end: float
    retry: int

    @classmethod
    def by_hash(cls, hash_: int) -> Result:
        """Fetch the result from DB by hash.

        :param int hash_: The hash value.

        :rtype: viper.collections.Result
        """

        with ViperDB(ViperDB.url) as conn:

            data = next(
                conn.execute(
                    """
                    SELECT
                        trigger_time, task, host, args, command, stdout, stderr,
                        returncode, start, end, retry
                    FROM results WHERE hash = ?
                    """,
                    (hash_,),
                )
            )

        return cls.from_dict(
            dict(
                trigger_time=data[0],
                task=loadjson(data[1]),
                host=loadjson(data[2]),
                args=tuple(loadjson(data[3])),
                command=tuple(loadjson(data[4])),
                stdout=data[5],
                stderr=data[6],
                returncode=data[7],
                start=data[8],
                end=data[9],
                retry=data[10],
            )
        )

    @classmethod
    def from_dict(cls, dict_: t.Dict[str, object]) -> Task:
        return cls(
            **dict(
                dict_,
                args=tuple(dict_["args"]),
                command=tuple(dict_["command"]),
                task=Task.from_dict(dict_["task"]),
                host=Host.from_dict(dict_["host"]),
            )
        )

    def to_dict(self) -> t.Dict[str, object]:
        return dict(vars(self), task=self.task.to_dict(), host=self.host.to_dict())

    def ok(self) -> bool:
        """Returns True the result is success.

        :rtype: bool
        """
        return self.returncode == 0

    def errored(self) -> bool:
        """returns True if the result is failure.

        :rtype: bool
        """
        return self.returncode != 0

    def retry_left(self) -> int:
        """Get how many retries are left.

        :rtype: int
        """
        return self.task.retry - self.retry

    def save(self) -> Result:
        """Save the result in DB.

        :rtype: viper.collections.Result
        """

        with ViperDB() as conn:
            conn.execute(
                """
                INSERT INTO results (
                    hash, trigger_time, task, host, args, command,
                    stdout, stderr, returncode, start, end, retry
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    self.hash(),
                    self.trigger_time,
                    self.task.to_json(),
                    self.host.to_json(),
                    dumpjson(self.args),
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
    """A group of :py:class:`viper.collections.Results`."""

    _item_factory: t.Type[Results] = field(init=False, default=Result)

    @classmethod
    def from_history(cls) -> Results:
        """Fetch and return all the results from history.

        :rtype: ciper.collections.Results
        """
        with ViperDB(ViperDB.url) as conn:
            rows = conn.execute("SELECT hash FROM results ORDER BY start DESC")
            results = [cls._item_factory.by_hash(r[0]) for r in rows]

        return cls.from_items(*results)

    @classmethod
    def by_host(cls, host: Host) -> Results:
        """Fetch and return results from history of the given host.

        :param viper.collections.Host host: Fetch results of this host.
        :rtype: viper.collections.Results
        """
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
        """Fetch and return results from history of the given task.

        :param viper.collections.Host host: Fetch results of this task.
        :rtype: viper.collections.Results
        """
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

    def hosts(self) -> Hosts:
        """Get the list of hosts from the results.

        :rtype: viper.collections.Hosts
        """
        return Hosts.from_items(*(r.host for r in self._all))
