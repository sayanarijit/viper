from viper import Host
from viper import Result
from viper import Results
from viper import Runner
from viper import Runners
from viper import Task


def make_echo_command(host, what):
    return ("echo", what)


def test_results_runners():

    task = Task("print IP address", command_factory=make_echo_command)
    host = Host("1.1.1.1")

    results = Results.from_items(
        Result(
            trigger_time=1.0,
            task=task,
            host=host,
            args=("bar",),
            command=("foo",),
            stdout="out",
            stderr="err",
            returncode=0,
            start=1.1,
            end=1.2,
            retry=0,
        )
    )

    runners = results.runners()

    assert runners == Runners.from_items(Runner(task=task, host=host, args=("bar",)))


def test_results_re_run():

    task = Task("print IP address", command_factory=make_echo_command)
    host = Host("1.1.1.1")

    results = Results.from_items(
        Result(
            trigger_time=1.0,
            task=task,
            host=host,
            args=("bar",),
            command=("foo",),
            stdout="out",
            stderr="err",
            returncode=0,
            start=1.1,
            end=1.2,
            retry=0,
        )
    )

    re_results = results.re_run()

    assert results.all()[0].task == re_results.all()[0].task
    assert results.all()[0].host == re_results.all()[0].host
    assert results.all()[0].args == re_results.all()[0].args
    assert results.all()[0].trigger_time != re_results.all()[0].trigger_time
    assert results.all()[0].start != re_results.all()[0].start
    assert results.all()[0].end != re_results.all()[0].end


def test_results_final():

    task = Task("print IP address", command_factory=make_echo_command)
    host = Host("1.1.1.1")

    result_list = [
        Result(
            trigger_time=1.0,
            task=task,
            host=host,
            args=("bar",),
            command=("foo",),
            stdout="out",
            stderr="err",
            returncode=0,
            start=1.1,
            end=1.2,
            retry=0,
        ),
        Result(
            trigger_time=1.0,
            task=task,
            host=host,
            args=("bar",),
            command=("foo",),
            stdout="out",
            stderr="err",
            returncode=0,
            start=2.1,
            end=2.2,
            retry=1,
        ),
        Result(
            trigger_time=2.0,
            task=task,
            host=host,
            args=("bar",),
            command=("foo",),
            stdout="out",
            stderr="err",
            returncode=0,
            start=3.1,
            end=3.2,
            retry=0,
        ),
    ]

    final = Results.from_items(*result_list).final().sort()
    assert final == Results.from_items(result_list[1], result_list[2]).sort()
