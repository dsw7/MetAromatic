from os import path
from tempfile import gettempdir
import nox

PATH_TO_PROJECT = path.dirname(__file__)
PATH_REQUIREMENTS = path.join(PATH_TO_PROJECT, 'requirements.txt')
PYTHON_INTERP_VERSION = '3.8.7'

nox.options.envdir = path.join(gettempdir(), '.nox_met_aromatic')
nox.options.report = path.join(nox.options.envdir, 'nox_report_met_aromatic')

@nox.session(python=PYTHON_INTERP_VERSION)
def lint(session):
    command = f'pylint {PATH_TO_PROJECT} --output-format=colorized --exit-zero'
    msg_template = ['--msg-template', '{msg_id}{line:4d}{column:3d} {obj} {msg}']
    session.install('-r', PATH_REQUIREMENTS)
    session.run(*command.split(), *msg_template)

@nox.session(python=PYTHON_INTERP_VERSION)
def run_pytests_with_coverage(session):
    command = 'pytest -vs {} '.format(PATH_TO_PROJECT)
    command += '--cov={} '.format(PATH_TO_PROJECT)
    command += '--cov-report=html:{} '.format(path.join(nox.options.envdir, 'htmlcov'))
    command += '--cov-config={} '.format(path.join(PATH_TO_PROJECT, '.coveragerc'))
    session.install('-r', PATH_REQUIREMENTS)
    session.run(*command.split())
