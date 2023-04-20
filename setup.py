from setuptools import setup

setup(
    name = 'MetAromatic',
    version='1.0',
    packages=[
        'MetAromatic/core',
        'MetAromatic/core/helpers'
    ],
    entry_points={
        'console_scripts': ['ma = MetAromatic.runner:cli']
    }
)
