# Stock Market Visualization in Dash

## Description

This is an application used to visualize the NASDAQ stock market using Dash (and Plotly).

This project is done as part of the course DATA15003 - Interactive Data Visualization at the University of Helsinki.

## Development

This project uses `uv` as its package management tool. You can install `uv` here: <https://docs.astral.sh/uv>. After having installed `uv`, here are some of the most common `uv` command lines:

- `uv add {package_name}`: add a new Python package/library.
- `uv run {some_script}.py`: run a Python script using the packages added in the project.
- `uv sync`: sync and create/update the virtual environment that rests in `.venv/` in the root folder of this project.

## Run the Application Locally

Before doing any of the following steps, please download `uv` and sync the virtual environment locally by running `uv sync` first.

### Mock Database

The mock database depends on the `data/` folder with the following structure:

```{txt}
data/
├── nasdag
│   ├── nasdag_stock_{timestamps}.csv
└── nasdaq_stock_screener.csv
```

To create a mock database, there are two options. First, if you don't have the fetched historical data (in `data/nasdaq/` folder) of the stock market yet, run following command to create a mock database with stock screeners data only:

```{bash}
uv run database/create_mock_database.py
```

and prepare the historical data of the stock market with the following command:

```{bash}
uv run database/fetch_data.py
```

This `fech_data.py` script reads the "last date" of the database in the file `database/metadata.json`. You can modify the metadata depending on your situation.

Otherwise, in the second option, if you already have fetched the historical data of the stock market, you can run the following command to create a mock database with both screener data and historical data.

```{bash}
uv run database/create_mock_database.py --populate-timeseries
```

### Run Application

- Run the application: `uv run src/app.py`
- The application should be available in: `http://localhost:8050/`
