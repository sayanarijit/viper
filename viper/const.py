"""Common contants are defined here."""

from enum import Enum
from os import environ as env

__all__ = ["Config"]


class Config(Enum):
    """Default viper configuration."""

    db_url = env.get("VIPER_DB_URL", "viperdb.sqlite3")
    max_workers = int(env.get("VIPER_MAX_WORKERS", 0))
