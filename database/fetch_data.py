"""Fetch NASQAD data using yfinance."""

import json
import logging
import sqlite3
from datetime import datetime, timedelta
from os.path import dirname, join, realpath

import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)

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


def fetch_and_process_raw_stock_data(
    symbol: str, start_date: str
) -> pd.DataFrame:
    """Fetch and process raw stock data.

    Parameters
    ----------
    symbol : str
        The ticker symbol.
    start_date : str
        Start date from the metadata

    """
    df = yf.download(tickers=symbol, start=start_date, timeout=10)

    df.columns = df.columns.get_level_values(level=0)

    df = df.reset_index().rename(columns=TIMESERIES_MAPPING)
    df.columns.name = None

    df["symbol"] = symbol

    return df


def fetch_stock_data(symbols: list[str], start_date: str) -> pd.DataFrame:
    """Fetch stock data from yfinance.

    Parameters
    ----------
    symbols : list[str]
        List of the stock symbols
    start_date : str
        Start date from the metadata

    Returns
    -------
    pd.DataFrame
        The stock timeseries as DataFrame

    """
    dfs = map(
        lambda symbol: fetch_and_process_raw_stock_data(symbol, start_date),
        symbols,
    )
    return pd.concat(dfs)


def main():
    """Fetch data and populate into the database."""
    logger.info("Reading metadata")
    metadata_path = join(dirname(realpath(__file__)), "metadata.json")
    with open(metadata_path, "r") as f:
        metadata = json.load(f)
        last_end_date = datetime.strptime(
            metadata["last_end_date"], "%Y-%m-%d"
        )
        start_date = (last_end_date + timedelta(days=1)).strftime("%Y-%m-%d")

    conn = sqlite3.connect(join(dirname(realpath(__file__)), "mock.db"))

    logger.info("Fetching stock data.")
    stock_symbols = get_stock_symbols(conn)
    stock_df = fetch_stock_data(stock_symbols, start_date)

    logger.info("Updating metadata")
    with open(metadata_path, "w") as f:
        json.dump(
            {"last_end_date": stock_df["date"].max().strftime("%Y-%m-%d")}, f
        )

    logger.info("Writing stock timeseries into the database.")
    stock_df.to_csv(
        join(
            dirname(realpath(__file__)),
            f"../data/nasdaq/nasdag_stock_{datetime.now()}.csv",
        ),
        index=False,
    )
    stock_df.to_sql(
        name="stock_timeseries", con=conn, if_exists="append", index=False
    )

    conn.close()


if __name__ == "__main__":
    main()
