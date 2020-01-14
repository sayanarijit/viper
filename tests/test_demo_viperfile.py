# NOTE: The code in this tests should exactly match the code examples
# in the docstrings of `viper.demo.viperfile`. Any change whould reflect in the
# examples as well.


import os
import subprocess

RESULTS_PATH = "viper/demo/results.csv"


def run(*command: str, **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="latin1",
        cwd="viper/demo",
        shell=True,
        **kwargs,
    )


def test_print_help():
    res = run("viper -h")
    assert res.returncode == 0
    assert "@myproj:allhosts" in res.stdout


def test_all_hosts():
    res = run("viper @myproj:allhosts")
    assert res.returncode == 0
    assert "999.999.999.999" in res.stdout
    assert "999.000.000.999" in res.stdout
    assert "root" in res.stdout
    assert "/root/.ssh/id_rsa.pub" in res.stdout


def test_hosts2csv():
    if os.path.exists(RESULTS_PATH):
        os.remove(RESULTS_PATH)

    res = run("viper @myproj:allhosts | viper @myproj:hosts2csv results.csv")

    assert res.returncode == 0
    assert "999.999.999.999" in res.stdout
    assert "999.000.000.999" in res.stdout

    assert os.path.exists(RESULTS_PATH)

    with open(RESULTS_PATH) as f:
        data = f.read()

    assert "999.999.999.999" in data
    assert "999.000.000.999" in data


def test_remote_exec():

    if os.path.exists(RESULTS_PATH):
        os.remove(RESULTS_PATH)

    run("viper init -f")
    res = run(
        "viper @myproj:allhosts"
        ' | viper @myproj:remote_exec "df -h" results.csv --max-workers 50'
    )

    assert res.returncode == 0
    assert "999.999.999.999" in res.stdout
    assert "999.000.000.999" in res.stdout
    assert "ssh" in res.stderr
    assert "/root/.ssh/id_rsa.pub" in res.stdout

    assert os.path.exists(RESULTS_PATH)

    with open(RESULTS_PATH) as f:
        data = f.read()

    assert "999.999.999.999" in data
    assert "999.000.000.999" in data

    assert "df -h" in data
    assert "False" in data
    assert "/root/.ssh/id_rsa.pub" in data


def install_via_apt():

    if os.path.exists(RESULTS_PATH):
        os.remove(RESULTS_PATH)

    run("viper init -f")
    res = run(
        "viper @myproj:allhosts"
        " | viper @myproj:install_via_apt python 3.8.0 results.csv --max-workers 50"
    )

    assert res.returncode == 0
    assert "apt-get install -y python-3.8.0" in res.stdout

    assert os.path.exists(RESULTS_PATH)

    with open(RESULTS_PATH) as f:
        data = f.read()
    assert "apt-get install -y python-3.8.0" in data


def test_final():

    if os.path.exists(RESULTS_PATH):
        os.remove(RESULTS_PATH)

    run("viper init -f")
    res = run(
        "viper @myproj:allhosts"
        " | viper hosts:where ip IS 999.999.999.999"
        ' | viper @myproj:remote_exec "df -h" results.csv --max-workers 50'
    )

    assert res.returncode == 0
    assert "999.999.999.999" in res.stdout
    assert "999.000.000.999" not in res.stdout

    with open(RESULTS_PATH) as f:
        data = f.read()

    assert "df -h" in data
    assert "False" in data
    assert "/root/.ssh/id_rsa.pub" in data
    assert "999.999.999.999" in data
    assert "999.000.000.999" not in data


def test_app_version():

    if os.path.exists(RESULTS_PATH):
        os.remove(RESULTS_PATH)

    run("viper init -f")
    res = run(
        "viper @myproj:allhosts"
        " | viper @myproj:app_version python results.csv --max-workers 50"
    )

    assert res.returncode == 0
    assert "python --version" in res.stdout

    assert os.path.exists(RESULTS_PATH)

    with open(RESULTS_PATH) as f:
        data = f.read()
    assert "python --version" in data


def test_install_via_apt():

    if os.path.exists(RESULTS_PATH):
        os.remove(RESULTS_PATH)

    run("viper init -f")
    res = run(
        "viper @myproj:allhosts"
        " | viper @myproj:install_via_apt python 3.8.0 results.csv --max-workers 50"
    )

    assert res.returncode == 0
    assert "[]" in res.stdout  # because the first command failed

    assert os.path.exists(RESULTS_PATH)

    with open(RESULTS_PATH) as f:
        data = f.read()
    assert "returncode" in data  # only the table headers will be there


def test_get_triggers():

    run("viper init -f")

    res = run("viper @myproj:get_triggers")
    assert res.returncode == 0
    assert res.stdout.strip() == ""

    run(
        "viper @myproj:allhosts"
        " | viper @myproj:app_version python results.csv --max-workers 50"
    )

    run(
        "viper @myproj:allhosts"
        " | viper @myproj:app_version python results.csv --max-workers 50"
    )

    res = run("viper @myproj:get_triggers --debug")
    assert res.returncode == 0
    assert len(res.stdout.strip().split()) == 2
