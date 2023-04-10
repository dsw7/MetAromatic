####################################
#                                  #
#  MET-AROMATIC OFFICIAL MAKEFILE  #
#                                  #
####################################

.PHONY = help \
         requirements setup teardown test full \
		 wheel install clean uninstall test-wheel full-wheel \
		 dockertest

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

Command line program:
To generate a requirements.txt file:
    $$ make requirements
To setup all project dependencies:
    $$ make setup
To uninstall all project dependencies:
    $$ make teardown
To test the project:
    $$ make test
To perform an end-to-end test:
    $$ make full

Wheel installation:
To generate Python wheel file for pip installs:
    $$ make wheel
To install into site-packages from wheel:
    $$ make install
To remove build, dist and other setuo.py directories:
    $$ make clean
To uninstall site-packages distribution:
    $$ make uninstall
To run a packaging test
    $$ make test-wheel
To run an end-to-end packaging test
    $$ make full-wheel

Other:
To display all targets:
    $$ make help
To run tests with Docker
    $$ make dockertest

endef

export HELP_LIST_TARGETS

PYTHON_INTERP = /usr/bin/env python3
PROJECT_NAME = MetAromatic
ROOT_DIRECTORY := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
PROJECT_DIRECTORY = $(ROOT_DIRECTORY)/MetAromatic
REQUIREMENTS_TXT = $(ROOT_DIRECTORY)/requirements.txt
DOCKER_TAG = ma

# ----------------------------------
# Simple install for running program via CLI
# ----------------------------------

requirements:
	$(call RENDER_PREAMBLE,Checking if pipreqs is installed)
	@$(PYTHON_INTERP) -m pip list | grep --word-regexp pipreqs || \
	(echo "Library 'pipreqs' is not installed. Installing pipreqs" && \
	$(PYTHON_INTERP) -m pip install --user pipreqs)

	$(call RENDER_PREAMBLE,Generating requirements.txt file)
	@$(PYTHON_INTERP) -m pipreqs.pipreqs --force \
	--savepath $(REQUIREMENTS_TXT) \
	--ignore $(PROJECT_DIRECTORY)/utils/test_data/ \
	$(PROJECT_DIRECTORY)

setup: requirements
	$(call RENDER_PREAMBLE,Installing all project dependencies)
	@$(PYTHON_INTERP) -m pip install --user --requirement $(REQUIREMENTS_TXT)
	$(call RENDER_PREAMBLE,Making runner executable)
	chmod +x $(PROJECT_DIRECTORY)/runner.py

teardown: requirements
	$(call RENDER_PREAMBLE,Uninstalling all project dependencies)
	@$(PYTHON_INTERP) -m pip uninstall --yes --requirement $(REQUIREMENTS_TXT)

test:
	$(call RENDER_PREAMBLE,Running pytest over project)
	@$(PYTHON_INTERP) -m pytest -vs -m 'test_command_line_interface' $(PROJECT_DIRECTORY)

full: setup test

# ----------------------------------
# Wheel install for importing Met-aromatic scripts
# ----------------------------------

wheel:
	$(call RENDER_PREAMBLE,Generating *.whl file for project)
	@$(PYTHON_INTERP) $(ROOT_DIRECTORY)/setup.py clean --all bdist_wheel

install: wheel
	$(call RENDER_PREAMBLE,Project will be installed under:)
	@$(PYTHON_INTERP) -m site --user-site
	$(call RENDER_PREAMBLE,Installing project...)
	@$(PYTHON_INTERP) -m pip install --user --force-reinstall dist/*whl
	$(call RENDER_PREAMBLE,List tree...)
	@tree --dirsfirst -I *pyc\|__pycache__ $(shell $(PYTHON_INTERP) -m site --user-site)/$(PROJECT_NAME)

clean:
	$(call RENDER_PREAMBLE,Removing scrap)
	@rm -rfv build/ dist/ *.egg-info/

uninstall:
	$(call RENDER_PREAMBLE,Uninstalling project)
	@$(PYTHON_INTERP) -m pip uninstall -y $(PROJECT_NAME)

test-wheel:
	$(call RENDER_PREAMBLE,Testing wheel installation)
	@cd MetAromatic/; $(PYTHON_INTERP) -m pytest -vs -m 'test_packaging' $(PROJECT_DIRECTORY); cd ..

full-wheel: install test-wheel clean uninstall

# ----------------------------------
# Other helpers
# ----------------------------------

help:
	$(call RENDER_TITLE,* MET-AROMATIC OFFICIAL MAKEFILE *)
	@echo "$$HELP_LIST_TARGETS"

dockertest:
	$(call RENDER_PREAMBLE,Building docker image $(DOCKER_TAG))
	@docker build --tag $(DOCKER_TAG) $(ROOT_DIRECTORY)/
	$(call RENDER_PREAMBLE,Running tests in docker container)
	@docker run --interactive --tty --rm $(DOCKER_TAG)
