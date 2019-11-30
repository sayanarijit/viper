.PHONY: readme
readme:
	@echo "# Viper Infrastructure Commander" | tee README.md
	@echo "" | tee -a README.md
	@echo "[![PyPI version](https://img.shields.io/pypi/v/viper-infra-commander.svg)](https://pypi.org/project/viper-infra-commander)" | tee -a README.md
	@echo "[![PyPI pyversions](https://img.shields.io/pypi/pyversions/viper-infra-commander.svg)](https://pypi.org/project/viper-infra-commander)" | tee -a README.md
	@echo "[![Build Status](https://travis-ci.org/sayanarijit/viper.svg?branch=master)](https://travis-ci.org/sayanarijit/viper)" | tee -a README.md
	@echo "[![codecov](https://codecov.io/gh/sayanarijit/viper/branch/master/graph/badge.svg)](https://codecov.io/gh/sayanarijit/viper)" | tee -a README.md
	@echo "[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)" | tee -a README.md
	@echo "" | tee -a README.md
	@echo "## Installation" | tee -a README.md
	@echo "" | tee -a README.md
	@echo '```' | tee -a README.md
	@echo "pip install -U viper-infra-commander" | tee -a README.md
	@echo '```' | tee -a README.md
	@echo "" | tee -a README.md
	@.venv/bin/python -c "import viper; print(viper.__doc__)" | tee -a README.md
	@echo "" | tee -a README.md
	@echo "## Viper CLI Reference" | tee -a README.md
	@echo "" | tee -a README.md
	@echo '```' | tee -a README.md
	@viper --help | tee -a README.md
	@echo '```' | tee -a README.md
