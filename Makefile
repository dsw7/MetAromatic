.PHONY = help requirements

.DEFAULT_GOAL = help

define HELP_LIST_TARGETS
##################################
# MET-AROMATIC OFFICIAL MAKEFILE #
##################################

 To display all targets:
    > make help
 To generate a requirements.txt file
    > make requirements
 To lint the project
    > make lint

endef

export HELP_LIST_TARGETS

help:
	@echo "$$HELP_LIST_TARGETS"

requirements:
	@echo "Generating requirements.txt"
	@pipreqs --force

lint:
	@echo "Linting the project using PyLint static analysis tool"
	@pylint $(PWD)/MetAromatic \
	--output-format=colorized \
	--exit-zero \
	--msg-template "{msg_id}{line:4d}{column:3d} {obj} {msg}"
