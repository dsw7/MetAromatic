from setuptools import setup

setup(
    name = 'MetAromatic',
    version='1.0',
    packages=[
        'MetAromatic',
    ],
    entry_points={
        'console_scripts': ['runner = MetAromatic.runner:cli']
    }
)
