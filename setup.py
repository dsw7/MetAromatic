from setuptools import setup, find_packages

setup(
    name = 'MetAromatic',
    version='1.0',
    packages=find_packages(),
    install_requires=[
        'click',
        'networkx',
        'numpy',
        'pymongo',
    ],
    entry_points={
        'console_scripts': ['runner = MetAromatic.runner:cli']
    }
)
