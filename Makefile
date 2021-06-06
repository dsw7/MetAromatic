####################################
#                                  #
#  MET-AROMATIC OFFICIAL MAKEFILE  #
#                                  #
####################################

.PHONY = help check-pipreqs requirements get-deps lint test test-coverage

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
    $$ make get-deps
    > Trajectory: requirements -> get-deps
To lint the project:
    $$ make lint
To test the project:
    $$ make test
To test the project with coverage:
    $$ make test-coverage
To perform an end-to-end test:
    $$ make full
    > Trajectory: get-deps -> test
endef

export HELP_LIST_TARGETS

PYTHON_INTERP = /usr/bin/python3
ROOT_DIRECTORY := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
PROJECT_DIRECTORY = $(ROOT_DIRECTORY)/MetAromatic
REQUIREMENTS_TXT = $(ROOT_DIRECTORY)/requirements.txt
DUMP_COVERAGE = /tmp/htmlcov

help:
	$(call RENDER_TITLE,MET-AROMATIC OFFICIAL MAKEFILE)
	@echo "$$HELP_LIST_TARGETS"

check-pipreqs:
	$(call RENDER_PREAMBLE,Checking if pipreqs is installed)
	@$(PYTHON_INTERP) -m pip list | grep --word-regexp pipreqs || \
	(echo "Library 'pipreqs' is not installed. Installing pipreqs" && \
	$(PYTHON_INTERP) -m pip install pipreqs)

requirements: check-pipreqs
	$(call RENDER_PREAMBLE,Generating requirements.txt file)
	@pipreqs --force \
	--savepath $(REQUIREMENTS_TXT) \
	--ignore $(PROJECT_DIRECTORY)/utils/test_data/ \
	$(PROJECT_DIRECTORY)

get-deps: requirements
	$(call RENDER_PREAMBLE,Installing all project dependencies)
	@$(PYTHON_INTERP) -m pip install --requirement $(REQUIREMENTS_TXT)

test:
	$(call RENDER_PREAMBLE,Running pytest over project)
	@$(PYTHON_INTERP) -m pytest -vs $(PROJECT_DIRECTORY)

full: get-deps test

# Might deprecate this - not used often enough
test-coverage:
	$(call RENDER_PREAMBLE,Running pytest over project with coverage report)
	@$(PYTHON_INTERP) -m pytest -vs $(PROJECT_DIRECTORY) \
	--cov=$(PROJECT_DIRECTORY) \
	--cov-report=html:$(DUMP_COVERAGE) \
	--cov-config=$(PROJECT_DIRECTORY)/coverage.rc
	@echo "Coverage report will be dumped to: $(DUMP_COVERAGE)"

lint:
	$(call RENDER_PREAMBLE,Linting the project using pylint static analysis tool)
	@$(PYTHON_INTERP) -m pylint $(PROJECT_DIRECTORY) \
	--output-format=colorized \
	--exit-zero \
	--msg-template "{msg_id}{line:4d}{column:3d} {obj} {msg}"
