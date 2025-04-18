"""404 Not Found page."""

import dash_bootstrap_components as dbc
from dash_extensions.enrich import dash, html

dash.register_page(__name__)


def layout(**kwargs):
    """Layout for 404 Not Found page."""
    return dbc.Container(
        children=[
            html.H1(
                children="404 Not Found",
                style={"textAlign": "left"},
            )
        ],
        className="p-2",
    )
