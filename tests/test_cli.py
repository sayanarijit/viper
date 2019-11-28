from subprocess import Popen, PIPE
from collections import namedtuple
from viper.hosts import Hosts
import json


def run(command):
    p = Popen(command, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate(timeout=5)
    stdout, stderr = out.decode("latin1"), err.decode("latin1")
    return namedtuple("Result", "stdout stderr returncode")(
        stdout, stderr, p.returncode
    )


