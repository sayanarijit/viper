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


def flatten_dict(d: t.Dict[t.Any, t.Any]) -> t.Dict[str, object]:
    def items() -> t.Iterable[t.Tuple[str, object]]:
        for key, value in d.items():
            if not isinstance(key, str):
                raise ValueError(f"{key}: expected {str}, but got {type(key)}")
            if isinstance(value, dict):
                for subkey, subvalue in flatten_dict(value).items():
                    if not isinstance(subkey, str):
                        raise ValueError(
                            f"{subkey}: expected {str}, but got {type(subkey)}"
                        )
                    yield key + ":" + subkey, subvalue
            else:
                yield key, value

    return dict(items())


def unflatten_dict(d: t.Dict[object, object]) -> t.Dict[object, object]:
    dict_: t.Dict[object, object] = {}
    for k, v in d.items():
        if not isinstance(k, str):
            raise ValueError(f"{k}: expected {str}, but got {type(k)}")

        if ":" in k:
            _dict: t.Union[object, t.Dict[object, object]] = dict_
            fields = k.split(":")
            count = len(fields)
            for i in range(count):
                field = fields[i]
                if not isinstance(_dict, dict):
                    continue
                if field not in _dict:
                    _dict[field] = v if i == (count - 1) else {}
                _dict = _dict[field]
        else:
            dict_[k] = v
    return dict_
