####################################
#                                  #
#  MET-AROMATIC OFFICIAL MAKEFILE  #
#                                  #
####################################

.PHONY = help check-pipreqs requirements install uninstall test full lint dockertest

.DEFAULT_GOAL = help

LIGHT_PURPLE_UNDERBAR = "\033[4;1;35m"
LIGHT_PURPLE = "\033[1;1;35m"
NO_COLOR = "\033[0m"

define RENDER_TITLE
	@echo -e $(LIGHT_PURPLE_UNDERBAR)$(1)$(NO_COLOR)
endef

define RENDER_PREAMBLE
	@echo -e $(LIGHT_PURPLE)\> $(1)$(NO_COLOR)
endef

define HELP_LIST_TARGETS

To display all targets:
    $$ make help
To check whether pipreqs is installed
    $$ make check-pipreqs
To generate a requirements.txt file:
    $$ make requirements
    > Trajectory: check-pipreqs -> requirements
To setup all project dependencies:
    $$ make install
    > Trajectory: requirements -> install
To uninstall all project dependencies:
    $$ make uninstall
    > Trajectory: requirements -> uninstall
To test the project:
    $$ make test
To perform an end-to-end test:
    $$ make full
    > Trajectory: install -> test -> full
To lint the project:
    $$ make lint
To run tests with Docker
    $$ make dockertest

endef

export HELP_LIST_TARGETS

PYTHON_INTERP = /usr/bin/python3
ROOT_DIRECTORY := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
PROJECT_DIRECTORY = $(ROOT_DIRECTORY)/MetAromatic
REQUIREMENTS_TXT = $(ROOT_DIRECTORY)/requirements.txt
DOCKER_IMAGE_NAME = ma

help:
	$(call RENDER_TITLE,MET-AROMATIC OFFICIAL MAKEFILE)
	@echo "$$HELP_LIST_TARGETS"

check-pipreqs:
	$(call RENDER_PREAMBLE,Checking if pipreqs is installed)
	@$(PYTHON_INTERP) -m pip list | grep --word-regexp pipreqs || \
	(echo "Library 'pipreqs' is not installed. Installing pipreqs" && \
	$(PYTHON_INTERP) -m pip install --user pipreqs)

requirements: check-pipreqs
	$(call RENDER_PREAMBLE,Generating requirements.txt file)
	@$(PYTHON_INTERP) -m pipreqs.pipreqs --force \
	--savepath $(REQUIREMENTS_TXT) \
	--ignore $(PROJECT_DIRECTORY)/utils/test_data/ \
	$(PROJECT_DIRECTORY)

install: requirements
	$(call RENDER_PREAMBLE,Installing all project dependencies)
	@$(PYTHON_INTERP) -m pip install --user --requirement $(REQUIREMENTS_TXT)
	$(call RENDER_PREAMBLE,Making runner executable)
	chmod +x $(PROJECT_DIRECTORY)/runner.py

uninstall: requirements
	$(call RENDER_PREAMBLE,Uninstalling all project dependencies)
	@$(PYTHON_INTERP) -m pip uninstall --yes --requirement $(REQUIREMENTS_TXT)

test:
	$(call RENDER_PREAMBLE,Running pytest over project)
	@$(PYTHON_INTERP) -m pytest -vs $(PROJECT_DIRECTORY)

full: install test

lint:
	$(call RENDER_PREAMBLE,Linting the project using pylint static analysis tool)
	@$(PYTHON_INTERP) -m pylint $(PROJECT_DIRECTORY) \
	--output-format=colorized \
	--exit-zero \
	--msg-template "{msg_id}{line:4d}{column:3d} {obj} {msg}"

dockertest:
	$(call RENDER_PREAMBLE,Building docker image $(DOCKER_IMAGE_NAME))
	@docker build --tag $(DOCKER_IMAGE_NAME) $(ROOT_DIRECTORY)/
