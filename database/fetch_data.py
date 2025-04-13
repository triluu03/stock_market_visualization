"""Fetch NASQAD data using yfinance."""

import logging
import sqlite3
from os.path import dirname, join, realpath

import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)

START_DATE = "2005-01-01"

TIMESERIES_MAPPING = {
    "Date": "date",
    "Close": "price_close",
    "High": "price_high",
    "Low": "price_low",
    "Open": "price_open",
    "Volume": "volume",
}


def get_stock_symbols(conn: sqlite3.Connection) -> list[str]:
    """Get Stock symbols from the database.

    Parameters
    ----------
    conn : sqlite3.Connection
        The connection to the sqlite3 database

    Returns
    -------
    list[str]
        The list of stock symbols

    """
    df = pd.read_sql_query(sql="SELECT * FROM stock_details", con=conn)
    return df["symbol"].unique().tolist()


def fetch_and_process_raw_stock_data(symbol: str) -> pd.DataFrame:
    """Fetch and process raw stock data.

    Parameters
    ----------
    symbol : str
        The ticker symbol.

    """
    df = yf.download(tickers=symbol, start=START_DATE)

    df.columns = df.columns.get_level_values(level=0)

    df = df.reset_index().rename(columns=TIMESERIES_MAPPING)
    df.columns.name = None

    df["symbol"] = symbol

    return df


def fetch_stock_data(symbols: list[str]) -> pd.DataFrame:
    """Fetch stock data from yfinance.

    Parameters
    ----------
    symbols : list[str]
        List of the stock symbols

    Returns
    -------
    pd.DataFrame
        The stock timeseries as DataFrame

    """
    dfs = map(fetch_and_process_raw_stock_data, symbols)
    return pd.concat(dfs)


def main():
    """Fetch data and populate into the database."""
    conn = sqlite3.connect(join(dirname(realpath(__file__)), "mock.db"))

    logger.info("Fetching stock data.")
    stock_symbols = get_stock_symbols(conn)
    stock_df = fetch_stock_data(stock_symbols)

    logger.info("Writing stock timeseries into the database.")
    stock_df.to_sql(
        name="stock_timeseries", con=conn, if_exists="append", index=False
    )

    conn.close()


if __name__ == "__main__":
    main()
