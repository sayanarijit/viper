from __future__ import annotations

import typing as t
from dataclasses import dataclass, field
from json import dumps as dumpjson
from json import loads as loadjson
from pydoc import locate


@dataclass(frozen=True, order=True)
class Item:
    """A single item."""

    @classmethod
    def from_dict(cls, dict_: t.Dict[str, t.Any]) -> Item:
        """Initialize item from given dict."""

        return cls(**dict_)

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

        return cls.from_items(*map(cls._item_factory.from_dict, list_))

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
    def from_obj(cls, objpath: str) -> Item:
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
