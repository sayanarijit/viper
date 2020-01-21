"""Datatypes for Viper Objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The data types for Viper objects are defined here.
"""

from __future__ import annotations
from collections import OrderedDict
from collections.abc import Iterable
from concurrent.futures import as_completed
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from json import dumps as dumpjson
from json import loads as loadjson
from pydoc import locate
from time import time
from types import FunctionType
from viper.const import Config
from viper.db import ViperDB
from viper.utils import optional
from viper.utils import required

import subprocess
import sys
import traceback
import typing as t

__all__ = [
    "WhereConditions",
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
]


T = t.TypeVar("T")
C = t.TypeVar("C")
CollectionType = t.TypeVar("CollectionType", bound="Collection")
ItemType = t.TypeVar("ItemType", bound="Item")
ItemsType = t.TypeVar("ItemsType", bound="Items[t.Any]")
JSONValueType = t.Optional[t.Union[str, bool, int, float]]
MetaType = t.Dict[str, JSONValueType]


class WhereConditions(Enum):
    """Where query conditions for viper Items"""

    is_ = "IS"
    is_not = "IS_NOT"
    contains = "CONTAINS"
    not_contains = "NOT_CONTAINS"
    startswith = "STARTSWITH"
    not_startswith = "NOT_STARTSWITH"
    endswith = "ENDSWITH"
    not_endswith = "NOT_ENDSWITH"


@dataclass(frozen=True, order=True)
class Collection:
    """The base collection class.

    This is the parent class for all Viper native objects such as
    :py:class:`viper.collections.Host`, :py:class:`viper.collections.Results` etc.
    """

    def __str__(self) -> str:
        return self.to_json()

    @classmethod
    def from_json(
        cls: t.Type[CollectionType], json: str, *args: t.Any, **kwargs: t.Any
    ) -> CollectionType:  # pragma: no cover
        """Initialise a new object of this class from the given JSON string.

        :param str json: The JSON data to parse.
        :param object args and kwargs: These will be passed to `json.laods`.

        :rtype: viper.collections.Collection

        :example:

        .. code-block:: python

            Hosts.from_json('[{"ip": "1.1.1.1"}]')
        """
        raise NotImplementedError()

    def to_json(self, *args: t.Any, **kwargs: t.Any) -> str:  # pragma: no cover
        """Represent the collection as JSON data.

        :param object args and kwargs: These will be passed to `json.laods`.

        :rtype: str

        :example:

        .. code-block:: python

            Host("1.2.3.4").to_json(indent=4)
        """
        raise NotImplementedError()

    @classmethod
    def from_func(cls: t.Type[CollectionType], funcpath: str, /) -> CollectionType:
        """Load the object from the given Python function.

        :param str funcpath: The path to a Python function that returns an
            instance of this class.

        :rtype: Collection

        :example:

        .. code-block:: python

            Task.from_func(ping)

        .. tip:: See :py:class:`viper.demo.tasks.ping`
        """

        func: object = locate(funcpath)

        if not func:
            raise ValueError(f"could not resolve {repr(funcpath)}.")

        if not callable(func):
            raise ValueError(f"{repr(funcpath)} is not callable.")

        obj = func()
        if not isinstance(obj, cls):
            raise ValueError(
                f"{repr(funcpath)} does not produce a valid {cls} instance."
            )

        return obj

    def pipe(self, handler: t.Any, *args: t.Any) -> T:
        """Pipe this object to the given function.

        :param callable handler: A callable that expects this object.
        :param object args: Arguments to be passed to the handler for decision making.

        :example:

        .. code-block:: python

            Hosts.from_items(Host("1.2.3.4")).pipe(hosts2csv)

        .. tip:: See :py:func:`viper.demo.handlers.hosts2csv`
        """
        if not callable(handler):
            raise ValueError(f"{handler}: expected a callable but got {type(handler)}")

        res = t.cast(T, handler(self, *args))
        return res

    def hash(self) -> int:
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
    def from_dict(
        cls: t.Type[ItemType], dict_: t.Dict[object, object], /,
    ) -> ItemType:  # pragma: no cover
        """Initialize item from the given dict.

        :param dict dict_: The dictionary containing the properties for this object.

        :rtype: viper.collections.Item

        :example:

        .. code-block:: python

            Host.from_dict({"ip": "1.2.3.4"})
        """
        raise NotImplementedError()

    def to_dict(self) -> t.Dict[str, object]:  # pragma: no cover
        """Represent the item as dict.

        :rtype: dict

        :example:

        .. code-block:: python

            Host("1.2.3.4").to_dict()
        """
        raise NotImplementedError()

    @classmethod
    def from_json(
        cls: t.Type[ItemType], json: str, *args: t.Any, **kwargs: t.Any
    ) -> ItemType:
        return cls.from_dict(loadjson(json, *args, **kwargs))

    def to_json(self, *args: t.Any, **kwargs: t.Any) -> str:
        return dumpjson(self.to_dict(), *args, **kwargs)

    def format(self, template: str) -> str:
        """Get a custom string representation of this object.

        :param str template: The template to be used as `"template".format(**self.to_dict())`
        :rtype: str

        :example:

        .. code-block:: python

            Host("1.2.3.4").format("{ip} {hostname} {meta[tag]}")
        """
        return template.format(**self.to_dict())


@dataclass(frozen=True)
class Items(Collection, t.Generic[T]):
    """The base class for collection objects for a group of similar items.

    :py:class:`viper.collections.Hosts`, :py:class:`viper.collections.Results` etc. inherits this base class.
    """

    _all: t.Sequence[T] = ()
    _item_type: t.Type[Item] = field(init=False)

    @classmethod
    def from_items(
        cls: t.Type[ItemsType], *items: t.Union[t.Iterable[T], T]
    ) -> ItemsType:
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
        items_set: t.Dict[Item, None] = OrderedDict()
        for item in items:
            if not isinstance(item, Item) and not isinstance(item, Iterable):
                raise ValueError(
                    f"{item}: expecting {Item} or generator of 'Item's but got {type(item)}"
                )

            if isinstance(item, Item):
                items_set[item] = None
                continue

            if isinstance(item, Iterable):
                for i in item:
                    if not isinstance(i, Item):
                        raise ValueError(f"{i}: expecting {Item} but got {type(i)}")
                    items_set[i] = None

        return cls(tuple(items_set))

    @classmethod
    def from_list(
        cls: t.Type[ItemsType], list_: t.Sequence[t.Dict[object, object]], /,
    ) -> ItemsType:
        """Initialize items from given list of dictiionaries.

        :param list list_: The list of dictiionaries containing the item properties.

        :rtype: viper.collections.Items

        This is used for loading JSON data into an instance of this class.

        :example:

        .. code:: python

            Hosts.from_list([{"ip": "1.2.3.4"}])
        """

        if cls._item_type is None:  # pragma: no cover
            raise NotImplementedError()

        try:
            return cls.from_items(map(cls._item_type.from_dict, list_))
        except Exception:
            raise ValueError(f"invalid input data for {cls.__name__}")

    def to_list(self) -> t.List[t.Dict[str, object]]:
        """Represent the items as a list of dictiionaries.

        This is used for dumping an instance of this object as JSON data.

        :rtype: list

        :example:

        .. code:: python

            Hosts.from_items(Host("1.2.3.4")).to_list()
        """

        return [i.to_dict() for i in self._all if isinstance(i, Item)]

    @classmethod
    def from_json(
        cls: t.Type[ItemsType], json: str, *args: t.Any, **kwargs: t.Any
    ) -> ItemsType:

        return cls.from_list(loadjson(json))

    def to_json(self, *args: t.Any, **kwargs: t.Any) -> str:

        return dumpjson(self.to_list(), *args, **kwargs)

    def __len__(self) -> int:
        return len(self._all)

    def count(self) -> int:
        """Count the number of items.

        :rtype: int
        """
        return len(self)

    def head(self: ItemsType, n: int = 10) -> ItemsType:
        """Get the first 'n' items from the group of items.

        Works like Python's [:n] index

        :rtype: viper.collections.Item
        """
        return self.range(None, n)

    def tail(self: ItemsType, n: int = 10) -> ItemsType:
        """Get the last 'n' item from the group of items.

        Works like Python's [-n:] index

        :rtype: viper.collections.Item
        """
        return self.range(-n)

    def range(
        self: ItemsType, i: t.Optional[int] = None, j: t.Optional[int] = None
    ) -> ItemsType:
        """get the items in given range.

        :param int i (optional): The first index.
        :param int j (optional): The last index.

        :rtype: Items

        This has the same behaviour as Python's [i:j]
        """
        return type(self).from_items(self._all[i:j])

    def sort(
        self: ItemsType,
        key: t.Optional[t.Callable[[Item], object]] = None,
        reverse: bool = False,
    ) -> ItemsType:
        """Sort the items by given key/function.

        :param callable key: A function similar to the one passed to the built-in `sorted()`.
        :param bool reverse: Reverse the order after sort.

        :rtype: Items
        """
        return type(self)(tuple(sorted(self._all, key=key, reverse=reverse)))

    def order_by(self: ItemsType, *properties: str, reverse: bool = False) -> ItemsType:
        """Sort the items by multiple properties

        :param list properties: The item will be sorted by the given properties in order.
        :param bool reverse: Reverse the order after sort.

        :rtype: Items
        """
        return type(self)(
            tuple(
                sorted(
                    self._all,
                    key=lambda x: [
                        f"{{{p}}}".format(**x.to_dict()) for p in properties
                    ],
                    reverse=reverse,
                )
            )
        )

    def filter(self: ItemsType, filter_: t.Any, *args: object) -> ItemsType:
        """Filter the items by a given function.

        :param callable filter_: A function that returns either True or False.
        :param object args: Arguments to be passed to the filter to manipulate the decision making.
        """
        if not callable(filter_):
            raise ValueError(f"{filter_}: expected a callable, but got {type(filter_)}")

        return type(self)(tuple(filter(lambda i: filter_(i, *args), self._all)))

    def all(self) -> t.Sequence[T]:
        """Get a tuple of all the items.

        :rtype: tuple
        """
        return self._all

    def format(self: ItemsType, template: str, sep: str = "\n") -> str:
        """Get a custom string representation of this list of objects.

        :param str template: The template will be compiled by Python's `.format()`.
        :param str sep: The separator used to separate all the items.

        :rtype: str

        :example:

        .. code-block:: python

            Hosts.from_items(Host("1.2.3.4")).format("{ip} {hostname} {meta[tag]}")
        """
        return sep.join(template.format(**x.to_dict()) for x in self._all)

    def where(
        self: ItemsType, key: str, condition: WhereConditions, values: t.Sequence[str]
    ) -> ItemsType:
        """Select items by a custom query.

        :param str key: The key will be compiled by Python's `.format()`.
        :param viper.collections.WhereConditions condition: The where condition.
        :param list values: The values for the key.

        :rtype: Items
        """
        result = []

        for obj in self._all:
            val = f"{{{key}}}".format(**obj.to_dict())

            if condition is WhereConditions.is_:
                if val in values:
                    result.append(obj)

            elif condition is WhereConditions.is_not:
                if val not in values:
                    result.append(obj)

            elif condition is WhereConditions.contains:
                if any(map(lambda x: x in val, values)):
                    result.append(obj)

            elif condition is WhereConditions.not_contains:
                if any(map(lambda x: x not in val, values)):
                    result.append(obj)

            elif condition is WhereConditions.startswith:
                if any(map(lambda x: val.startswith(x), values)):
                    result.append(obj)

            elif condition is WhereConditions.not_startswith:
                if any(map(lambda x: not val.startswith(x), values)):
                    result.append(obj)

            elif condition is WhereConditions.endswith:
                if any(map(lambda x: val.endswith(x), values)):
                    result.append(obj)

            elif condition is WhereConditions.not_endswith:
                if any(map(lambda x: not val.endswith(x), values)):
                    result.append(obj)

            else:
                raise ValueError(f"expecting enum {WhereConditions}")

        return type(self).from_items(*result)


@dataclass(frozen=True, order=True)
class Host(Item):
    """Viper Host class."""

    ip: str
    hostname: t.Optional[str] = None
    domain: t.Optional[str] = None
    port: int = 22
    login_name: t.Optional[str] = None
    identity_file: t.Optional[str] = None
    meta: t.Sequence[t.Tuple[str, JSONValueType]] = ()

    def __hash__(self) -> int:
        return hash(self.ip)

    def __eq__(self, value: object) -> bool:
        return isinstance(value, self.__class__) and self.ip == value.ip

    @classmethod
    def from_dict(cls: t.Type[Host], dict_: t.Dict[object, object], /) -> Host:
        ip: str = required(dict_, "ip", str)
        hostname = optional(dict_, "hostname", str)
        domain = optional(dict_, "domain", str)
        port = required(dict_, "port", int, default=22)
        login_name = optional(dict_, "login_name", str)
        identity_file = optional(dict_, "identity_file", str)
        meta: MetaType = required(dict_, "meta", dict, default_factory=lambda: {})
        host = cls(
            ip=ip,
            hostname=hostname,
            domain=domain,
            port=port,
            login_name=login_name,
            identity_file=identity_file,
            meta=tuple(meta.items()),
        )
        return host

    def to_dict(self) -> t.Dict[str, object]:
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
        return Results.by_host(self)


@dataclass(frozen=True)
class Hosts(Items[Host]):
    """A group of :py:class:`viper.collections.Host` objects.

    .. tip:: See :py:mod:`viper.demo.hosts`
    """

    _all: t.Sequence[Host] = ()
    _item_type: t.Type[Host] = field(init=False, default=Host)

    @classmethod
    def from_file(
        cls: t.Type[Hosts],
        filepath: str,
        /,
        loader: t.Optional[t.Callable[[t.TextIO], Hosts]] = None,
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
                    Host(ip.strip()) for ip in f.read().strip().split()
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
            Runner(task=task, host=h, args=args) for h in self._all
        )

    def run_task(
        self, task: Task, *args: str, max_workers: int = Config.max_workers.value
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
            for r in h.results().all():
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
    command_factory: t.Any
    timeout: t.Optional[t.Union[int, float]] = None
    retry: int = 0
    stdout_processor: t.Optional[t.Callable[[str], str]] = None
    stderr_processor: t.Optional[t.Callable[[str], str]] = None
    pre_run: t.Optional[t.Callable[[Runner], None]] = None
    post_run: t.Optional[t.Callable[[Result], None]] = None
    meta: t.Sequence[t.Tuple[object, object]] = ()

    @classmethod
    def from_dict(cls: t.Type[Task], dict_: t.Dict[object, object], /) -> Task:

        name: str = required(dict_, "name", str)

        command_factory: FunctionType = required(
            dict_,
            "command_factory",
            FunctionType,
            parser=lambda dict_, key: locate(str(dict_.get(key))),
        )

        timeout = optional(dict_, "timeout", (int, float,))

        retry = required(dict_, "retry", int, default=0)

        stdout_processor = optional(
            dict_,
            "stdout_processor",
            FunctionType,
            parser=lambda dict_, key: locate(str(dict_.get(key))),
        )

        stderr_processor = optional(
            dict_,
            "stderr_processor",
            FunctionType,
            parser=lambda dict_, key: locate(str(dict_.get(key))),
        )

        pre_run = optional(
            dict_,
            "pre_run",
            FunctionType,
            parser=lambda dict_, key: locate(str(dict_.get(key))),
        )

        post_run = optional(
            dict_,
            "post_run",
            FunctionType,
            parser=lambda dict_, key: locate(str(dict_.get(key))),
        )

        meta: MetaType = required(dict_, "meta", dict, default_factory=lambda: {})

        hosts = cls(
            name=name,
            command_factory=command_factory,
            timeout=timeout,
            retry=retry,
            stdout_processor=stdout_processor,
            stderr_processor=stderr_processor,
            pre_run=pre_run,
            post_run=post_run,
            meta=tuple(meta.items()),
        )
        return hosts

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
        return Results.by_task(self)


@dataclass(frozen=True, order=True)
class Runner(Item):
    """A single task runner.

    A runner owns the responsibility of actually generating and running
    the command, store the result, calling, retrying, etc.
    We generally do not use it directly.
    """

    host: Host
    task: Task
    args: t.Tuple[str, ...] = ()

    @classmethod
    def from_dict(cls: t.Type[Runner], dict_: t.Dict[object, object], /) -> Runner:
        host: Host = required(
            dict_,
            "host",
            Host,
            parser=lambda dict_, key: Host.from_dict(
                required(dict_, key, dict, default_factory=dict)
            ),
        )
        task: Task = required(
            dict_,
            "task",
            Task,
            parser=lambda dict_, key: Task.from_dict(
                required(dict_, key, dict, default_factory=dict)
            ),
        )
        args: t.Tuple[str, ...] = tuple(
            required(dict_, "args", list, default_factory=list)
        )
        return cls(host=host, task=task, args=args)

    def to_dict(self) -> t.Dict[str, t.Any]:
        return dict(
            vars(self),
            task=self.task.to_dict(),
            host=self.host.to_dict(),
            args=list(self.args),
        )

    def run(self, retry: int = 0, trigger_time: t.Optional[float] = None) -> Result:
        """Run the task on the host.

        :param int retry: Count of retries used.
        :param float trigger_time (optional): The trigger time used for grouping (auto generated).

        :rtype: viper.collections.Result
        """
        if not trigger_time:
            trigger_time = time()

        if not all(isinstance(a, str) for a in self.args):
            raise ValueError(f"{self.args}: args must be a list/tuple of strings.")

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

        if self.task.stdout_processor is not None:
            stdout = self.task.stdout_processor(stdout)

        if self.task.stderr_processor is not None:
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


@dataclass(frozen=True)
class Runners(Items[Runner]):
    _all: t.Sequence[Runner] = ()
    _item_type: t.Type[Runner] = field(init=False, default=Runner)

    def run(self, max_workers: int = Config.max_workers.value) -> Results:
        """Run the tasks.

        :param int max_workers: Maximum number of thread workers to use.

        :rtype: viper.collections.Results
        """

        trigger_time = time()

        if max_workers <= 1:
            # Run in sequence
            results = []
            for r in self._all:
                try:
                    results.append(r.run(trigger_time=trigger_time))
                except Exception:  # pragma: no cover
                    print(traceback.format_exc(), file=sys.stderr)
            return Results.from_items(*results)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Run in parallel
            futures = [
                executor.submit(r.run, **{"trigger_time": trigger_time})
                for r in self._all
            ]
            results = []
            for f in as_completed(futures):
                try:
                    results.append(f.result())
                except Exception:  # pragma: no cover
                    print(traceback.format_exc(), file=sys.stderr)

        return Results.from_items(*results)

    def hosts(self) -> Hosts:
        """Get the list of hosts from the runners.

        :rtype: viper.collections.Hosts
        """
        return Hosts.from_items(t.host for t in self._all)


@dataclass(frozen=True, order=True)
class Result(Item):
    """The result of an executed task."""

    trigger_time: float
    task: Task
    host: Host
    args: t.Tuple[str, ...]
    command: t.Tuple[str, ...]
    stdout: str
    stderr: str
    returncode: int
    start: float
    end: float
    retry: int

    @classmethod
    def by_id(cls, id_: int) -> Result:
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
                    FROM results WHERE id = ?
                    """,
                    (id_,),
                )
            )

        return cls.from_dict(
            dict(
                trigger_time=data[0],
                task=loadjson(data[1]),
                host=loadjson(data[2]),
                args=loadjson(data[3]),
                command=loadjson(data[4]),
                stdout=data[5],
                stderr=data[6],
                returncode=data[7],
                start=data[8],
                end=data[9],
                retry=data[10],
            )
        )

    @classmethod
    def from_dict(cls: t.Type[Result], dict_: t.Dict[object, object], /) -> Result:
        return cls(
            trigger_time=required(dict_, "trigger_time", float),
            task=required(
                dict_,
                "task",
                Task,
                parser=lambda dict_, key: Task.from_dict(
                    required(dict_, key, dict, default_factory=dict)
                ),
            ),
            host=required(
                dict_,
                "host",
                Host,
                parser=lambda dict_, key: Host.from_dict(
                    required(dict_, key, dict, default_factory=dict)
                ),
            ),
            args=tuple(required(dict_, "args", list, default_factory=list)),
            command=tuple(required(dict_, "command", list, default_factory=list)),
            stdout=required(dict_, "stdout", str),
            stderr=required(dict_, "stderr", str),
            returncode=required(dict_, "returncode", int),
            start=required(dict_, "start", float),
            end=required(dict_, "end", float),
            retry=required(dict_, "retry", int),
        )

    def to_dict(self) -> t.Dict[str, t.Any]:
        return dict(
            vars(self),
            task=self.task.to_dict(),
            host=self.host.to_dict(),
            args=list(self.args),
        )

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

    def runner(self) -> Runner:
        """Recreate the runner from the result.

        :rtype: viper.collections.Runner
        """
        return Runner(host=self.host, task=self.task, args=self.args)


@dataclass(frozen=True)
class Results(Items[Result]):
    """A group of :py:class:`viper.collections.Results`."""

    _all: t.Sequence[Result] = ()
    _item_type: t.Type[Result] = field(init=False, default=Result)

    @classmethod
    def from_history(cls: t.Type[Results], final: bool = False) -> Results:
        """Fetch and return all the results from history.

        :rtype: ciper.collections.Results
        """
        with ViperDB(ViperDB.url) as conn:
            rows = conn.execute("SELECT id FROM results ORDER BY start DESC")
            result_list = [cls._item_type.by_id(r[0]) for r in rows]

        results = cls.from_items(*result_list)
        return results.final() if final else results

    @classmethod
    def by_host(cls, host: Host) -> Results:
        """Fetch and return results from history of the given host.

        :param viper.collections.Host host: Fetch results of this host.
        :rtype: viper.collections.Results
        """
        with ViperDB(ViperDB.url) as conn:
            rows = conn.execute(
                f"""
                SELECT id FROM results
                WHERE JSON_EXTRACT(host, '$.ip') = ?
                ORDER BY start DESC
                """,
                (host.ip,),
            )
            results = [cls._item_type.by_id(r[0]) for r in rows]

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
                SELECT id FROM results
                WHERE JSON_EXTRACT(task, '$.name') = ?
                ORDER BY start DESC
                """,
                (task.name,),
            )
            results = [cls._item_type.by_id(r[0]) for r in rows]

        return cls.from_items(*results)

    def hosts(self) -> Hosts:
        """Get the list of hosts from the results.

        :rtype: viper.collections.Hosts
        """
        return Hosts.from_items(r.host for r in self._all)

    def final(self) -> Results:
        """Get the final results only (ignoring the previous retries).

        :rtype: viper.collections.Results
        """
        results: t.Dict[float, t.Dict[Host, Result]] = {}
        for result in self._all:
            if result.trigger_time not in results:
                results[result.trigger_time] = {result.host: result}
                continue

            res_grp = results[result.trigger_time]
            if result.host not in res_grp:
                res_grp[result.host] = result
                continue

            if res_grp[result.host].retry < result.retry:
                res_grp[result.host] = result

        out = []
        for res_grp in results.values():
            for res in res_grp.values():
                out.append(res)
        return Results.from_items(*out)

    def runners(self) -> Runners:
        """Recreate the runners from the results.

        :rtype: viper.collections.Runners
        """
        return Runners.from_items(r.runner() for r in self._all)

    def re_run(self, max_workers: int = Config.max_workers.value) -> Results:
        """Recreate the runners from the results and run again.

        :rtype: viper.collections.Results
        """
        return self.runners().run(max_workers=max_workers)
