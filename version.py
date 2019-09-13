"""
dsw7@sfu.ca

In this namespace I house the machinery for handling versioninfo / git commit
count.

How it works:
    If we are in a directory under .git control:
        1. Generate a VERSIONINFO.py file
        2. Get the commit count from GitPython
    Otherwise:
        1. Get commit count by importing VERSIONINFO.py file
"""


from git import Repo, exc
from uuid import uuid4
VERSIONFILE = 'VERSIONINFO.py'


def get_commit_count(git_repo_loc):
    """ Get commit count using GitPython """
    repo = Repo(git_repo_loc)
    return repo.git.rev_list('--count', 'HEAD')
    

def generate_version_info(git_repo_loc, versioninfo_filename):
    """ Create a version information file in current directory """
    version = 'version = {}\n'.format(get_commit_count(git_repo_loc=git_repo_loc))
    UUID = "UUID = '{}'\n".format(uuid4().hex)
    with open(versioninfo_filename, 'w+') as f:
        f.write(version)
        f.write(UUID)  # add UUID for making sure files are updated on run


def version_handler(repo_path, versioninfo_filename=VERSIONFILE):
    """ Performs procedure described in script docstring """
    try:
        Repo(".", search_parent_directories=True)
        generate_version_info(repo_path, versioninfo_filename)
    except exc.InvalidGitRepositoryError:
        from VERSIONINFO import version
        return version
    else:
        return get_commit_count(repo_path)
        

