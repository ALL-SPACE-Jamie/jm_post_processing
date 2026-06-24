# -*- coding: utf-8 -*-
"""
TLM Inspector - Entry point.

Run this file to launch the dashboard::

    python app.py

Then open http://127.0.0.1:8050 in a browser.

@author: jmitchell
"""

from dash import Dash
import dash_bootstrap_components as dbc

from tlm_inspector.dashboard import create_layout, register_callbacks

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY, dbc.icons.BOOTSTRAP],
    suppress_callback_exceptions=True,
)
app.title = "TLM Inspector"
app.layout = create_layout()
register_callbacks(app)


if __name__ == "__main__":
    app.run(debug=True)
