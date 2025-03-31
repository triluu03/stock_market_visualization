"""Script to create mock database."""

import logging
import sqlite3
from os.path import dirname, join, realpath

import pandas as pd

logger = logging.getLogger(__name__)

STOCK_SCREENER_COLUMNS = [
    "symbol",
    "name",
    "country",
    "ipo_year",
    "volume",
    "sector",
    "industry",
]

ETF_SCREENER_COLUMNS = [
    "symbol",
    "name",
]


def create_mock_database():
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


def process_stock_screener_data(df: pd.DataFrame) -> pd.DataFrame:
    """Process stock screener data."""
    df.columns = df.columns.str.lower()
    df = df.dropna(subset=["symbol"])
    return df.rename(columns={"ipo year": "ipo_year"})[STOCK_SCREENER_COLUMNS]


def populate_stock_screener():
    """Populate stock screener into the database."""
    stock_path = join(
        dirname(realpath(__file__)), "../data/nasdaq_stock_screener.csv"
    )
    stock_df = pd.read_csv(stock_path)

    stock_df = process_stock_screener_data(stock_df)

    # Populate into the database
    conn = sqlite3.connect(join(dirname(realpath(__file__)), "mock.db"))
    stock_df.to_sql(
        name="stock_details", con=conn, if_exists="append", index=False
    )
    conn.close()


def process_etf_screener_data(df: pd.DataFrame) -> pd.DataFrame:
    """Process ETF screener data."""
    df.columns = df.columns.str.lower()
    df = df.dropna(subset=["symbol"])
    return df[ETF_SCREENER_COLUMNS]


def populate_etf_screener():
    """Populate stock screener into the database."""
    etf_path = join(
        dirname(realpath(__file__)), "../data/nasdaq_etf_screener.csv"
    )
    etf_df = pd.read_csv(etf_path)

    etf_df = process_etf_screener_data(etf_df)

    # Populate into the database
    conn = sqlite3.connect(join(dirname(realpath(__file__)), "mock.db"))
    etf_df.to_sql(
        name="etf_details", con=conn, if_exists="append", index=False
    )
    conn.close()


def main():
    """Create mock database and populate data."""
    logger.info("Creating the mock database in sqlite3.")
    create_mock_database()

    logger.info("Populating the stock screener into the database.")
    populate_stock_screener()

    logger.info("Populating the ETF screener into the database.")
    populate_etf_screener()


if __name__ == "__main__":
    main()
