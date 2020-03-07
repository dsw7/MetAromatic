import sys
from pytest import main as pytest_main


def run_tests(root):
    sys.exit(pytest_main(f'{root} -vs'.split()))


def run_tests_with_coverage(root):
    sys.exit(pytest_main([
        fr'{root}',
        '-vs',
        f'--cov={root}',
        fr'--cov-report=html:{root}\htmlcov',
        fr'--cov-config={root}\.coveragerc'
    ]))
