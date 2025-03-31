"""Script to create mock database."""

import sqlite3
from os.path import dirname, join, realpath


def main():
    """Create mock database."""
    conn = sqlite3.connect(join(dirname(realpath(__file__)), "mock.db"))

    with open(
        join(dirname(realpath(__file__)), "database_schema.sql"), "r"
    ) as sql_file:
        sql_script = sql_file.read()

    cursor = conn.cursor()
    cursor.executescript(sql_script)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
