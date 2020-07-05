import sys
from pytest import main as pytest_main

class RunTests:
    def __init__(self, command_line_arguments, root):
        self.root = root
        self.cmd = [root]
        self.cmd.append('-s')

        if not command_line_arguments.quiet:
            self.cmd.append('-v')
        if command_line_arguments.exit_on_failure:
            self.cmd.append('-x')
        if command_line_arguments.test_expression:
            self.cmd.append(f'-k{command_line_arguments.test_expression}')

    def run_tests(self):
        sys.exit(pytest_main(self.cmd))

    def run_tests_with_coverage(self):
        self.cmd.append(f'--cov={self.root}')
        self.cmd.append(fr'--cov-report=html:{self.root}\htmlcov')
        self.cmd.append(fr'--cov-config={self.root}\.coveragerc')
        sys.exit(pytest_main(self.cmd))
