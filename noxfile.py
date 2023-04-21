import sys
from pathlib import Path
from glob import glob
from nox import session, sessions

REQUIREMENTS_TXT = Path(__file__).resolve().parent / 'requirements.txt'
PATH_WHL = Path(__file__).resolve().parent / 'dist' / '*.whl'
PATH_TESTS = Path(__file__).resolve().parent / 'tests'

@session(python='3.9')
def tests(session: sessions.Session) -> None:

    session.install('--requirement', REQUIREMENTS_TXT)
    whl = glob(str(PATH_WHL))

    if len(whl) > 1:
        sys.exit('More than one wheel file exists. Cannot proceed')

    session.install(whl[0], '--force-reinstall')
    session.install('pytest')

    command = f'pytest -vsx {PATH_TESTS}'
    session.run(*command.split())
