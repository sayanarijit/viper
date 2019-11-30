import subprocess
from viper.demo import __doc__ as examples_doc


def test_all_cli_examples():

    commands = [
        line.strip()
        for line in examples_doc.splitlines()
        if line.startswith("   ") and not line.strip().startswith("#")
    ]

    for command in commands:
        print(command)
        assert subprocess.run(command, shell=True).returncode == 0
