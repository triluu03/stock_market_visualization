"""Performance timeseries page."""

from typing import Literal

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash_extensions.enrich import (
    Input,
    Output,
    callback,
    dash,
    dcc,
    html,
)

from utils.database import execute_select_query, get_stock_details

START_DATE = "2020-01-01"

dash.register_page(
    __name__, path="/timeseries", name="timeseries", title="Timeseries"
)


def get_stock_timeseries(symbol: str) -> pd.DataFrame:
    """Get stock timeseries data."""
    select_result = execute_select_query(
        f"SELECT * FROM stock_timeseries WHERE symbol = '{symbol}' "
        f"AND date >= '{START_DATE}'"
    )
    if select_result[0]:
        df: pd.DataFrame = select_result[1]
    else:
        raise ValueError(f"{select_result[1]}")

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(by="date")

    return df


def layout(symbol: str | None = None, **kwargs):
    """Create layout for performance timeseries."""
    stock_df = get_stock_details()

    filter_view = html.Div(
        children=[
            html.Div(
                dcc.Dropdown(
                    options=stock_df["symbol"].unique(),
                    searchable=True,
                    placeholder="Select a stock...",
                    multi=False,
                    id="selected-stock-symbols",
                ),
                className="mt-4 mb-3",
            ),
            html.Div(
                [
                    dbc.RadioItems(
                        options=[
                            {
                                "label": "Daily Trade",
                                "value": "candlestick",
                            },
                            {
                                "label": "Performance Index",
                                "value": "line_graph",
                            },
                        ],
                        value="candlestick",
                        id="timeseries-plot-type",
                        inline=True,
                    ),
                ],
                className="mb-3",
            ),
            html.Div(
                [
                    dbc.Label("Select Date Range"),
                    dbc.RadioItems(
                        options=[
                            {"label": "Year to date", "value": "ytd"},
                            {"label": "1 month", "value": "30D"},
                            {"label": "6 months", "value": "183D"},
                            {"label": "1 year", "value": "365D"},
                            {"label": "3 years", "value": "1096D"},
                            {"label": "5 years", "value": "1826D"},
                        ],
                        value="183D",
                        id="timeseries-date-range",
                    ),
                ],
            ),
        ]
    )

    return dbc.Container(
        children=[
            dcc.Store(id="timeseries-data"),
            dcc.Store(
                id="stock-details-data",
                data=stock_df[["symbol", "name"]]
                .set_index("symbol")
                .to_dict(orient="index"),
            ),
            dbc.Row(
                children=[
                    dbc.Col(children=dbc.Row(children=filter_view), width=2),
                    dbc.Col(
                        dbc.Row(
                            dcc.Graph(
                                id="performance-timeseries-graph",
                                style={"height": "90vh"},
                            ),
                        )
                    ),
                ]
            ),
        ],
    )


@callback(
    Output("timeseries-data", "data"),
    Input("selected-stock-symbols", "value"),
    prevent_initial_call=True,
)
def fetch_timeseries_data(
    selected_stock_symbol: str | None,
) -> list[dict]:
    """Fetch timeseries data from the database.

    Parameters
    ----------
    selected_stock_symbol : str | None
        The selected stock symbol.

    """
    if not selected_stock_symbol:
        return dash.no_update

    df = get_stock_timeseries(selected_stock_symbol)
    return df.to_dict(orient="records")


def create_candlestick_graph(
    df: pd.DataFrame, selected_stock_symbol: str, stock_name: str
) -> go.Figure:
    """Create candlestick graph.

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe to plot.
    selected_stock_symbol : str
        The selected stock symbol.
    stock_name : str
        The name of the stock.

    """
    return go.Figure(
        data=[
            go.Candlestick(
                x=df["date"],
                open=df["price_open"],
                high=df["price_high"],
                low=df["price_low"],
                close=df["price_close"],
            )
        ]
    ).update_layout(
        title=dict(
            text=f"{selected_stock_symbol} | {stock_name}",
            subtitle=dict(
                text=(
                    f"Daily trading details "
                    f"from {df.iloc[0]['date'].strftime('%Y-%m-%d')} "
                    f"to {df.iloc[-1]['date'].strftime('%Y-%m-%d')}"
                )
            ),
        )
    )


def create_line_graph(
    df: pd.DataFrame, selected_stock_symbol: str, stock_name: str
) -> go.Figure:
    """Create line graph.

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe to plot.
    selected_stock_symbol : str
        The selected stock symbol.
    stock_name : str
        The name of the stock.

    """
    return (
        px.line(
            data_frame=df.assign(
                performance_index=df["price_close"] / df.iloc[0]["price_close"]
                - 1
            ),
            x="date",
            y="performance_index",
            hover_data=["price_close"],
        )
        .update_layout(
            title=dict(
                text=f"{selected_stock_symbol} | {stock_name}",
                subtitle=dict(
                    text=(
                        f"Performance index "
                        f"from {df.iloc[0]['date'].strftime('%Y-%m-%d')} "
                        f"to {df.iloc[-1]['date'].strftime('%Y-%m-%d')}"
                    )
                ),
            ),
            xaxis_title="Date",
            yaxis_title="Price",
            yaxis_tickformat=".0%",
            margin=dict(t=100),
        )
        .update_traces(
            hovertemplate=(
                "Date: %{x}"
                "<br>Performance: %{y:.2%}"
                "<br>Price: %{customdata[0]:,.2f}"
                "<extra></extra>"
            ),
            line=dict(
                color=(
                    "#089000"
                    if df["price_close"].iloc[-1] >= df["price_close"].iloc[0]
                    else "#ff0000"
                ),
                width=3,
            ),
        )
        .update_xaxes(
            rangeslider_visible=True,
        )
    )


@callback(
    Output("performance-timeseries-graph", "figure"),
    Input("timeseries-data", "data"),
    Input("timeseries-plot-type", "value"),
    Input("timeseries-date-range", "value"),
    Input("stock-details-data", "data"),
    Input("selected-stock-symbols", "value"),
)
def update_graph(
    data: list[dict],
    plot_type: Literal["candlestick", "line_graph"],
    time_delta: str,
    stock_details_data: dict,
    selected_stock_symbol: str | None,
) -> go.Figure:
    """Update the performance timeseries graph.

    Parameters
    ----------
    data : list[dict]
        The fetched data from the database.
    plot_type : Literal["candlestick", "line_graph"]
        The type of plot to display.
    time_delta : str
        The date range to filter the data. Should be in pd.Timedelta format.
    stock_details_data : dict
        The stock details data.
    selected_stock_symbol : str | None
        The selected stock symbol.

    """
    if not selected_stock_symbol:
        return go.Figure().add_annotation(
            text="Please select at least one stock to show!",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=14),
        )

    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(by="date")

    if time_delta == "ytd":
        df = df.loc[
            df["date"]
            >= pd.Timestamp(year=df["date"].max().year, month=1, day=1)
        ]
    else:
        df = df.loc[df["date"] >= df["date"].max() - pd.Timedelta(time_delta)]

    match plot_type:
        case "candlestick":
            fig = create_candlestick_graph(
                df,
                selected_stock_symbol,
                stock_details_data[selected_stock_symbol]["name"],
            )
        case "line_graph":
            fig = create_line_graph(
                df,
                selected_stock_symbol,
                stock_details_data[selected_stock_symbol]["name"],
            )

    return fig
