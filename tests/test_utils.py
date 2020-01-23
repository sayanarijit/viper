from viper.utils import flatten_dict
from viper.utils import optional
from viper.utils import required
from viper.utils import unflatten_dict

import pytest


def test_optional():
    assert optional({"key": "val"}, "key", str) == "val"
    assert optional({}, "key", str) is None
    assert optional({"key": None}, "key", str) is None
    assert (
        optional({"key": None}, "key", str, parser=lambda dict_, key: dict_.get(key))
        is None
    )

    with pytest.raises(ValueError) as e:
        optional({"key": 1}, "key", str)
    assert "invalid type" in str(vars(e))


def test_required():
    assert required({"key": "val"}, "key", str) == "val"
    assert (
        required({"key": "val"}, "key", str, parser=lambda dict_, key: dict_.get(key))
        == "val"
    )
    assert required({}, "key", str, default="val") == "val"
    assert required({"key": None}, "key", str, default_factory=lambda: "val") == "val"

    with pytest.raises(ValueError) as e:
        required({"key": 1}, "key", str)
    assert "invalid type" in str(vars(e))

    with pytest.raises(ValueError) as e:
        required({"key": None}, "key", str)
    assert "value is required" in str(vars(e))

    with pytest.raises(ValueError) as e:
        required({}, "key", str)
    assert "value is required" in str(vars(e))


def test_flatten_dict():
    assert flatten_dict({"a": 1, "b": {"c": 2, "d": 3}}) == {"a": 1, "b:c": 2, "b:d": 3}


def test_unflatten_dict():
    assert unflatten_dict({"a": 1, "b:c": 2, "b:d": 3}) == {
        "a": 1,
        "b": {"c": 2, "d": 3},
    }
