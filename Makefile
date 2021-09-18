####################################
#                                  #
#  MET-AROMATIC OFFICIAL MAKEFILE  #
#                                  #
####################################

.PHONY = help requirements setup teardown test full wheel install clean uninstall lint dockertest

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
To generate Python wheel file for pip installs:
    $$ make wheel
To install into site-packages from wheel:
    $$ make install
To remove build, dist and other setuo.py directories:
    $$ make clean
To uninstall site-packages distribution:
    $$ make uninstall
To lint the project:
    $$ make lint
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

help:
	$(call RENDER_TITLE,* MET-AROMATIC OFFICIAL MAKEFILE *)
	@echo "$$HELP_LIST_TARGETS"

# -- Simple install - run via CLI --

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
	@$(PYTHON_INTERP) -m pytest -vs $(PROJECT_DIRECTORY)

full: setup test

# -- Wheel install - for importing Met-aromatic scripts --

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

# -- Other helpers --

lint:
	$(call RENDER_PREAMBLE,Linting the project using pylint static analysis tool)
	@$(PYTHON_INTERP) -m pylint $(PROJECT_DIRECTORY) \
	--output-format=colorized \
	--exit-zero \
	--rcfile=$(ROOT_DIRECTORY)/.pylintrc \
	--ignore=pdb_file_reading_module_v4_0.py \
	--msg-template "{msg_id}{line:4d}{column:3d} {obj} {msg}"

dockertest:
	$(call RENDER_PREAMBLE,Building docker image $(DOCKER_TAG))
	@docker build --tag $(DOCKER_TAG) $(ROOT_DIRECTORY)/
	$(call RENDER_PREAMBLE,Running tests in docker container)
	@docker run --interactive --tty --rm $(DOCKER_TAG)
