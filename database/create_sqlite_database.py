"""Script to create mock database."""

import logging
import sqlite3
from os import listdir
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


def fetch_historical_timeseries_data() -> pd.DataFrame:
    """Fetch historical timeseries data."""
    timeseries_path = "../data/nasdaq/"

    dfs = []
    for file in listdir(timeseries_path):
        if file == ".DS_Store":
            logger.warning("Detecting `DS_Store` file. Skipping it!")
            continue
        dfs.append(pd.read_csv(f"{timeseries_path}{file}"))

    df = pd.concat(dfs)
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")

    return df


def populate_stock_screener():
    """Populate stock screener into the database."""
    # Reading symbol data
    symbol_path = join(
        dirname(realpath(__file__)), "../data/nasdaq_stock_screener.csv"
    )
    symbol_df = pd.read_csv(symbol_path)
    symbol_df = process_stock_screener_data(symbol_df)

    # Reading historical timeseries data
    stock_df = fetch_historical_timeseries_data()

    # Populate into the database
    conn = sqlite3.connect(join(dirname(realpath(__file__)), "mock.db"))
    symbol_df.to_sql(
        name="stock_details", con=conn, if_exists="append", index=False
    )
    stock_df.to_sql(
        name="stock_timeseries", con=conn, if_exists="append", index=False
    )
    conn.close()


def process_etf_screener_data(df: pd.DataFrame) -> pd.DataFrame:
    """Process ETF screener data."""
    df.columns = df.columns.str.lower()
    df = df.dropna(subset=["symbol"])
    return df[ETF_SCREENER_COLUMNS]


def populate_etf_screener():
    """Populate ETF screener into the database."""
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
