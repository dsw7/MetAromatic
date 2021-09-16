from setuptools import setup

setup(
    name = 'MetAromatic',
    version='1.0',
    packages=find_packages(),
    packages=[
        'MetAromatic/core',
        'MetAromatic/core/helpers'
    ],
    install_requires=[
        'pymongo',
        'networkx',
        'numpy',
        'pytest'
    ]
)
