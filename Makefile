.PHONY = help wheel setup test dockertest clean test-pypi pypi
.DEFAULT_GOAL = help

define HELP_LIST_TARGETS

    To build wheel:
        $$ make wheel
    To set up the project:
        $$ make setup
    To test the project:
        $$ make test
    To run tests with Docker
        $$ make dockertest
    To remove build, dist and other setuo.py directories:
        $$ make clean
    To upload package to TestPyPI:
        $$ make test-pypi
    To upload package to PyPI:
        $$ make pypi

endef

export HELP_LIST_TARGETS

ROOT_DIRECTORY := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
DOCKER_TAG = ma

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

dockertest:
	@docker build --tag $(DOCKER_TAG) $(ROOT_DIRECTORY)/
	@docker run --interactive --tty --rm $(DOCKER_TAG)

clean:
	@rm -rfv dist/ *.egg-info/

test-pypi: wheel
	@pip3 install --upgrade twine
	@python3 -m twine upload --repository testpypi dist/*

pypi: wheel
	@pip3 install --upgrade twine
	@python3 -m twine upload dist/*
