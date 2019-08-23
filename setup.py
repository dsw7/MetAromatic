# Written by David Weber
# dsw7@sfu.ca

"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

"""
from setuptools import setup
import sys

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)

# this block throws Errno 63
"""

# fix for errno 63
import py2app
import sys
from distutils.core import setup
from os             import getcwd
from pathlib        import Path

APP = ['MetAromatic.py']
DATA_FILES = []
OPTIONS = {}

sys.argv.append('py2app')
setup(app=APP,
      options=dict(py2app=dict(bdist_base=str(Path(getcwd()).parent)
      + '/build', dist_dir=str(Path(getcwd()).parent) + '/dist')),
      data_files=DATA_FILES,
      setup_requires=['py2app'])
