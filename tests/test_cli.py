import subprocess


def test_all_cli_examples():
    from viper.demo import __doc__ as examples_doc

    command = " && \\\n\n".join(
        [
            line.strip()
            for line in examples_doc.splitlines()
            if line.startswith("   ") and not line.strip().startswith("#")
        ]
    )

    print(command)

    assert subprocess.run(command, shell=True).returncode == 0
