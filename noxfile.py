from pathlib import Path
from glob import glob
from nox import session, sessions

PATH_SRC = Path(__file__).resolve().parent / 'MetAromatic'
PATH_REQS = Path(__file__).resolve().parent / 'requirements.txt'
PATH_WHL = Path(__file__).resolve().parent / 'dist' / '*.whl'
PATH_TESTS = Path(__file__).resolve().parent / 'tests'

@session(python='3.9')
def tests(session: sessions.Session) -> None:

    # Get requirements.txt
    session.install('pipreqs')
    command = f'pipreqs --force --savepath={PATH_REQS} {PATH_SRC}'
    session.run(*command.split())

    # Install all non-MetAromatic dependencies
    session.install('--requirement', PATH_REQS)

    # Install MetAromatic into venv
    session.install('wheel')
    command = 'python3 setup.py clean --all bdist_wheel'
    session.run(*command.split())

    whl = glob(str(PATH_WHL))

    if len(whl) > 1:
        raise Exception('More than one wheel file exists. Cannot proceed')

    session.install(whl[0], '--force-reinstall')

    # Install pytest and runs tests
    session.install('pytest')
    command = f'pytest -vs {PATH_TESTS}'
    session.run(*command.split())
