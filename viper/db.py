from __future__ import annotations
from dataclasses import dataclass
from dataclasses import field
from sqlite3 import Cursor
from viper.const import Config

import sqlite3
import typing as t


@dataclass
class ViperDB:

    url: str = Config.db_url.value
    engine: t.Optional[sqlite3.Connection] = field(init=False, default=None)

    @classmethod
    def init(cls, url: str, force: bool = False) -> None:
        if force:
            with cls(url) as conn:
                conn.execute("DROP TABLE IF EXISTS results")

        with cls(url) as conn:
            conn.execute(
                """
                CREATE TABLE results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hash INTEGER NOT NULL,
                    trigger_time REAL NOT NULL,
                    task JSON NOT NULL,
                    host JSON NOT NULL,
                    args JSON NOT NULL,
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

    def __enter__(self) -> Cursor:
        self.engine = sqlite3.connect(self.url)
        return self.engine.cursor()

    def __exit__(self, exc_type: type, exc_value: t.Any, exc_traceback: Exception):
        try:
            self.engine.commit()
        except Exception:  # pragma: no cover
            self.engine.rollback()
        self.engine.close()
