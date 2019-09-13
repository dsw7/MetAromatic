"""
dsw7@sfu.ca

This file does the following:
    [1] Creates --onefile binary for MetAromatic in a folder: /dist
    [2] Moves an .ico to /dist
    [3] Creates a build log: /build (can be scrapped)
    [4] Creates a .spec file
"""

from subprocess import call
from os import path, remove
from shutil import copyfile

dump = path.join(path.expanduser('~'), 'Desktop')
loc_dist = path.join(dump, 'dist')
loc_build = path.join(dump, 'build')
icon_src = 'icon.ico'
icon_dst = path.join(loc_dist, icon_src)


def bundle():
    """ Runs the pyinstaller command """
    cmd = r"""
    pyinstaller 
    MetAromatic.py 
    --onefile 
    --name MetAromatic 
    --distpath {} 
    --workpath {}
    --clean --hidden-import tkinter 
    --icon {}""".format(loc_dist, loc_build, icon_src)
    call(cmd.split())
    copyfile(icon_src, icon_dst)
    

def remove_spec_file():
    """ We don't need the spec file as we have the dispatcher """
    remove('./MetAromatic.spec')
    

if __name__ == '__main__':
    bundle()
    remove_spec_file()
