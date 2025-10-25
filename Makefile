.PHONY = help wheel setup test clean py
.DEFAULT_GOAL = help

define HELP_LIST_TARGETS
To build wheel:
  $$ make wheel
To set up the project:
  $$ make setup
To test the project:
  $$ make test
To remove build, dist and other setup.py directories:
  $$ make clean
To run formatter, linter and static analysis:
  $$ make py
endef

export HELP_LIST_TARGETS

help:
	@echo "$$HELP_LIST_TARGETS"

wheel:
	@pip3 install --upgrade build
	@python3 -m build

setup: wheel
	@pip3 install dist/*whl --force-reinstall

test:
	@pip3 install nox
	@nox --envdir=/tmp

clean:
	@rm -rfv dist/ *.egg-info/

py:
	@black MetAromatic tests
	@pylint --exit-zero MetAromatic tests
	@mypy --strict --cache-dir=/tmp/mypy_cache_metaromatic MetAromatic tests
