"""Common contants are defined here."""

from enum import Enum
from os import environ as env
from os import path

__all__ = ["Config"]


class Config(Enum):
    """Default viper configuration."""

    db_url = env.get("VIPER_DB_URL", "viperdb.sqlite3")
    max_workers = int(env.get("VIPER_MAX_WORKERS", 0))
    modules_path = path.expanduser(env.get("VIPER_MODULES_PATH", "."))
