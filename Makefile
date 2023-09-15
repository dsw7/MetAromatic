.PHONY = help wheel setup test clean test-pypi pypi black mypy
.DEFAULT_GOAL = help

define HELP_LIST_TARGETS

    To build wheel:
        $$ make wheel
    To set up the project:
        $$ make setup
    To test the project:
        $$ make test
    To remove build, dist and other setuo.py directories:
        $$ make clean
    To upload package to TestPyPI:
        $$ make test-pypi
    To upload package to PyPI:
        $$ make pypi
	To run black over Python code:
        $$ make black
	To run mypy over Python code:
        $$ make mypy

endef

export HELP_LIST_TARGETS

help:
	@echo "$$HELP_LIST_TARGETS"

wheel:
	@pip3 install --upgrade build
	@python3 -m build

setup: wheel
	@pip3 install dist/*whl --force-reinstall

test:
	@pip3 install nox
	@nox --envdir=/tmp

clean:
	@rm -rfv dist/ *.egg-info/

test-pypi: wheel
	@pip3 install --upgrade twine
	@python3 -m twine upload --repository testpypi dist/*

pypi: wheel
	@pip3 install --upgrade twine
	@python3 -m twine upload dist/*

black:
	@black MetAromatic tests

mypy:
	@mypy --cache-dir=/tmp/mypy_cache_metaromatic MetAromatic tests
