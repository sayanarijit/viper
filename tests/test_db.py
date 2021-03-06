from viper.db import ViperDB

import os
import pytest
import sqlite3

DB_URL = "tests/data/viperdb.sqlite3"


def test_viper_db_init():

    if os.path.exists(DB_URL):
        os.remove(DB_URL)

    ViperDB.init(DB_URL)

    with pytest.raises(sqlite3.OperationalError) as e:
        ViperDB.init(DB_URL)
        assert "already exists" in str(vars(e))

    ViperDB.init(DB_URL, force=True)


def test_viper_db_insert():

    ViperDB.init(DB_URL, force=True)

    with ViperDB(DB_URL) as conn:
        conn.execute(
            """
            INSERT INTO results (
                hash, trigger_time, task, host, args, command, stdout,
                stderr, returncode, start, end, retry
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
            """,
            (999, 1.2, "foo", "2", "bar", "3", "4", "5", 6, 7, 8, 9),
        )

    with ViperDB(DB_URL) as conn:
        data = next(conn.execute("SELECT id, task FROM results"))

    assert data == (1, "foo")
