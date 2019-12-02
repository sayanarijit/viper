from viper.cli import func
from viper.demo import __doc__ as examples_doc

import pytest
import subprocess


def test_all_cli_examples():

    commands = [
        line.strip()
        for line in examples_doc.splitlines()
        if line.startswith("   ") and not line.strip().startswith("#")
    ]

    assert subprocess.run(["viper", "init", "-f"]).returncode == 0

    for command in commands:
        print(command)
        assert subprocess.run(command, shell=True).returncode == 0


def test_load_func_errors():
    with pytest.raises(ValueError) as e:
        func("xyz")
        assert "coud not resolve" in str(vars(e))

    with pytest.raises(ValueError) as e:
        func("viper")
        assert "not a valid function" in str(vars(e))


def test_print_usage():
    p = subprocess.Popen(
        ["python", "-m", "viper.main"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    out, err = p.communicate()
    assert p.returncode == 1
    assert "usage: viper" in out.decode()
