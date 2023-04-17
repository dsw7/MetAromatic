from pathlib import Path
from os import chdir, getcwd, EX_OK
from subprocess import call, DEVNULL, STDOUT
from contextlib import contextmanager
from pytest import mark


@mark.test_command_line_interface
class TestRunFromDifferentDirectories:

    def setup_class(self):

        self.root = Path(__file__).resolve().parent
        self.pwd = None

    @contextmanager
    def restore_dir(self):

        self.pwd = getcwd()

        try:
            yield
        finally:
            chdir(self.pwd)

    def test_aromatic_interaction_run_from_parent_directory(self):

        with self.restore_dir():
            chdir(self.root.parent)
            exit_code = call('MetAromatic/runner.py pair 1rcy'.split(), stdout=DEVNULL, stderr=STDOUT)

            assert exit_code == EX_OK

    def test_aromatic_interaction_run_from_child_directory(self):

        with self.restore_dir():
            chdir(self.root / 'core')
            exit_code = call('../runner.py pair 1rcy'.split(), stdout=DEVNULL, stderr=STDOUT)

            assert exit_code == EX_OK

    def test_bridging_interaction_run_from_parent_directory(self):

        with self.restore_dir():
            chdir(self.root.parent)
            exit_code = call('MetAromatic/runner.py bridge 6lu7'.split(), stdout=DEVNULL, stderr=STDOUT)

            assert exit_code == EX_OK

    def test_bridging_interaction_run_from_child_directory(self):

        with self.restore_dir():
            chdir(self.root / 'core')
            exit_code = call('../runner.py bridge 6lu7'.split(), stdout=DEVNULL, stderr=STDOUT)

            assert exit_code == EX_OK
