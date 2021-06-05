####################################
#                                  #
#  MET-AROMATIC OFFICIAL MAKEFILE  #
#                                  #
####################################

.PHONY = help requirements get-deps lint test test-coverage

.DEFAULT_GOAL = help

define HELP_LIST_TARGETS

To display all targets:
    $$ make help
To generate a requirements.txt file:
    $$ make requirements
To setup all project dependencies:
    $$ make get-deps
To lint the project:
    $$ make lint
To test the project:
    $$ make test
To test the project with coverage:
    $$ make test-coverage
endef

export HELP_LIST_TARGETS

LIGHT_PURPLE = "\033[4;1;35m"
NO_COLOR = "\033[0m"
ROOT_DIRECTORY := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
PROJECT_DIRECTORY = $(ROOT_DIRECTORY)/MetAromatic
REQUIREMENTS_TXT = $(ROOT_DIRECTORY)/requirements.txt
DUMP_COVERAGE = /tmp/htmlcov

help:
	@echo -e $(LIGHT_PURPLE)MET-AROMATIC OFFICIAL MAKEFILE$(NO_COLOR)
	@echo "$$HELP_LIST_TARGETS"

requirements:
	@echo "Generating $(REQUIREMENTS_TXT)"
	@pipreqs --force --savepath $(REQUIREMENTS_TXT) $(PROJECT_DIRECTORY)

get-deps: requirements
	@echo "Installing all project dependencies using $(REQUIREMENTS_TXT)"
	@pip install --requirement $(REQUIREMENTS_TXT)

lint:
	@echo "Linting the project using pylint static analysis tool"
	@pylint $(PROJECT_DIRECTORY) \
	--output-format=colorized \
	--exit-zero \
	--msg-template "{msg_id}{line:4d}{column:3d} {obj} {msg}"

test:
	@pytest -vs $(PROJECT_DIRECTORY)

# Might deprecate this - not used often enough
test-coverage:
	@echo "Running pytest over project with coverage report"
	@pytest -vs $(PROJECT_DIRECTORY) \
	--cov=$(PROJECT_DIRECTORY) \
	--cov-report=html:$(DUMP_COVERAGE) \
	--cov-config=$(PROJECT_DIRECTORY)/coverage.rc
	@echo "Coverage report will be dumped to: $(DUMP_COVERAGE)"
