"""Main application view."""

import argparse
import os

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_extensions.enrich import (
    DashProxy,
    dash,
    html,
)

app = DashProxy(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.ZEPHYR, dbc.icons.BOOTSTRAP],
    suppress_callback_exceptions=True,
)
server = app.server

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(
            dbc.NavLink(
                [
                    html.I(className="bi bi-graph-up me-1"),
                    "Performance Timeseries",
                ],
                href="/timeseries",
            )
        ),
        dbc.NavItem(
            dbc.NavLink(
                [
                    html.I(className="bi bi-clipboard-data me-1"),
                    "Market Overview",
                ],
                href="/",
            )
        ),
    ],
    brand="NASDAQ Visualization",
    brand_href="/",
    color="primary",
    dark=True,
)

app.layout = dmc.MantineProvider(
    [
        navbar,
        dash.page_container,
    ]
)

if __name__ == "__main__":
    os.environ["STOCK_DATABASE"] = "mock.db"

    parser = argparse.ArgumentParser(
        description="Run Dash app in production or development mode"
    )
    parser.add_argument(
        "--prod",
        action="store_true",
        help="Run in production mode (debug off)",
    )
    args = parser.parse_args()

    if args.prod:
        app.run(port=8050, debug=False)
    else:
        app.run(port=8050, debug=True)
