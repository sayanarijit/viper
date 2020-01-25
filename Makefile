PRINT_DECRRIPTION := python -c "import viper; print(viper.__description__)"
PRINT_GETTING_STARTED_DOCS := python -c "import viper; print('\n'.join(viper.__doc__.splitlines()[11:]))"
PRINT_PYTHON_API_DOCS := python -c "from viper import collections; print(collections.__doc__)"
PRINT_CLI_DOCS := python -c "from viper import cli; print(cli.__doc__)"
PRINT_EXTENDING_CLI_DOCS := python -c "from viper import project; print(project.__doc__)"

.PHONY: install
install:
	pip install -r dev-requirements.txt
	$(MAKE) install-hooks


.PHONY: install-hooks
install-hooks:
	pre-commit install -f --hook-type pre-commit
	pre-commit install -f --hook-type pre-push


.PHONY: checks
checks:
	pre-commit run -a
	@$(MAKE) readme
	@$(MAKE) types


.PHONY: docs
docs:
	@$(PRINT_DECRRIPTION) | tee docs/description.rst
	@$(PRINT_GETTING_STARTED_DOCS) | tee docs/getting_started.rst
	@$(PRINT_PYTHON_API_DOCS) | tee docs/python_api.rst
	@$(PRINT_CLI_DOCS) | tee docs/cli.rst
	@$(PRINT_EXTENDING_CLI_DOCS) | tee docs/extending_cli.rst
	$(MAKE) readme
	$(MAKE) apidocs


.PHONY: readme
readme:
	@cat docs/logos.rst | tee README.rst
	@echo | tee -a README.rst
	@$(PRINT_DECRRIPTION) | tee -a README.rst
	@echo | tee -a README.rst
	@$(PRINT_GETTING_STARTED_DOCS) | tee -a README.rst
	@echo | tee -a README.rst
	@cat docs/footnotes.rst | tee -a README.rst


.PHONY: types
types:
	mypy --strict viper
	python -m typecov 100 typecov/linecount.txt

.PHONY: apidocs
apidocs:
	rm -rf docs/_build
	sphinx-apidoc -o docs viper -f
	cd docs && make html
	# open file://$(PWD)/docs/_build/html/index.html


.PHONY: unit-tests
unit-tests:
	pytest --cov=viper --cov-report html .


.PHONY: tests
tests: test

.PHONY: test
test:
	$(MAKE) checks
	$(MAKE) unit-tests
