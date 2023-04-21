from os import EX_OK
from subprocess import call, DEVNULL, STDOUT

def test_runner_pair() -> None:
    assert call('runner pair 1rcy'.split(), stdout=DEVNULL, stderr=STDOUT) == EX_OK

def test_runner_bridge() -> None:
    assert call('runner bridge 6lu7'.split(), stdout=DEVNULL, stderr=STDOUT) == EX_OK
