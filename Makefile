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
	$(MAKE) readme
	python -c "import viper; print(viper.__doc__)" | tee docs/intro.rst
	$(MAKE) apidocs


.PHONY: readme
readme:
	@python -c "import viper; print(viper.__doc__)" | tee README.rst

.PHONY: types
types:
	# TODO: remove the "|| true"
	mypy --strict viper || true
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
