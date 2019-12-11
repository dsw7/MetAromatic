import setuptools
from os import remove

from metaromatic.versionhandler import VersionHandler
version = VersionHandler('.').get_version().get('__version__')
remove('version.py')

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="MetAromatic",
    version=version,
    author="David Weber",
    author_email="dsw7@sfu.ca",
    description="The MetAromatic Algorithm",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dsw7/MetAromaticEngine",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
