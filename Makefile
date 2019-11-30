.PHONY: readme
readme:
	@.venv/bin/python -c "import viper; print(viper.__doc__)" | tee README.md
	@echo "" | tee -a README.md
	@echo "# Viper CLI Reference" | tee -a README.md
	@echo "" | tee -a README.md
	@echo '```' | tee -a README.md
	@viper --help | tee -a README.md
	@echo '```' | tee -a README.md
