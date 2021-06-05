####################################
#                                  #
#  MET-AROMATIC OFFICIAL MAKEFILE  #
#                                  #
####################################

.PHONY = help requirements lint test test-coverage

.DEFAULT_GOAL = help

define HELP_LIST_TARGETS
************************************
*                                  *
*  MET-AROMATIC OFFICIAL MAKEFILE  *
*                                  *
************************************

 To display all targets:
    > make help
 To generate a requirements.txt file
    > make requirements
 To lint the project
    > make lint
 To test the project
    > make test
 To test the project with coverage
    > make test-coverage

endef

export HELP_LIST_TARGETS

ROOT_DIRECTORY := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
PROJECT_DIRECTORY = $(ROOT_DIRECTORY)/MetAromatic
DUMP_COVERAGE = /tmp/htmlcov

help:
	@echo "$$HELP_LIST_TARGETS"

requirements:
	@echo "Generating requirements.txt"
	@pipreqs --force

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
