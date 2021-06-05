####################################
#                                  #
#  MET-AROMATIC OFFICIAL MAKEFILE  #
#                                  #
####################################

.PHONY = help requirements get-deps lint test test-coverage

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

ROOT_DIRECTORY := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
PROJECT_DIRECTORY = $(ROOT_DIRECTORY)/MetAromatic
REQUIREMENTS_TXT = $(ROOT_DIRECTORY)/requirements.txt
DUMP_COVERAGE = /tmp/htmlcov

help:
	$(call RENDER_TITLE,MET-AROMATIC OFFICIAL MAKEFILE)
	@echo "$$HELP_LIST_TARGETS"

requirements:
	$(call RENDER_PREAMBLE,Generating requirements.txt file)
	@pipreqs --force \
	--savepath $(REQUIREMENTS_TXT) \
	--ignore $(PROJECT_DIRECTORY)/utils/test_data/ \
	$(PROJECT_DIRECTORY)

get-deps: requirements
	$(call RENDER_PREAMBLE,Installing all project dependencies)
	@pip install --requirement $(REQUIREMENTS_TXT)

lint:
	$(call RENDER_PREAMBLE,Linting the project using pylint static analysis tool)
	@pylint $(PROJECT_DIRECTORY) \
	--output-format=colorized \
	--exit-zero \
	--msg-template "{msg_id}{line:4d}{column:3d} {obj} {msg}"

test:
	$(call RENDER_PREAMBLE,Running pytest over project)
	@pytest -vs $(PROJECT_DIRECTORY)

# Might deprecate this - not used often enough
test-coverage:
	$(call RENDER_PREAMBLE,Running pytest over project with coverage report)
	@pytest -vs $(PROJECT_DIRECTORY) \
	--cov=$(PROJECT_DIRECTORY) \
	--cov-report=html:$(DUMP_COVERAGE) \
	--cov-config=$(PROJECT_DIRECTORY)/coverage.rc
	@echo "Coverage report will be dumped to: $(DUMP_COVERAGE)"

full: get-deps test
