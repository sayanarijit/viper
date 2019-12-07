from viper.cli import __doc__
from viper.cli import func

import pytest
import subprocess


def test_all_cli_examples():
    lines = [
        line.strip()
        for line in __doc__.splitlines()
        if line.startswith("   ") and not line.strip().startswith("#")
    ]

    commands = []
    buffr = []
    for line in lines:
        if line.endswith("\\"):
            buffr.append(line)
            continue

        if buffr:
            commands.append("\n".join(buffr + [line]))
            del buffr[:]
            continue
        commands.append(line)

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
    p = subprocess.Popen(["viper"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()

    assert p.returncode == 1
    assert "usage: viper" in out.decode()
