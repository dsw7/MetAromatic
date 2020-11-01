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
    'pylint==2.4.2'
]

nox.options.report = path.join(gettempdir(), 'noxreport')
nox.options.envdir = path.join(gettempdir(), '.nox')

@nox.session(python=PYTHON_INTERP_VERSION)
def lint(session):
    session.install(*ALL_PROJECT_DEPENDENCIES)
    session.run('pylint', PATH_TO_PROJECT, '--output-format=colorized')

@nox.session(python=PYTHON_INTERP_VERSION)
def tests(session):
    session.install(*ALL_PROJECT_DEPENDENCIES)
    session.run('pytest', '-vs', PATH_TO_PROJECT)
