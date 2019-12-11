"""
dsw7@sfu.ca

A version handling script.
"""

from uuid import uuid4
from datetime import datetime
from git import Repo, exc
VERSIONFILE = 'version.py'


class VersionHandler:
    """
    How it works:
    ==============
        Step 1:
        -------
        $ git init
        $ git add *
        $ git commit -m "First commit"

        Step 2:
        -------
        Run program once. Version, UUID, sha, and commit message will be returned both
        into program and logged into a python version file.
        {'__version__': '19.1', 'UUID': 'edddd', 'sha': 'f8c2d', 'message': 'First commit'}

        Step 3:
        -------
        $ git add *
        $ git commit -m "Second commit"

        Step 4:
        -------
        Run program once. Version, UUID, sha, and commit message will be returned both
        into program and logged into a NEW python version file.
        {'__version__': '19.2', 'UUID': '8c9bb', 'sha': '17f06', 'message': 'Second commit'}

        Step 5:
        -------
        $ git add *
        $ git commit -m "Third commit"

        Step 6:
        -------
        Run program once. Version, UUID, sha, and commit message will be returned both
        into program and logged into a NEW python version file.
        {'__version__': '19.3', 'UUID': '3c7c8', 'sha': '9287d', 'message': 'Third commit'}

        Step 7:
        -------
        $ rm -rf .git

        Step 8:
        -------
        We are no longer in a .git repository. Therefore the code will default to reading
        the version python file previously generated when we were still in a .git repo.

        {'__version__': '19.3', 'UUID': '3c7c8', 'sha': '9287d', 'message': 'Third commit'}
        {'__version__': '19.3', 'UUID': '3c7c8', 'sha': '9287d', 'message': 'Third commit'}
        {'__version__': '19.3', 'UUID': '3c7c8', 'sha': '9287d', 'message': 'Third commit'}


    Parameters:
    ==============
        path    -> The path in which .git directory resides


    Returns:
    ==============
        version -> A string of form:
            X.Y
            -- Where X is the last two digits of the current year
            -- Where Y is the commit count (frozen or dynamic)
        UUID    -> Optional. Used for ensuring that version.py log is updated
                   every commit
        sha     -> The most recent commit SHA checksum

        Writes to VERSIONFILE python file which must be imported into main
        script in a dispatchable project

    Example:
    ==============
        >>> from versionhandler import VersionHandler
        >>> version = VersionHandler('/path/to/.git').get_version()
        >>> print(version)
    """

    def __init__(self, path):
        self.path = path
        self.major = str(datetime.now().year)[-2:]
        try:
            self.repo = Repo(path)
        except exc.InvalidGitRepositoryError:
            self.repo = False

    @staticmethod
    def export_file(ver, uid, sha, msg):
        """ Create an importable version file """
        literal = (
            "version = {{"
            "'__version__': '{}', "
            "'UUID': '{}', "
            "'sha': '{}', "
            "'message': '{}'"
            "}}\n"
        )
        with open(VERSIONFILE, 'w+') as file:
            file.write(literal.format(ver, uid, sha, msg))

    def handle_true_case(self):
        """ Handle case where we are inside a .git repository """
        commit_count = self.repo.git.rev_list('--count', 'HEAD')
        version = '{}.{}'.format(self.major, commit_count)
        uuid_ = uuid4().hex
        sha = self.repo.head.object.hexsha
        message = self.repo.head.commit.message.strip('\n')
        self.export_file(ver=version, uid=uuid_, sha=sha, msg=message)
        return {
            '__version__': version,
            'UUID': uuid_,
            'sha': sha,
            'message': message
        }

    @staticmethod
    def handle_false_case():
        """ Handle case where we are not inside a .git repository """
        try:
            from version import version
        except ImportError:
            raise ValueError('Missing version file: {}'.format(VERSIONFILE))
        else:
            # return version.get('__version__'), version.get('UUID'), version.get('sha')
            return version

    def get_version(self):
        """ End user should call this method """
        if not self.repo:
            return self.handle_false_case()
        else:
            return self.handle_true_case()
