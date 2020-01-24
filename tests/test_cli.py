from viper.cli import func

import pytest
import subprocess


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
