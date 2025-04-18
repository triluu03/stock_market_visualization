"""Home page for search and search options."""

from typing import Literal

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from dash_extensions.enrich import (
    Input,
    Output,
    callback,
    callback_context,
    dash,
    dcc,
    html,
)

from utils.database import execute_select_query

dash.register_page(
    __name__, path="/", name="market_overview", title="Market Overview"
)


def get_stock_details() -> pd.DataFrame:
    """Get gene annotation from the database."""
    select_result = execute_select_query("SELECT * FROM stock_details")
    if select_result[0]:
        stock_details: pd.DataFrame = select_result[1]
    else:
        raise ValueError(f"{select_result[1]}")

    return stock_details


def get_latest_trade_details() -> pd.DataFrame:
    """Get the latest trade details."""
    select_result = execute_select_query(
        "SELECT * FROM stock_timeseries WHERE date = "
        "(SELECT MAX(date) FROM stock_timeseries)"
    )
    if select_result[0]:
        stock_df: pd.DataFrame = select_result[1]
    else:
        raise ValueError(f"{select_result[1]}")

    return stock_df


def get_market_overview() -> pd.DataFrame:
    """Get market overview data."""
    stock_details = get_stock_details()
    df = get_latest_trade_details()

    # Process
    df = (
        df.assign(delta=df["price_close"] / df["price_open"] - 1)
        .filter(items=["symbol", "price_close", "delta"])
        .merge(stock_details, on=["symbol"], validate="1:1")
        .assign(market_cap=df["price_close"] * df["volume"])
        .fillna({"sector": "N/A"})
    )

    # Set colors for plotting
    df["colors"] = pd.cut(
        df["delta"],
        bins=[-1, -0.05, -0.02, 0, 0.02, 0.05, 1],
        labels=["red", "indianred", "gray", "lightgreen", "lime", "green"],
    ).cat.set_categories(
        ["(?)", "red", "indianred", "gray", "lightgreen", "lime", "green"]
    )

    return df


stock_df = get_market_overview()


def layout(refresh: bool = False, **kwargs):
    """Layout for home page with search functionality.

    Parameters
    ----------
    refresh : bool, default False
        Whether to fetch the gene annotation again.

    """
    global stock_df
    if refresh:
        stock_df = get_market_overview()

    # Construct filter options
    options_sector = [
        sector for sector in stock_df["sector"].drop_duplicates().sort_values()
    ]
    all_filter_options = {"sector": options_sector}

    plot_type_selector = html.Div(
        [
            dbc.Label("Size represents:"),
            dbc.RadioItems(
                options=[
                    {"label": "Market Cap", "value": "market_cap"},
                    {"label": "Volume", "value": "volume"},
                ],
                value="market_cap",
                id="treemap-groupby",
                inline=True,
            ),
        ],
        className="mb-3 mt-4",
    )

    filter_view = html.Div(
        children=[
            plot_type_selector,
            html.Div(
                [
                    dbc.Checklist(
                        options=["All sectors"],
                        value=["All sectors"],
                        id="sector-checklist-all",
                        switch=True,
                    ),
                    dbc.Checklist(
                        options=[
                            {"label": sector, "value": sector}
                            for sector in options_sector
                        ],
                        value=options_sector,
                        id="sector-checklist-input",
                    ),
                ],
            ),
        ]
    )

    return dbc.Container(
        children=[
            dcc.Store(id="all-filter-options", data=all_filter_options),
            dcc.Store(
                id="fetched-dataframe", data=stock_df.to_dict(orient="records")
            ),
            dbc.Row(
                children=[
                    dbc.Col(
                        children=dbc.Row(children=filter_view),
                        # style={"overflow": "scroll", "height": "85vh"},
                        width=2,
                    ),
                    dbc.Col(
                        dbc.Row(
                            dcc.Graph(
                                id="treemap-market-overview",
                                style={
                                    "height": "90vh",
                                    "width": "100%",
                                },
                            )
                        )
                    ),
                ]
            ),
        ],
    )


@callback(
    Output("sector-checklist-input", "value"),
    Output("sector-checklist-all", "value"),
    Input("sector-checklist-input", "value"),
    Input("sector-checklist-all", "value"),
    Input("all-filter-options", "data"),
)
def sync_sector_checklist(
    sector_selected: list[str],
    sector_all_selected: list[str],
    all_filter_options: dict[Literal["sector"], list[str]],
) -> tuple[list[str], list[str]]:
    """Sync sector checklist.

    Parameters
    ----------
    sector_selected : list[str]
        The selected sectors
    sector_all_selected : list[str]
        Whether the "All sectors" option is selected
    all_filter_options : dict[str, list[str]]
        The stored filter options

    Returns
    -------
    tuple[list[str], list[str]]
        The synced values for sector filter options.

    """
    ctx = callback_context

    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if input_id == "sector-checklist-input":
        sector_all_selected = (
            ["All sectors"]
            if set(sector_selected) == set(all_filter_options["sector"])
            else []
        )
    else:
        sector_selected = (
            all_filter_options["sector"] if sector_all_selected else []
        )
    return sector_selected, sector_all_selected


@callback(
    Output("treemap-market-overview", "figure"),
    Input("fetched-dataframe", "data"),
    Input("sector-checklist-input", "value"),
    Input("treemap-groupby", "value"),
)
def update_treemap(
    data: list[dict],
    sector_selected: list[str],
    treemap_groupby: Literal["market_cap", "volume"],
) -> go.Figure:
    """Update market overview.

    Parameters
    ----------
    data : list[dict]
        The fetched data from the database

    """
    stock_df = pd.DataFrame(data)

    fig = px.treemap(
        stock_df.loc[stock_df["sector"].isin(sector_selected)],
        path=[px.Constant("NASDAQ"), "sector", "symbol"],
        values=treemap_groupby,
        color="colors",
        color_discrete_map={
            "(?)": "#262931",
            "red": "red",
            "indianred": "indianred",
            "gray": "gray",
            "lightgreen": "lightgreen",
            "lime": "lime",
            "green": "green",
        },
        hover_data={"delta": ":.2p"},
        custom_data=["industry", "sector"],
        title="NASDAQ Market Overview",
    ).update_traces(
        textposition="middle center",
        texttemplate="%{label}<br>%{customdata[2]:.2p}",
        hovertemplate=(
            "%{parent} - %{customdata[0]}"
            "<br>Market Cap: %{value:,}"
            "<br>1-day: %{customdata[2]:.2p}"
        ),
    )

    return fig


# @callback(
#     Input("treemap-market-overview", "clickData"), prevent_initial_call=True
# )
# def redirect_on_click(click_data):
#     """Redirect to candle stick plot."""
#     if click_data:
#         print(click_data)
