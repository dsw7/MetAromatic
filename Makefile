####################################
#                                  #
#  MET-AROMATIC OFFICIAL MAKEFILE  #
#                                  #
####################################

.PHONY = help test test-wheel dockertest clean

.DEFAULT_GOAL = help

LIGHT_PURPLE = "\033[1;1;35m"
NO_COLOR = "\033[0m"

define RENDER_PREAMBLE
	@echo -e $(LIGHT_PURPLE)\> $(1)$(NO_COLOR)
endef

define HELP_LIST_TARGETS

    To test the project:
        $$ make test
    To run a packaging test
        $$ make test-wheel
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

test:
	$(call RENDER_PREAMBLE,Running pytest over project)
	@python3 -m pytest -vs -m 'test_command_line_interface' $(PROJECT_DIRECTORY)

test-wheel:
	$(call RENDER_PREAMBLE,Testing wheel installation)
	@cd MetAromatic/; python3 -m pytest -vs -m 'test_packaging' $(PROJECT_DIRECTORY); cd ..

dockertest:
	$(call RENDER_PREAMBLE,Building docker image $(DOCKER_TAG))
	@docker build --tag $(DOCKER_TAG) $(ROOT_DIRECTORY)/
	$(call RENDER_PREAMBLE,Running tests in docker container)
	@docker run --interactive --tty --rm $(DOCKER_TAG)

clean:
	$(call RENDER_PREAMBLE,Removing build artifacts)
	@rm -rfv build/ dist/ *.egg-info/
