"""Utilities for database operations."""

import sqlite3
from os.path import dirname, join, realpath

import pandas as pd

DATABASE_PATH = join(dirname(realpath(__file__)), "../../database/mock.db")


def execute_select_query(query: str) -> tuple[bool, pd.DataFrame | str]:
    """Execute SELECT query.

    Parameters
    ----------
    query : str
        The query to execute

    Returns
    -------
    tuple[bool, pd.DataFrame | None]
        - Whether the operation succeeded
        - The DataFrame if succeeds, the error message if fails

    """
    if not query.startswith("SELECT"):
        raise ValueError("The query is not an SELECT query.")
    try:
        conn = sqlite3.connect(DATABASE_PATH)

        df = pd.read_sql_query(query, conn)

        conn.close()

        return (True, df)

    except Exception as error:
        return (False, error)


def execute_update_query(query: str) -> tuple[bool, str]:
    """Execute UPDATE query.

    Parameters
    ----------
    query : str
        The query to execute

    Returns
    -------
    tuple[bool, str]
        - Whether the operation succeeded
        - The message from the operation

    """
    if not query.startswith("UPDATE"):
        raise ValueError("The query is not an UPDATE query.")
    try:
        conn = sqlite3.connect(DATABASE_PATH)

        conn.execute(query)

        conn.commit()

        conn.close()

        return (True, "success")

    except Exception as error:
        return (False, error)
