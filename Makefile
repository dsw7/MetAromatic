.PHONY = help wheel setup test clean black mypy lint
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
To run black over Python code:
  $$ make black
To run mypy over Python code:
  $$ make mypy
To run pylint over Python code:
  $$ make lint
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

black:
	@black MetAromatic tests

mypy:
	@mypy --strict --cache-dir=/tmp/mypy_cache_metaromatic MetAromatic tests

lint:
	@pylint MetAromatic tests
