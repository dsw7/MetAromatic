.PHONY = help setup test dockertest clean

.DEFAULT_GOAL = help

LIGHT_PURPLE = "\033[1;1;35m"
NO_COLOR = "\033[0m"

define RENDER_PREAMBLE
	@echo -e $(LIGHT_PURPLE)\> $(1)$(NO_COLOR)
endef

define HELP_LIST_TARGETS

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
PROJECT_DIRECTORY = $(ROOT_DIRECTORY)/MetAromatic
DOCKER_TAG = ma

help:
	$(call RENDER_PREAMBLE,MET-AROMATIC OFFICIAL MAKEFILE)
	@echo "$$HELP_LIST_TARGETS"

setup:
	$(call RENDER_PREAMBLE,Setting up project)
	@pip3 install pipreqs
	@pipreqs --force --savepath=requirements.txt $(PROJECT_DIRECTORY)
	@pip3 install --requirement requirements.txt
	@pip3 install wheel
	@python3 setup.py clean --all bdist_wheel
	@pip3 install dist/*whl --force-reinstall

test:
	$(call RENDER_PREAMBLE,Running nox tests)
	@pip3 install nox
	@nox --envdir=/tmp

dockertest:
	$(call RENDER_PREAMBLE,Building docker image $(DOCKER_TAG))
	@docker build --tag $(DOCKER_TAG) $(ROOT_DIRECTORY)/
	$(call RENDER_PREAMBLE,Running tests in docker container)
	@docker run --interactive --tty --rm $(DOCKER_TAG)

clean:
	$(call RENDER_PREAMBLE,Removing build artifacts)
	@rm -rfv build/ dist/ *.egg-info/
