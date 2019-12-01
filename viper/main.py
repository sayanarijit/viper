from viper.cli import run

import sys

__all__ = ["main"]


def main() -> None:
    """The main entrypoint to Viper CLI."""
    sys.exit(run())


if __name__ == "__main__":
    main()
