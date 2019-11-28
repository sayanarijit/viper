from enum import Enum
from os import environ as env


class Config(Enum):

    max_workers = int(env.get("VIPER_MAX_WORKERS", 50))
    db_url = env.get("VIPER_DB_URL", "viperdb.sqlite3")
