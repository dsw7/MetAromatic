"""
dsw7@sfu.ca

In this namespace I house a small function for getting commit count
from git.
"""

from subprocess import Popen, PIPE

def get_commit_count():
    # disable this when generating binaries
    cmd = ['git', 'rev-list', '--all', '--count']
    stdout = Popen(cmd, stdout=PIPE).communicate()
    return stdout[0].decode().strip('\n')