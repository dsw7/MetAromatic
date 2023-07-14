.PHONY = help tarball setup test dockertest clean
.DEFAULT_GOAL = help

define HELP_LIST_TARGETS

    To build tarball:
        $$ make tarball
    To set up the project:
        $$ make setup
    To test the project:
        $$ make test
    To run tests with Docker
        $$ make dockertest
    To remove build, dist and other setuo.py directories:
        $$ make clean

endef

export HELP_LIST_TARGETS

ROOT_DIRECTORY := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
DOCKER_TAG = ma

help:
	@echo "$$HELP_LIST_TARGETS"

tarball:
	@pip3 install wheel
	@python3 setup.py clean --all bdist_wheel

setup: tarball
	@pip3 install dist/*whl --force-reinstall

test:
	@pip3 install nox
	@nox --envdir=/tmp

dockertest:
	@docker build --tag $(DOCKER_TAG) $(ROOT_DIRECTORY)/
	@docker run --interactive --tty --rm $(DOCKER_TAG)

clean:
	@rm -rfv build/ dist/ *.egg-info/
