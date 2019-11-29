.PHONY: readme
readme:
	.venv/bin/python -c "import viper; print(viper.__doc__)" > README.md
