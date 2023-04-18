####################################
#                                  #
#  MET-AROMATIC OFFICIAL MAKEFILE  #
#                                  #
####################################

.PHONY = help \
         test \
		 wheel install clean uninstall test-wheel full-wheel \
		 dockertest

.DEFAULT_GOAL = help

LIGHT_PURPLE = "\033[1;1;35m"
NO_COLOR = "\033[0m"

define RENDER_PREAMBLE
	@echo -e $(LIGHT_PURPLE)\> $(1)$(NO_COLOR)
endef

define HELP_LIST_TARGETS

Unit tests:

    To test the project:
        $$ make test

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

PROJECT_NAME = MetAromatic
ROOT_DIRECTORY := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
PROJECT_DIRECTORY = $(ROOT_DIRECTORY)/MetAromatic
DOCKER_TAG = ma

# ----------------------------------
# Unit tests
# ----------------------------------

test:
	$(call RENDER_PREAMBLE,Running pytest over project)
	@python3 -m pytest -vs -m 'test_command_line_interface' $(PROJECT_DIRECTORY)

# ----------------------------------
# Wheel install for importing Met-aromatic scripts
# ----------------------------------

wheel:
	$(call RENDER_PREAMBLE,Generating *.whl file for project)
	@python3 $(ROOT_DIRECTORY)/setup.py clean --all bdist_wheel

install: wheel
	$(call RENDER_PREAMBLE,Project will be installed under:)
	@python3 -m site --user-site
	$(call RENDER_PREAMBLE,Installing project...)
	@python3 -m pip install --user --force-reinstall dist/*whl
	$(call RENDER_PREAMBLE,List tree...)
	@tree --dirsfirst -I *pyc\|__pycache__ $(shell python3 -m site --user-site)/$(PROJECT_NAME)

clean:
	$(call RENDER_PREAMBLE,Removing scrap)
	@rm -rfv build/ dist/ *.egg-info/

uninstall:
	$(call RENDER_PREAMBLE,Uninstalling project)
	@python3 -m pip uninstall -y $(PROJECT_NAME)

test-wheel:
	$(call RENDER_PREAMBLE,Testing wheel installation)
	@cd MetAromatic/; python3 -m pytest -vs -m 'test_packaging' $(PROJECT_DIRECTORY); cd ..

full-wheel: install test-wheel clean uninstall

# ----------------------------------
# Other helpers
# ----------------------------------

help:
	$(call RENDER_PREAMBLE,MET-AROMATIC OFFICIAL MAKEFILE)
	@echo "$$HELP_LIST_TARGETS"

dockertest:
	$(call RENDER_PREAMBLE,Building docker image $(DOCKER_TAG))
	@docker build --tag $(DOCKER_TAG) $(ROOT_DIRECTORY)/
	$(call RENDER_PREAMBLE,Running tests in docker container)
	@docker run --interactive --tty --rm $(DOCKER_TAG)
