from viper import Host
from viper import Hosts
from viper import meta
from viper.serializers import _dump_csv
from viper.serializers import _load_csv
from viper.serializers import Serializers

import json
import yaml


def test_serializers_json():
    assert json.dumps(
        Serializers.json.value.load(Host("1.1.1.1").to_json()), indent=4
    ) == Serializers.json.value.dump(Host("1.1.1.1").to_dict())


def test_serializers_yaml_dump():
    assert yaml.safe_dump(
        Host("1.1.1.1").to_dict(), default_flow_style=False
    ) == Serializers.yml.value.dump(Host("1.1.1.1").to_dict())


def test_serializers_yaml_load():
    dumped = Serializers.yml.value.dump(Host("1.1.1.1").to_dict())
    assert yaml.safe_load(dumped) == Serializers.yml.value.load(dumped)


def test_serializer_dump_csv():

    csv = _dump_csv(
        Hosts.from_items(Host("1.1.1.1", meta=meta(foo="bar"))).to_list(flatten=True)
    )
    assert (
        "ip,hostname,domain,port,login_name,identity_file,meta:foo"
        in csv.splitlines()[0]
    )
    assert "1.1.1.1" in csv.splitlines()[1]
    assert "bar" in csv.splitlines()[1].split(",")[6]


def test_serializer_load_csv():

    csv = _dump_csv(
        Hosts.from_items(Host("1.1.1.1", meta=meta(foo="bar"))).to_list(flatten=True)
    )

    assert _load_csv(csv) == Hosts.from_items(
        Host("1.1.1.1", meta=meta(foo="bar"))
    ).to_list(flatten=True)


def test_serializers_csv():
    data = Hosts.from_items(Host("1.1.1.1", meta=meta(foo="bar"))).to_list(flatten=True)
    csv = Serializers.csv.value.dump(data)

    assert Serializers.csv.value.load(csv) == data
