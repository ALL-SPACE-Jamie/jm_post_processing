# -*- coding: utf-8 -*-
"""
TLM Glass - Entry point.

Run this file to launch the dashboard::

    python app.py

Then open http://127.0.0.1:8050 in a browser.

@author: jmitchell
"""

from pathlib import Path

import dash_bootstrap_components as dbc
import diskcache
from dash import Dash, DiskcacheManager

from tlm_glass.dashboard import create_layout, register_callbacks

_cache_dir = Path(__file__).resolve().parent / ".dash_cache"
_cache_dir.mkdir(parents=True, exist_ok=True)
_background_callback_manager = DiskcacheManager(diskcache.Cache(str(_cache_dir)))

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY, dbc.icons.BOOTSTRAP],
    suppress_callback_exceptions=True,
    background_callback_manager=_background_callback_manager,
)
app.title = "TLM Glass"
app.layout = create_layout()
register_callbacks(app)


if __name__ == "__main__":
    app.run(debug=True)
