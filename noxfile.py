from os import path
from tempfile import gettempdir
import nox

PATH_TO_PROJECT = path.dirname(__file__)
PYTHON_INTERP_VERSION = '3.6.10'
ALL_PROJECT_DEPENDENCIES = [
    'pytest==5.2.1',
    'networkx==2.3',
    'numpy==1.19.0',
    'pymongo==3.9.0',
    'click==7.1.2',
    'pylint==2.4.2',
    'nox==2020.8.22'
]

nox.options.report = path.join(gettempdir(), 'noxreport')
nox.options.envdir = path.join(gettempdir(), '.nox')

@nox.session(python=PYTHON_INTERP_VERSION)
def lint(session):
    command = f'pylint {PATH_TO_PROJECT} --output-format=colorized --exit-zero'
    msg_template = ['--msg-template', '{msg_id}{line:4d}{column:3d} {obj} {msg}']
    session.install(*ALL_PROJECT_DEPENDENCIES)
    session.run(*command.split(), *msg_template)

@nox.session(python=PYTHON_INTERP_VERSION)
def tests(session):
    command = f'pytest -vs {PATH_TO_PROJECT}'
    session.install(*ALL_PROJECT_DEPENDENCIES)
    session.run(*command.split())
