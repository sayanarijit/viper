from enum import Enum
from os import environ as env


class Config(Enum):

    db_url = env.get("VIPER_DB_URL", "viperdb.sqlite3")
