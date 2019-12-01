from __future__ import annotations

import sqlite3
import typing as t
from dataclasses import dataclass, field

from viper.const import Config


@dataclass
class ViperDB:

    url: str = Config.db_url.value
    engine: t.Optional[sqlite3.Connection] = field(init=False, default=None)

    @classmethod
    def init(cls, url, force=False):
        if force:
            with cls(url) as conn:
                conn.execute("DELETE FROM results")
                conn.execute("DROP TABLE results")

        with cls(url) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hash INTEGER UNIQUE NOT NULL,
                    task JSON NOT NULL,
                    host JSON NOT NULL,
                    command JSON NOT NULL,
                    stdout BLOB NOT NULL,
                    stderr BLOB NOT NULL,
                    returncode INTEGER NOT NULL,
                    start REAL NOT NULL,
                    end REAL NOT NULL,
                    retry INTEGER NOT NULL
                );
                """
            )

    def __enter__(self):
        self.engine = sqlite3.connect(self.url)
        return self.engine.cursor()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        try:
            self.engine.commit()
        except Exception:
            self.engine.rollback()
        self.engine.close()
