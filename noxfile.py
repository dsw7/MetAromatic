from os import path
from tempfile import gettempdir
import nox

DEPENDENCIES_TESTS = [
    'pytest==5.2.1',
    'networkx==2.3',
    'numpy==1.19.0',
    'pymongo==3.9.0',
    'click==7.1.2'
]
DEPENDENCIES_PYLINT = [
    'pylint==2.4.2'
]
PYTHON_INTERP_VERSION = '3.6.10'

nox.options.envdir = path.join(gettempdir(), '.nox')

@nox.session(python=PYTHON_INTERP_VERSION)
def lint(session):
    session.install(*DEPENDENCIES_PYLINT)
    session.run('pylint', '*py')

@nox.session(python=PYTHON_INTERP_VERSION)
def tests(session):
    session.install(*DEPENDENCIES_TESTS)
    session.run('pytest', '-vs')
