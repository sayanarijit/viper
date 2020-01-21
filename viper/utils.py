from __future__ import annotations

import typing as t

T = t.TypeVar("T")


def optional(
    dict_: t.Dict[object, object],
    /,
    key: object,
    expect: t.Union[type, t.Tuple[type, ...]],
    *,
    parser: t.Optional[t.Callable[[t.Dict[object, object], object], object]] = None,
) -> t.Optional[T]:
    """Get a value safely from the given dict using the given key.
    If the value is not found or is None, return it anyway.

    :raises: ValueError
    """

    if parser is None:
        value = dict_.get(key)
    else:
        value = parser(dict_, key)

    if value is not None and not isinstance(value, expect):
        raise ValueError(
            f"{dict_}: {repr(key)}: {repr(value)}: invalid type {type(value)}, expecting {expect}"
        )
    return t.cast(T, value)


def required(
    dict_: t.Dict[object, object],
    /,
    key: object,
    expect: t.Union[type, t.Tuple[type, ...]],
    *,
    parser: t.Optional[t.Callable[[t.Dict[object, object], object], object]] = None,
    default: t.Optional[T] = None,
    default_factory: t.Optional[t.Callable[[], T]] = None,
) -> T:
    """Get a value safely from the given dict using the given key.
    If the value is not found or is None, raise value error.

    :raises: ValueError
    """
    value: t.Optional[T] = optional(dict_, key, expect, parser=parser)
    if value is None:
        if default is not None:
            return default
        if default_factory is not None:
            return default_factory()
        raise ValueError(f"{dict_}: {repr(key)}: value is required")
    return value
