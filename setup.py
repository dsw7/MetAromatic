from setuptools import (
    setup,
    find_packages
)

setup(
    name = 'MetAromatic',
    version='1.0',
    packages=find_packages('commands'),
    install_requires=[
        'pymongo',
        'networkx',
        'numpy',
        'pytest'
    ]
)
