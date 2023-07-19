from pathlib import Path
from glob import glob
from nox import session, sessions

PATH_WHL = Path(__file__).resolve().parent / 'dist' / '*.whl'
PATH_TESTS = Path(__file__).resolve().parent / 'tests'

@session(python='3.9')
def met_aromatic_tests(session: sessions.Session) -> None:

    session.install('wheel')
    command = 'python3 setup.py clean --all bdist_wheel'
    session.run(*command.split())

    whl = glob(str(PATH_WHL))

    if len(whl) > 1:
        raise Exception('More than one wheel file exists. Cannot proceed')

    session.install(whl[0], '--force-reinstall')

    session.install('pytest', 'typing_extensions')
    command = f'pytest -vs {PATH_TESTS}'
    session.run(*command.split())
