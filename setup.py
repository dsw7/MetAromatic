from setuptools import (
    setup,
    find_packages
)
#from os import path
#
#def get_path_to_commands() -> str:
#    return path.join(path.dirname(__file__),

setup(
    name = 'metaromatic',
    version='1.0',
    packages=find_packages('MetAromatic')
)
