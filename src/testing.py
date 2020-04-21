import sys
from pytest import main as pytest_main


class TestRunner:
    def __init__(self, root, capture=True,
                 verbose=True, exit_on_failure=False, expression=None):
        self.root = root
        self.cmd = [root]

        if capture:
            self.cmd.append('-s')
        if verbose:
            self.cmd.append('-v')
        if exit_on_failure:
            self.cmd.append('-x')
        if expression:
            self.cmd.append(f'-k{expression}')

    def run_tests(self):
        sys.exit(pytest_main(self.cmd))

    def run_tests_with_coverage(self):
        self.cmd.append(f'--cov={self.root}')
        self.cmd.append(fr'--cov-report=html:{self.root}\htmlcov')
        self.cmd.append(fr'--cov-config={self.root}\.coveragerc')
        sys.exit(pytest_main(self.cmd))
