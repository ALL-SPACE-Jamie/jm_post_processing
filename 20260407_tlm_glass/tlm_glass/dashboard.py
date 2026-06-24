# -*- coding: utf-8 -*-
"""
TLM Glass - Dash layout and callbacks.

Defines the complete dashboard layout (all tabs rendered simultaneously
for reliable callback wiring) and registers every Dash callback.

@author: jmitchell
"""

import os
from datetime import datetime

import numpy as np
import pandas as pd
from dash import Dash, html, dcc, no_update, Input, Output, State
import dash_bootstrap_components as dbc

from .config import (
    COLORS, CARD_STYLE, TAB_STYLE, TAB_SELECTED_STYLE,
    FILE_TYPES, MAX_INLINE_PLOTS, VERSION, CHANGELOG,
)
from . import parser
from . import plots


# ---------------------------------------------------------------------------
# Module-level figure caches (used for saving to disk)
# ---------------------------------------------------------------------------

_port_figure_cache: dict = {}
_freq_figure_cache: dict = {}
_stats_figure_cache: dict = {}


# ===================================================================
# Layout
# ===================================================================

def create_layout() -> html.Div:
    """Build the complete dashboard layout with all tabs pre-rendered."""
    return html.Div(
        style={
            "backgroundColor": COLORS["background"],
            "minHeight": "100vh",
            "color": COLORS["text"],
            "fontFamily": "Inter, -apple-system, BlinkMacSystemFont, sans-serif",
        },
        children=[
            _header(),
            dcc.Store(id="data-store"),
            dcc.Store(id="full-results-store"),
            dcc.Store(id="stats-context-store", data=None),
            dcc.Download(id="download-index"),
            dcc.Download(id="download-full-results"),

            dcc.Tabs(
                id="main-tabs",
                value="data-tab",
                style={"backgroundColor": COLORS["sidebar"]},
                children=[
                    dcc.Tab(
                        label="Data", value="data-tab",
                        style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE,
                    ),
                    dcc.Tab(
                        label="1D Port Plot", value="port-tab",
                        style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE,
                    ),
                    dcc.Tab(
                        label="1D Frequency Plot", value="freq-tab",
                        style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE,
                    ),
                    dcc.Tab(
                        label="Statistics", value="stats-tab",
                        style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE,
                    ),
                    dcc.Tab(
                        label="Documentation", value="docs-tab",
                        style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE,
                    ),
                    dcc.Tab(
                        label="Further Development", value="dev-tab",
                        style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE,
                    ),
                ],
            ),

            html.Div(style={"padding": "24px 32px"}, children=[
                html.Div(id="data-tab-content", children=_data_tab()),
                html.Div(
                    id="port-tab-content", children=_port_plot_tab(),
                    style={"display": "none"},
                ),
                html.Div(
                    id="freq-tab-content", children=_freq_plot_tab(),
                    style={"display": "none"},
                ),
                html.Div(
                    id="stats-tab-content", children=_stats_tab(),
                    style={"display": "none"},
                ),
                html.Div(
                    id="docs-tab-content", children=_docs_tab(),
                    style={"display": "none"},
                ),
                html.Div(
                    id="dev-tab-content", children=_dev_tab(),
                    style={"display": "none"},
                ),
            ]),
        ],
    )


# -------------------------------------------------------------------
# Individual tab layouts
# -------------------------------------------------------------------

def _header() -> html.Div:
    return html.Div(
        style={
            "backgroundColor": COLORS["sidebar"],
            "padding": "16px 32px",
            "borderBottom": f"1px solid {COLORS['border']}",
            "display": "flex",
            "alignItems": "center",
        },
        children=[
            html.H1(
                "TLM Glass",
                style={
                    "margin": "0",
                    "color": COLORS["primary"],
                    "fontSize": "24px",
                    "fontWeight": "700",
                },
            ),
            html.Span(
                f"v{VERSION}",
                style={
                    "color": COLORS["text_muted"],
                    "fontSize": "11px",
                    "marginLeft": "8px",
                    "alignSelf": "flex-end",
                },
            ),
            html.Span(
                "ALL.SPACE",
                style={
                    "color": COLORS["text_muted"],
                    "fontSize": "11px",
                    "letterSpacing": "3px",
                    "marginLeft": "16px",
                    "alignSelf": "flex-end",
                },
            ),
        ],
    )


def _data_tab() -> html.Div:
    indicator_blank = html.Span(
        "\u25CF", style={"color": COLORS["border"], "fontSize": "18px"},
    )
    return html.Div([
        # --- Section 1: Load Data ---
        html.Div(style=CARD_STYLE, children=[
            html.H4(
                "1. Load Data",
                style={"color": COLORS["accent"], "marginBottom": "12px"},
            ),
            html.P(
                "Enter the root directory containing TLM measurement results "
                "(paste a full Windows path; browsers cannot open a native folder picker).",
                style={"color": COLORS["text_muted"], "marginBottom": "12px",
                        "fontSize": "13px"},
            ),
            dbc.Row([
                dbc.Col([
                    dbc.Input(
                        id="data-path-input",
                        type="text",
                        placeholder=r"e.g.  C:\scratch\20251208\Tx\...\T2_Tx_TLM",
                        className="bg-dark text-light border-secondary",
                        style={"fontSize": "14px"},
                    ),
                ], width=7),
                dbc.Col([
                    dbc.Button(
                        [html.I(className="bi bi-folder2-open me-2"), "Load Data"],
                        id="load-data-btn",
                        color="primary",
                        className="w-100",
                        style={
                            "backgroundColor": COLORS["primary"],
                            "border": "none",
                        },
                    ),
                ], width=2),
                dbc.Col([
                    html.Div(
                        id="load-indicator",
                        children=indicator_blank,
                        style={"display": "flex", "alignItems": "center",
                                "height": "100%", "paddingLeft": "8px"},
                    ),
                ], width=3),
            ]),
            html.Div(
                id="load-progress-wrap",
                style={"marginTop": "12px", "display": "none"},
                children=[
                    dbc.Progress(
                        id="load-progress",
                        value=0,
                        striped=True,
                        animated=True,
                        color="info",
                        style={"height": "10px"},
                    ),
                    html.Small(
                        id="load-progress-text",
                        style={"color": COLORS["text_muted"], "display": "block",
                                "marginTop": "6px"},
                    ),
                ],
            ),
            html.Div(id="load-summary", style={"marginTop": "12px"}),
            html.Div(id="pipeline-checklist", style={"marginTop": "16px"}),
        ]),

        # --- Section 2: Download Index CSV ---
        html.Div(style=CARD_STYLE, children=[
            html.H4(
                "2. Download Summary Index",
                style={"color": COLORS["accent"], "marginBottom": "12px"},
            ),
            html.P(
                "Download the file index as a CSV after data has been loaded.",
                style={"color": COLORS["text_muted"], "marginBottom": "12px",
                        "fontSize": "13px"},
            ),
            dbc.Row([
                dbc.Col([
                    dbc.Button(
                        [html.I(className="bi bi-download me-1"),
                         "Download Index CSV"],
                        id="download-index-btn",
                        color="secondary",
                        outline=True,
                        disabled=True,
                    ),
                ], width=3),
                dbc.Col([
                    html.Div(
                        id="index-indicator",
                        children=indicator_blank,
                        style={"display": "flex", "alignItems": "center",
                                "height": "100%"},
                    ),
                ], width=9),
            ]),
        ]),

        # --- Section 3: Build & Download Full DataFrame ---
        html.Div(style=CARD_STYLE, children=[
            html.H4(
                "3. Full DataFrame",
                style={"color": COLORS["accent"], "marginBottom": "12px"},
            ),
            html.P(
                "Build a wide DataFrame with gain/phase at each file's setpoint "
                "frequency for every port. Then download as CSV.",
                style={"color": COLORS["text_muted"], "marginBottom": "12px",
                        "fontSize": "13px"},
            ),
            dbc.Row([
                dbc.Col([
                    dbc.Button(
                        [html.I(className="bi bi-calculator me-1"),
                         "Build DataFrame"],
                        id="build-full-btn",
                        color="secondary",
                        outline=True,
                        disabled=True,
                    ),
                ], width=2),
                dbc.Col([
                    dbc.Button(
                        [html.I(className="bi bi-download me-1"),
                         "Download CSV"],
                        id="download-full-csv-btn",
                        color="secondary",
                        outline=True,
                        disabled=True,
                    ),
                ], width=2),
                dbc.Col([
                    html.Div(
                        id="full-results-status",
                        style={"display": "flex", "alignItems": "center",
                                "height": "100%"},
                    ),
                ], width=8),
            ]),
            html.Div(
                id="build-progress-wrap",
                style={"marginTop": "12px", "display": "none"},
                children=[
                    dbc.Progress(
                        id="build-progress",
                        value=0,
                        striped=True,
                        animated=True,
                        color="info",
                        style={"height": "10px"},
                    ),
                    html.Small(
                        id="build-progress-text",
                        style={"color": COLORS["text_muted"], "display": "block",
                                "marginTop": "6px"},
                    ),
                ],
            ),
        ]),
    ])


def _port_plot_tab() -> html.Div:
    return html.Div([
        html.Div(style=CARD_STYLE, children=[
            html.H4(
                "1D Port Plot Configuration",
                style={"color": COLORS["accent"], "marginBottom": "16px"},
            ),
            dbc.Row([
                dbc.Col([
                    _label("File Type"),
                    dcc.Dropdown(
                        id="port-file-type-dd",
                        options=[{"label": ft, "value": ft} for ft in FILE_TYPES],
                        value="OP",
                        clearable=False,
                    ),
                ], width=2),
                dbc.Col([
                    _label("Variable"),
                    dcc.Dropdown(
                        id="port-depvar-dd",
                        options=[
                            {"label": "Gain", "value": "gain"},
                            {"label": "Phase", "value": "phase"},
                        ],
                        value="gain",
                        clearable=False,
                    ),
                ], width=2),
                dbc.Col([
                    _label("Frequency [GHz]"),
                    dcc.Dropdown(
                        id="port-freq-dd",
                        options=[],
                        multi=True,
                        placeholder="Load data first\u2026",
                    ),
                ], width=3),
                dbc.Col([
                    _label("Spread Type"),
                    dcc.Dropdown(
                        id="port-spread-dd",
                        options=[
                            {"label": "Std Dev", "value": "STD"},
                            {"label": "IQR", "value": "IQR"},
                            {"label": "Min-Max", "value": "MinMax"},
                        ],
                        value="IQR",
                        clearable=False,
                    ),
                ], width=2),
                dbc.Col([
                    _label("Iteration"),
                    dcc.Dropdown(
                        id="port-iteration-dd",
                        options=[],
                        value=1,
                        clearable=False,
                    ),
                ], width=1),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([
                    _label("Y-axis Limits (Auto default)"),
                    dbc.InputGroup([
                        dbc.Input(
                            id="port-ylim-min", type="number",
                            placeholder="Auto (min)",
                            className="bg-dark text-light border-secondary",
                            size="sm",
                        ),
                        dbc.Input(
                            id="port-ylim-max", type="number",
                            placeholder="Auto (max)",
                            className="bg-dark text-light border-secondary",
                            size="sm",
                        ),
                    ], size="sm"),
                ], width=2),
                dbc.Col([
                    _label("Spread Y Limits (Auto default)"),
                    dbc.InputGroup([
                        dbc.Input(
                            id="port-sylim-min", type="number",
                            placeholder="Auto (min)",
                            className="bg-dark text-light border-secondary",
                            size="sm",
                        ),
                        dbc.Input(
                            id="port-sylim-max", type="number",
                            placeholder="Auto (max)",
                            className="bg-dark text-light border-secondary",
                            size="sm",
                        ),
                    ], size="sm"),
                ], width=2),
                dbc.Col(width=4),
                dbc.Col([
                    _label("\u00A0"),
                    dbc.Button(
                        "Generate",
                        id="port-generate-btn",
                        color="primary",
                        className="w-100",
                        style={
                            "backgroundColor": COLORS["primary"],
                            "border": "none",
                        },
                    ),
                ], width=2),
            ]),
        ]),

        dcc.Loading(
            id="port-loading",
            type="default",
            color=COLORS["primary"],
            children=html.Div(id="port-plot-container"),
        ),

        html.Div(id="port-save-container", style={"display": "none"}, children=[
            html.Div(style=CARD_STYLE, children=[
                html.H5(
                    "Save Plots",
                    style={"color": COLORS["accent"], "marginBottom": "12px"},
                ),
                dbc.Row([
                    dbc.Col([
                        dbc.Input(
                            id="port-save-dir", type="text",
                            placeholder=r"Save directory  e.g.  C:\scratch\figs",
                            className="bg-dark text-light border-secondary",
                        ),
                    ], width=8),
                    dbc.Col([
                        dbc.Button(
                            "Save All Images",
                            id="port-save-btn",
                            color="success",
                            className="w-100",
                        ),
                    ], width=2),
                    dbc.Col(html.Div(id="port-save-status"), width=2),
                ]),
            ]),
        ]),
    ])


def _freq_plot_tab() -> html.Div:
    return html.Div([
        html.Div(style=CARD_STYLE, children=[
            html.H4(
                "1D Frequency Plot Configuration",
                style={"color": COLORS["accent"], "marginBottom": "16px"},
            ),
            dbc.Row([
                dbc.Col([
                    _label("File Type"),
                    dcc.Dropdown(
                        id="freq-file-type-dd",
                        options=[{"label": ft, "value": ft} for ft in FILE_TYPES],
                        value="OP",
                        clearable=False,
                    ),
                ], width=2),
                dbc.Col([
                    _label("Variable"),
                    dcc.Dropdown(
                        id="freq-depvar-dd",
                        options=[
                            {"label": "Gain", "value": "gain"},
                            {"label": "Phase", "value": "phase"},
                        ],
                        value="gain",
                        clearable=False,
                    ),
                ], width=2),
                dbc.Col([
                    _label("Setpoint [GHz]"),
                    dcc.Dropdown(
                        id="freq-setpoint-dd",
                        options=[],
                        placeholder="Load data first\u2026",
                        clearable=False,
                    ),
                ], width=2),
                dbc.Col([
                    _label("Port Number(s)"),
                    dbc.Input(
                        id="freq-ports-input", type="text",
                        placeholder="e.g.  1,5,10  or  1-10",
                        className="bg-dark text-light border-secondary",
                    ),
                ], width=2),
                dbc.Col([
                    _label("Spread Type"),
                    dcc.Dropdown(
                        id="freq-spread-dd",
                        options=[
                            {"label": "Std Dev", "value": "STD"},
                            {"label": "IQR", "value": "IQR"},
                            {"label": "Min-Max", "value": "MinMax"},
                        ],
                        value="IQR",
                        clearable=False,
                    ),
                ], width=2),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([
                    _label("Y-axis Limits (Auto default)"),
                    dbc.InputGroup([
                        dbc.Input(
                            id="freq-ylim-min", type="number",
                            placeholder="Auto (min)",
                            className="bg-dark text-light border-secondary",
                            size="sm",
                        ),
                        dbc.Input(
                            id="freq-ylim-max", type="number",
                            placeholder="Auto (max)",
                            className="bg-dark text-light border-secondary",
                            size="sm",
                        ),
                    ], size="sm"),
                ], width=2),
                dbc.Col([
                    _label("Spread Y Limits (Auto default)"),
                    dbc.InputGroup([
                        dbc.Input(
                            id="freq-sylim-min", type="number",
                            placeholder="Auto (min)",
                            className="bg-dark text-light border-secondary",
                            size="sm",
                        ),
                        dbc.Input(
                            id="freq-sylim-max", type="number",
                            placeholder="Auto (max)",
                            className="bg-dark text-light border-secondary",
                            size="sm",
                        ),
                    ], size="sm"),
                ], width=2),
                dbc.Col([
                    _label("Iteration"),
                    dcc.Dropdown(
                        id="freq-iteration-dd",
                        options=[],
                        value=1,
                        clearable=False,
                    ),
                ], width=1),
                dbc.Col(width=3),
                dbc.Col([
                    _label("\u00A0"),
                    dbc.Button(
                        "Generate",
                        id="freq-generate-btn",
                        color="primary",
                        className="w-100",
                        style={
                            "backgroundColor": COLORS["primary"],
                            "border": "none",
                        },
                    ),
                ], width=2),
            ]),
        ]),

        dcc.Loading(
            id="freq-loading",
            type="default",
            color=COLORS["primary"],
            children=html.Div(id="freq-plot-container"),
        ),

        html.Div(id="freq-save-container", style={"display": "none"}, children=[
            html.Div(style=CARD_STYLE, children=[
                html.H5(
                    "Save Plots",
                    style={"color": COLORS["accent"], "marginBottom": "12px"},
                ),
                dbc.Row([
                    dbc.Col([
                        dbc.Input(
                            id="freq-save-dir", type="text",
                            placeholder=r"Save directory  e.g.  C:\scratch\figs",
                            className="bg-dark text-light border-secondary",
                        ),
                    ], width=8),
                    dbc.Col([
                        dbc.Button(
                            "Save All Images",
                            id="freq-save-btn",
                            color="success",
                            className="w-100",
                        ),
                    ], width=2),
                    dbc.Col(html.Div(id="freq-save-status"), width=2),
                ]),
            ]),
        ]),
    ])


def _stats_tab() -> html.Div:
    return html.Div([
        html.Div(style=CARD_STYLE, children=[
            html.H4(
                "Patch Map Statistics",
                style={"color": COLORS["accent"], "marginBottom": "16px"},
            ),
            dbc.Row([
                dbc.Col([
                    _label("File Type"),
                    dcc.Dropdown(
                        id="stats-file-type-dd",
                        options=[{"label": ft, "value": ft} for ft in FILE_TYPES],
                        value="OP",
                        clearable=False,
                    ),
                ], width=2),
                dbc.Col([
                    _label("Variable"),
                    dcc.Dropdown(
                        id="stats-depvar-dd",
                        options=[
                            {"label": "Gain", "value": "gain"},
                            {"label": "Phase", "value": "phase"},
                        ],
                        value="gain",
                        clearable=False,
                    ),
                ], width=2),
                dbc.Col([
                    _label("Frequency [GHz]"),
                    dcc.Dropdown(
                        id="stats-freq-dd",
                        options=[],
                        placeholder="Load data first\u2026",
                        clearable=False,
                    ),
                ], width=2),
                dbc.Col([
                    _label("Iteration"),
                    dcc.Dropdown(
                        id="stats-iteration-dd",
                        options=[],
                        value=1,
                        clearable=False,
                    ),
                ], width=1),
                dbc.Col([
                    _label("Spread Type"),
                    dcc.Dropdown(
                        id="stats-spread-dd",
                        options=[
                            {"label": "Std Dev", "value": "STD"},
                            {"label": "IQR", "value": "IQR"},
                            {"label": "Min-Max", "value": "MinMax"},
                        ],
                        value="STD",
                        clearable=False,
                    ),
                ], width=2),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([
                    _label("\u00A0"),
                    dbc.Checklist(
                        id="stats-align-chk",
                        options=[{
                            "label": " Align (mcr_file_stats / lens_rotation)",
                            "value": "align",
                        }],
                        value=["align"],
                        inline=True,
                        style={"paddingTop": "2px"},
                        labelStyle={"color": COLORS["text"]},
                    ),
                ], width=3),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([
                    _label("Avg Colour Limits (Auto default)"),
                    dbc.InputGroup([
                        dbc.Input(
                            id="stats-avg-min", type="number",
                            placeholder="Auto (min)",
                            className="bg-dark text-light border-secondary",
                            size="sm",
                        ),
                        dbc.Input(
                            id="stats-avg-max", type="number",
                            placeholder="Auto (max)",
                            className="bg-dark text-light border-secondary",
                            size="sm",
                        ),
                    ], size="sm"),
                ], width=2),
                dbc.Col([
                    _label("Spread Colour Limits (Auto default)"),
                    dbc.InputGroup([
                        dbc.Input(
                            id="stats-spread-min", type="number",
                            placeholder="Auto (min)",
                            className="bg-dark text-light border-secondary",
                            size="sm",
                        ),
                        dbc.Input(
                            id="stats-spread-max", type="number",
                            placeholder="Auto (max)",
                            className="bg-dark text-light border-secondary",
                            size="sm",
                        ),
                    ], size="sm"),
                ], width=2),
                dbc.Col(width=4),
                dbc.Col([
                    _label("\u00A0"),
                    dbc.Button(
                        "Generate",
                        id="stats-generate-btn",
                        color="primary",
                        className="w-100",
                        style={
                            "backgroundColor": COLORS["primary"],
                            "border": "none",
                        },
                    ),
                ], width=2),
            ]),
        ]),

        dcc.Loading(
            id="stats-loading",
            type="default",
            color=COLORS["primary"],
            children=html.Div(id="stats-plot-container"),
        ),

        # Port histogram section
        html.Div(style=CARD_STYLE, children=[
            html.H5(
                "Port Histogram",
                style={"color": COLORS["accent"], "marginBottom": "12px"},
            ),
            html.P(
                "Generate the patch map first. Then enter a port to plot "
                "2×2 histograms (H/V × Beam 1 / Beam 2) at the stats frequency.",
                style={"color": COLORS["text_muted"], "fontSize": "13px",
                        "marginBottom": "12px"},
            ),
            dbc.Row([
                dbc.Col([
                    _label("Port number (odd = H, even = V for same feed)"),
                    dbc.Input(
                        id="stats-hist-port", type="number",
                        placeholder="e.g. 1",
                        className="bg-dark text-light border-secondary",
                        min=1, step=1,
                    ),
                ], width=2),
                dbc.Col([
                    _label("\u00A0"),
                    dbc.Button(
                        "Generate Histogram",
                        id="stats-hist-btn",
                        color="primary",
                        style={
                            "backgroundColor": COLORS["primary"],
                            "border": "none",
                        },
                    ),
                ], width=2),
            ]),
            html.Div(id="stats-histogram-container", style={"marginTop": "12px"}),
        ]),

        html.Div(id="stats-save-container", style={"display": "none"}, children=[
            html.Div(style=CARD_STYLE, children=[
                html.H5(
                    "Save Plots",
                    style={"color": COLORS["accent"], "marginBottom": "12px"},
                ),
                dbc.Row([
                    dbc.Col([
                        dbc.Input(
                            id="stats-save-dir", type="text",
                            placeholder=r"Save directory  e.g.  C:\scratch\figs",
                            className="bg-dark text-light border-secondary",
                        ),
                    ], width=8),
                    dbc.Col([
                        dbc.Button(
                            "Save All Images",
                            id="stats-save-btn",
                            color="success",
                            className="w-100",
                        ),
                    ], width=2),
                    dbc.Col(html.Div(id="stats-save-status"), width=2),
                ]),
            ]),
        ]),
    ])


def _docs_tab() -> html.Div:
    version_items = []
    for ver in sorted(CHANGELOG.keys(), reverse=True):
        items = CHANGELOG[ver]
        version_items.append(
            html.Div(style={"marginBottom": "20px"}, children=[
                html.H5(
                    f"Version {ver}",
                    style={"color": COLORS["primary"], "marginBottom": "8px"},
                ),
                html.Ul(
                    [html.Li(item, style={"color": COLORS["text"], "marginBottom": "4px"})
                     for item in items],
                    style={"paddingLeft": "20px"},
                ),
            ])
        )

    return html.Div([
        html.Div(style=CARD_STYLE, children=[
            html.H4(
                "Documentation",
                style={"color": COLORS["accent"], "marginBottom": "16px"},
            ),

            html.H5(
                "How to Run",
                style={"color": COLORS["primary"], "marginBottom": "8px"},
            ),
            html.Pre(
                "python app.py\n"
                "# Then open http://127.0.0.1:8050 in a browser",
                style={
                    "backgroundColor": COLORS["plot_bg"],
                    "padding": "12px",
                    "borderRadius": "6px",
                    "color": COLORS["text"],
                    "fontSize": "13px",
                },
            ),

            html.H5(
                "Architecture",
                style={"color": COLORS["primary"], "margin": "20px 0 8px"},
            ),
            html.Pre(
                "app.py                  \u2190 Entry point (Dash server, diskcache long callbacks)\n"
                "tlm_glass/\n"
                "  \u251C\u2500 config.py              \u2190 Theme, constants, version\n"
                "  \u251C\u2500 geometry_transforms.py \u2190 lens_rotation / xy_clockwise (mcr_file_stats parity)\n"
                "  \u251C\u2500 parser.py              \u2190 File discovery, CSV parsing, geometry cache\n"
                "  \u251C\u2500 plots.py               \u2190 Plotly figure generation\n"
                "  \u251C\u2500 dashboard.py           \u2190 Dash layout and callbacks\n"
                "  \u2514\u2500 geometry/              \u2190 Bundled array geometry CSVs\n"
                "assets/\n"
                "  \u2514\u2500 style.css              \u2190 Dark theme CSS overrides\n"
                ".dash_cache/              \u2190 Background callback job store (gitignored)\n"
                "requirements.txt        \u2190 Python dependencies",
                style={
                    "backgroundColor": COLORS["plot_bg"],
                    "padding": "12px",
                    "borderRadius": "6px",
                    "color": COLORS["text"],
                    "fontSize": "13px",
                    "lineHeight": "1.6",
                },
            ),

            html.H5(
                "Data Flow",
                style={"color": COLORS["primary"], "margin": "20px 0 8px"},
            ),
            html.Ol([
                html.Li("User provides a root TLM directory on the Data tab (paste path)."),
                html.Li(
                    "Load Data runs parser.discover_files() in a background callback "
                    "with a live progress bar, then stores the file index in dcc.Store."
                ),
                html.Li(
                    "Optional: Build DataFrame reads every indexed CSV and collates "
                    "gain/phase at each setpoint (also background + progress). "
                    "Downloads are explicit button actions only."
                ),
                html.Li(
                    "Plot tabs filter the index; parser.get_file_data caches parsed CSVs."
                ),
                html.Li(
                    "Statistics patch maps use the same merged geometry and "
                    "lens_rotation convention as mcr_file_stats.py when Align is on."
                ),
                html.Li(
                    "Histogram selections are stored in stats-context-store so they "
                    "survive in single-worker deployments."
                ),
                html.Li(
                    "Figures can be exported as PNG to a user-specified directory."
                ),
            ], style={
                "paddingLeft": "20px",
                "color": COLORS["text"],
                "lineHeight": "1.8",
            }),
        ]),

        html.Div(style=CARD_STYLE, children=[
            html.H4(
                "Version History",
                style={"color": COLORS["accent"], "marginBottom": "16px"},
            ),
            *version_items,
        ]),
    ])


def _dev_tab() -> html.Div:
    items = [
        "Tx TLM combiner support",
        "Multi-iteration comparison and overlay",
        "Status log metadata parsing and display",
        "SEC file temperature and power correlation analysis",
        "Batch export of statistics to CSV / Excel",
        "Golden board comparison (median reference)",
        "Port failure detection and highlighting",
        "Summary CSV error log integration",
        "Rx TLM support",
        "Multi-TLM overlay by serial number",
        "Full-spectrum results export (all frequencies)",
    ]
    return html.Div([
        html.Div(style=CARD_STYLE, children=[
            html.H4(
                "Further Development",
                style={"color": COLORS["accent"], "marginBottom": "16px"},
            ),
            html.P(
                "Planned features and enhancements for future releases:",
                style={"color": COLORS["text_muted"], "marginBottom": "16px"},
            ),
            html.Ol(
                [
                    html.Li(
                        item,
                        style={"marginBottom": "8px", "color": COLORS["text"]},
                    )
                    for item in items
                ],
                style={"paddingLeft": "20px"},
            ),
        ]),
    ])


# ===================================================================
# Callbacks
# ===================================================================

def register_callbacks(app: Dash) -> None:
    """Register all Dash callbacks with the application."""

    # --- Tab switching (show / hide pre-rendered tabs) ---------------

    _tab_ids = [
        "data-tab-content", "port-tab-content", "freq-tab-content",
        "stats-tab-content", "docs-tab-content", "dev-tab-content",
    ]
    _tab_values = [
        "data-tab", "port-tab", "freq-tab",
        "stats-tab", "docs-tab", "dev-tab",
    ]

    @app.callback(
        [Output(tid, "style") for tid in _tab_ids],
        Input("main-tabs", "value"),
    )
    def switch_tab(tab):
        hidden = {"display": "none"}
        visible = {"display": "block"}
        return [visible if tab == tv else hidden for tv in _tab_values]

    _prog_hide = {"display": "none", "marginTop": "12px"}
    _prog_show = {"display": "block", "marginTop": "12px"}

    # --- Data loading (background + progress) ------------------------

    @app.callback(
        output=[
            Output("data-store", "data"),
            Output("load-indicator", "children"),
            Output("load-summary", "children"),
            Output("full-results-store", "data", allow_duplicate=True),
        ],
        inputs=[Input("load-data-btn", "n_clicks")],
        state=[State("data-path-input", "value")],
        progress=[
            Output("load-progress", "value"),
            Output("load-progress-text", "children"),
        ],
        running=[
            (Output("load-data-btn", "disabled"), True, False),
            (Output("load-progress-wrap", "style"), _prog_show, _prog_hide),
        ],
        background=True,
        prevent_initial_call=True,
    )
    def load_data(set_progress, n_clicks, path):
        if not path or not str(path).strip():
            set_progress((0, ""))
            return (
                no_update,
                _indicator("warning", "Enter a directory path"),
                no_update,
                no_update,
            )

        try:
            parser.clear_cache()
            set_progress((1, "Validating path and preparing scan\u2026"))

            def hook(pct: int, msg: str) -> None:
                set_progress((max(0, min(100, pct)), msg))

            df = parser.discover_files(str(path).strip(), progress_hook=hook)
            if df.empty:
                set_progress((0, ""))
                return (
                    no_update,
                    _indicator("danger", "No files found"),
                    no_update,
                    no_update,
                )

            store_data = df.to_json(date_format="iso", orient="split")

            n_tlms = df["qr"].nunique()
            n_files = len(df)
            freqs = sorted(df["setpoint"].unique())
            freq_str = ", ".join(f"{f:.2f}" for f in freqs)
            file_types_str = ", ".join(sorted(df["file_type"].unique()))

            summary = dbc.Row([
                dbc.Col([
                    html.Div(
                        style={"display": "flex", "alignItems": "center"},
                        children=[
                            html.I(
                                className="bi bi-database-fill",
                                style={
                                    "fontSize": "28px",
                                    "color": COLORS["primary"],
                                },
                            ),
                            html.Div(
                                style={"marginLeft": "12px"},
                                children=[
                                    html.H6(
                                        f"{n_tlms} TLMs  \u2022  {n_files} files",
                                        style={"margin": "0"},
                                    ),
                                ],
                            ),
                        ],
                    ),
                ], width=3),
                dbc.Col([
                    html.Small(
                        "Frequencies [GHz]",
                        style={"color": COLORS["text_muted"]},
                    ),
                    html.P(
                        freq_str,
                        style={"margin": "0", "fontSize": "13px"},
                    ),
                ], width=4),
                dbc.Col([
                    html.Small(
                        "File Types",
                        style={"color": COLORS["text_muted"]},
                    ),
                    html.P(
                        file_types_str,
                        style={"margin": "0", "fontSize": "13px"},
                    ),
                ], width=3),
            ])

            set_progress((100, "Complete."))
            return (
                store_data,
                _indicator(
                    "success",
                    f"Loaded \u2014 {n_files} files from {n_tlms} TLMs",
                ),
                summary,
                None,
            )

        except Exception as exc:
            set_progress((0, ""))
            return (
                no_update,
                _indicator("danger", f"Error: {exc}"),
                no_update,
                no_update,
            )

    @app.callback(
        Output("load-indicator", "children", allow_duplicate=True),
        Input("load-data-btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def set_loading_indicator_immediate(n_clicks):
        """Show immediate feedback while the background load starts."""
        if not n_clicks:
            return no_update
        return _indicator("warning", "Loading\u2026")

    # --- Enable/disable download buttons based on data availability ---

    @app.callback(
        Output("download-index-btn", "disabled"),
        Output("build-full-btn", "disabled"),
        Output("index-indicator", "children"),
        Input("data-store", "data"),
    )
    def toggle_data_buttons(store_data):
        has_data = bool(store_data)
        if has_data:
            ind = _indicator("success", "Ready")
        else:
            ind = html.Span(
                "\u25CF",
                style={"color": COLORS["border"], "fontSize": "18px"},
            )
        return not has_data, not has_data, ind

    @app.callback(
        Output("download-full-csv-btn", "disabled"),
        Input("full-results-store", "data"),
    )
    def toggle_csv_button(full_data):
        return not bool(full_data)

    @app.callback(
        Output("pipeline-checklist", "children"),
        Input("data-store", "data"),
        Input("full-results-store", "data"),
    )
    def render_pipeline_checklist(store_idx, store_full):
        def row(done: bool, label: str) -> html.Div:
            mark = "\u2713" if done else "\u25CB"
            colour = COLORS["success"] if done else COLORS["border"]
            return html.Div(
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "gap": "10px",
                    "marginBottom": "6px",
                },
                children=[
                    html.Span(
                        mark,
                        style={"color": colour, "fontSize": "16px", "width": "18px"},
                    ),
                    html.Span(label, style={"color": COLORS["text"], "fontSize": "13px"}),
                ],
            )

        return html.Div([
            html.Small(
                "Pipeline",
                style={"color": COLORS["text_muted"], "display": "block",
                        "marginBottom": "8px"},
            ),
            row(bool(store_idx), "File index loaded (ready for plots and exports)"),
            row(bool(store_full), "Full results DataFrame built (CSV download enabled)"),
        ])

    # --- Download index CSV ------------------------------------------

    @app.callback(
        Output("download-index", "data"),
        Input("download-index-btn", "n_clicks"),
        State("data-store", "data"),
        prevent_initial_call=True,
    )
    def download_index(n_clicks, store_data):
        if not store_data:
            return no_update
        df = pd.read_json(store_data, orient="split")
        return dcc.send_data_frame(df.to_csv, "tlm_file_index.csv", index=False)

    # --- Build full results DataFrame (background + progress) --------

    @app.callback(
        output=[
            Output("full-results-store", "data"),
            Output("full-results-status", "children"),
        ],
        inputs=[Input("build-full-btn", "n_clicks")],
        state=[State("data-store", "data")],
        progress=[
            Output("build-progress", "value"),
            Output("build-progress-text", "children"),
        ],
        running=[
            (Output("build-full-btn", "disabled"), True, False),
            (Output("build-progress-wrap", "style"), _prog_show, _prog_hide),
        ],
        background=True,
        prevent_initial_call=True,
    )
    def build_full_results(set_progress, n_clicks, store_data):
        if not store_data:
            set_progress((0, ""))
            return no_update, _status_badge("Load data first", "warning")

        try:
            df_index = pd.read_json(store_data, orient="split")

            def hook(pct: int, msg: str) -> None:
                set_progress((max(0, min(100, pct)), msg))

            set_progress((0, "Reading measurement files\u2026"))
            df_full = parser.build_full_results(df_index, progress_hook=hook)
            if df_full.empty:
                set_progress((0, ""))
                return no_update, _status_badge("No results to export", "warning")

            set_progress((100, "Complete."))
            return (
                df_full.to_json(date_format="iso", orient="split"),
                _status_badge(
                    f"Built DataFrame with {len(df_full):,} rows", "success"
                ),
            )
        except Exception as exc:
            set_progress((0, ""))
            return no_update, _status_badge(f"Build failed: {exc}", "danger")

    # --- Download full results (CSV) ---------------------------------

    @app.callback(
        Output("download-full-results", "data"),
        Input("download-full-csv-btn", "n_clicks"),
        State("full-results-store", "data"),
        prevent_initial_call=True,
    )
    def download_full_results_csv(n_clicks, full_results_data):
        if not full_results_data:
            return no_update
        df_full = pd.read_json(full_results_data, orient="split")
        return dcc.send_data_frame(df_full.to_csv, "tlm_full_results.csv", index=False)

    # --- Populate port-plot dropdowns --------------------------------

    @app.callback(
        Output("port-freq-dd", "options"),
        Output("port-iteration-dd", "options"),
        Output("port-iteration-dd", "value"),
        Input("data-store", "data"),
    )
    def update_port_dropdowns(store_data):
        if not store_data:
            return [], [], no_update
        df = pd.read_json(store_data, orient="split")
        freqs = sorted(df["setpoint"].unique())
        freq_opts = [{"label": f"{f:.2f} GHz", "value": f} for f in freqs]
        iters = sorted(df["iteration"].unique())
        iter_opts = [{"label": f"Iteration {i}", "value": i} for i in iters]
        default_iter = 1 if 1 in iters else (iters[0] if iters else no_update)
        return freq_opts, iter_opts, default_iter

    # --- Populate freq-plot dropdowns --------------------------------

    @app.callback(
        Output("freq-setpoint-dd", "options"),
        Output("freq-iteration-dd", "options"),
        Output("freq-iteration-dd", "value"),
        Input("data-store", "data"),
    )
    def update_freq_dropdowns(store_data):
        if not store_data:
            return [], [], no_update
        df = pd.read_json(store_data, orient="split")
        freqs = sorted(df["setpoint"].unique())
        freq_opts = [{"label": "Segmented", "value": "Segmented"}]
        freq_opts += [{"label": f"{f:.2f} GHz", "value": f} for f in freqs]
        iters = sorted(df["iteration"].unique())
        iter_opts = [{"label": f"Iteration {i}", "value": i} for i in iters]
        default_iter = 1 if 1 in iters else (iters[0] if iters else no_update)
        return freq_opts, iter_opts, default_iter

    # --- Populate stats dropdowns ------------------------------------

    @app.callback(
        Output("stats-freq-dd", "options"),
        Output("stats-iteration-dd", "options"),
        Output("stats-iteration-dd", "value"),
        Input("data-store", "data"),
    )
    def update_stats_dropdowns(store_data):
        if not store_data:
            return [], [], no_update
        df = pd.read_json(store_data, orient="split")
        freqs = sorted(df["setpoint"].unique())
        freq_opts = [{"label": f"{f:.2f} GHz", "value": f} for f in freqs]
        iters = sorted(df["iteration"].unique())
        iter_opts = [{"label": f"Iteration {i}", "value": i} for i in iters]
        default_iter = 1 if 1 in iters else (iters[0] if iters else no_update)
        return freq_opts, iter_opts, default_iter

    # --- Generate port plots -----------------------------------------

    @app.callback(
        Output("port-plot-container", "children"),
        Output("port-save-container", "style"),
        Input("port-generate-btn", "n_clicks"),
        State("port-file-type-dd", "value"),
        State("port-depvar-dd", "value"),
        State("port-freq-dd", "value"),
        State("port-spread-dd", "value"),
        State("port-ylim-min", "value"),
        State("port-ylim-max", "value"),
        State("port-sylim-min", "value"),
        State("port-sylim-max", "value"),
        State("port-iteration-dd", "value"),
        State("data-store", "data"),
        prevent_initial_call=True,
    )
    def generate_port_plots(
        n_clicks, file_type, depvar, frequencies, spread_type,
        y_min, y_max, sy_min, sy_max, iteration, store_data,
    ):
        if not store_data or not frequencies:
            return (
                [_placeholder("Select frequencies and ensure data is loaded.")],
                {"display": "none"},
            )

        df = pd.read_json(store_data, orient="split")
        y_lims = _make_lims(y_min, y_max)
        spread_lims = _make_lims(sy_min, sy_max)

        if not isinstance(frequencies, list):
            frequencies = [frequencies]

        _port_figure_cache.clear()
        children: list = []

        for freq in frequencies:
            mask = (
                (df["file_type"] == file_type)
                & (df["setpoint"] == freq)
                & (df["iteration"] == iteration)
            )
            files_b1 = df[mask & (df["beam"] == 1)]["file_path"].tolist()
            files_b2 = df[mask & (df["beam"] == 2)]["file_path"].tolist()
            if not files_b1 and not files_b2:
                continue

            fig = plots.create_port_figure(
                files_b1, files_b2, depvar, freq,
                spread_type, y_lims, spread_lims,
            )
            _port_figure_cache[f"{freq:.2f}"] = fig

        n_figs = len(_port_figure_cache)
        if n_figs == 0:
            return (
                [_placeholder("No matching files found for the selected parameters.")],
                {"display": "none"},
            )

        if n_figs >= MAX_INLINE_PLOTS:
            children.append(_too_many_alert(n_figs))
        else:
            for key, fig in _port_figure_cache.items():
                children.append(
                    dcc.Graph(
                        figure=fig,
                        style={"height": "680px", "marginBottom": "16px"},
                        config={"toImageButtonOptions": {"format": "png", "scale": 2}},
                    )
                )

        return children, {"display": "block"}

    # --- Generate frequency plots ------------------------------------

    @app.callback(
        Output("freq-plot-container", "children"),
        Output("freq-save-container", "style"),
        Input("freq-generate-btn", "n_clicks"),
        State("freq-file-type-dd", "value"),
        State("freq-depvar-dd", "value"),
        State("freq-setpoint-dd", "value"),
        State("freq-ports-input", "value"),
        State("freq-spread-dd", "value"),
        State("freq-ylim-min", "value"),
        State("freq-ylim-max", "value"),
        State("freq-sylim-min", "value"),
        State("freq-sylim-max", "value"),
        State("freq-iteration-dd", "value"),
        State("data-store", "data"),
        prevent_initial_call=True,
    )
    def generate_freq_plots(
        n_clicks, file_type, depvar, setpoint, ports_str, spread_type,
        y_min, y_max, sy_min, sy_max, iteration, store_data,
    ):
        if not store_data or setpoint is None or not ports_str:
            return (
                [_placeholder("Select a setpoint and enter port number(s).")],
                {"display": "none"},
            )

        df = pd.read_json(store_data, orient="split")
        y_lims = _make_lims(y_min, y_max)
        spread_lims = _make_lims(sy_min, sy_max)

        port_numbers = _parse_port_input(ports_str)
        if not port_numbers:
            return (
                [_placeholder("Invalid port input.  Use e.g. '1,5,10' or '1-10'.")],
                {"display": "none"},
            )

        _freq_figure_cache.clear()
        children: list = []

        is_segmented = (setpoint == "Segmented")

        if is_segmented:
            all_setpoints = sorted(df["setpoint"].unique())

            for port in port_numbers:
                fps_b1: dict[float, list[str]] = {}
                fps_b2: dict[float, list[str]] = {}
                for sp in all_setpoints:
                    mask = (
                        (df["file_type"] == file_type)
                        & (df["setpoint"] == sp)
                        & (df["iteration"] == iteration)
                    )
                    fps_b1[sp] = df[mask & (df["beam"] == 1)]["file_path"].tolist()
                    fps_b2[sp] = df[mask & (df["beam"] == 2)]["file_path"].tolist()

                fig = plots.create_segmented_freq_figure(
                    fps_b1, fps_b2, depvar, port,
                    spread_type, y_lims, spread_lims,
                )
                _freq_figure_cache[f"seg_port{port}"] = fig
        else:
            setpoint_val = float(setpoint)
            mask = (
                (df["file_type"] == file_type)
                & (df["setpoint"] == setpoint_val)
                & (df["iteration"] == iteration)
            )
            files_b1 = df[mask & (df["beam"] == 1)]["file_path"].tolist()
            files_b2 = df[mask & (df["beam"] == 2)]["file_path"].tolist()

            if not files_b1 and not files_b2:
                return (
                    [_placeholder("No matching files found.")],
                    {"display": "none"},
                )

            for port in port_numbers:
                fig = plots.create_freq_figure(
                    files_b1, files_b2, depvar, port,
                    spread_type, y_lims, spread_lims,
                )
                _freq_figure_cache[f"port{port}"] = fig

        n_figs = len(_freq_figure_cache)
        if n_figs == 0:
            return (
                [_placeholder("No matching files found.")],
                {"display": "none"},
            )

        if n_figs >= MAX_INLINE_PLOTS:
            children.append(_too_many_alert(n_figs))
        else:
            for key, fig in _freq_figure_cache.items():
                children.append(
                    dcc.Graph(
                        figure=fig,
                        style={"height": "680px", "marginBottom": "16px"},
                        config={"toImageButtonOptions": {"format": "png", "scale": 2}},
                    )
                )

        return children, {"display": "block"}

    # --- Generate statistics patch map -------------------------------

    @app.callback(
        Output("stats-plot-container", "children"),
        Output("stats-save-container", "style"),
        Output("stats-context-store", "data"),
        Input("stats-generate-btn", "n_clicks"),
        State("stats-file-type-dd", "value"),
        State("stats-depvar-dd", "value"),
        State("stats-freq-dd", "value"),
        State("stats-iteration-dd", "value"),
        State("stats-spread-dd", "value"),
        State("stats-align-chk", "value"),
        State("stats-avg-min", "value"),
        State("stats-avg-max", "value"),
        State("stats-spread-min", "value"),
        State("stats-spread-max", "value"),
        State("data-store", "data"),
        prevent_initial_call=True,
    )
    def generate_stats(
        n_clicks, file_type, depvar, frequency, iteration,
        spread_type, align_val, avg_min, avg_max, sp_min, sp_max,
        store_data,
    ):
        if not store_data or frequency is None:
            return (
                [_placeholder(
                    "Select a frequency and ensure data is loaded."
                )],
                {"display": "none"},
                None,
            )

        df = pd.read_json(store_data, orient="split")
        frequency_val = float(frequency)
        align_coords = "align" in (align_val or [])
        avg_lims = _make_lims(avg_min, avg_max)
        spread_lims = _make_lims(sp_min, sp_max)

        mask = (
            (df["file_type"] == file_type)
            & (df["setpoint"] == frequency_val)
            & (df["iteration"] == iteration)
        )
        files_b1 = df[mask & (df["beam"] == 1)]["file_path"].tolist()
        files_b2 = df[mask & (df["beam"] == 2)]["file_path"].tolist()

        if not files_b1 and not files_b2:
            return (
                [_placeholder("No matching files found.")],
                {"display": "none"},
                None,
            )

        fig = plots.create_patch_map_figure(
            files_b1, files_b2, depvar, frequency_val,
            spread_type, avg_lims, spread_lims, align_coords,
        )

        _stats_figure_cache.clear()
        _stats_figure_cache["patch_map"] = fig

        ref_fp = files_b1[0] if files_b1 else files_b2[0]
        max_ports = int(parser.get_file_data(ref_fp)["gain"].shape[0])
        stats_ctx = {
            "files_b1": files_b1,
            "files_b2": files_b2,
            "depvar": depvar,
            "frequency": frequency_val,
            "max_ports": max_ports,
        }

        graph = dcc.Graph(
            id="stats-patch-graph",
            figure=fig,
            style={"height": "1400px", "marginBottom": "16px"},
            config={"toImageButtonOptions": {"format": "png", "scale": 2}},
        )

        return [graph], {"display": "block"}, stats_ctx

    # --- Port histogram (explicit port input) ------------------------

    @app.callback(
        Output("stats-histogram-container", "children"),
        Input("stats-hist-btn", "n_clicks"),
        State("stats-hist-port", "value"),
        State("stats-context-store", "data"),
        prevent_initial_call=True,
    )
    def generate_port_histogram(n_clicks, port_number, stats_ctx):
        if not stats_ctx or port_number is None:
            return _placeholder(
                "Generate the patch map first, then enter a port number."
            )

        port_number = int(port_number)
        max_ports = int(stats_ctx.get("max_ports", 1))
        if port_number < 1 or port_number > max_ports:
            return _placeholder(f"Port number must be between 1 and {max_ports}.")

        try:
            fig = plots.create_port_histogram(
                stats_ctx["files_b1"],
                stats_ctx["files_b2"],
                stats_ctx["depvar"],
                float(stats_ctx["frequency"]),
                port_number,
                max_ports=max_ports,
            )
        except Exception as exc:
            return dbc.Alert(
                f"Histogram generation failed: {exc}",
                color="warning",
                className="mt-2",
            )

        return dcc.Graph(
            figure=fig,
            style={"height": "540px"},
            config={"toImageButtonOptions": {"format": "png", "scale": 2}},
        )

    @app.callback(
        Output("stats-context-store", "data", allow_duplicate=True),
        Input("data-store", "data"),
        prevent_initial_call=True,
    )
    def clear_stats_context_on_new_index(_store_data):
        """Invalidate histogram file lists when the file index changes."""
        return None

    # --- Save port plots ---------------------------------------------

    @app.callback(
        Output("port-save-status", "children"),
        Input("port-save-btn", "n_clicks"),
        State("port-save-dir", "value"),
        prevent_initial_call=True,
    )
    def save_port_plots(n_clicks, save_dir):
        return _save_figures(_port_figure_cache, save_dir, "port")

    # --- Save freq plots ---------------------------------------------

    @app.callback(
        Output("freq-save-status", "children"),
        Input("freq-save-btn", "n_clicks"),
        State("freq-save-dir", "value"),
        prevent_initial_call=True,
    )
    def save_freq_plots(n_clicks, save_dir):
        return _save_figures(_freq_figure_cache, save_dir, "freq")

    # --- Save stats plots --------------------------------------------

    @app.callback(
        Output("stats-save-status", "children"),
        Input("stats-save-btn", "n_clicks"),
        State("stats-save-dir", "value"),
        prevent_initial_call=True,
    )
    def save_stats_plots(n_clicks, save_dir):
        return _save_figures(_stats_figure_cache, save_dir, "stats")


# ===================================================================
# Helpers
# ===================================================================

def _label(text: str) -> html.Label:
    return html.Label(
        text,
        style={"color": COLORS["text_muted"], "fontSize": "13px"},
    )


def _indicator(variant: str, text: str = "") -> html.Span:
    """Small coloured circle + optional text for status indication."""
    color = {
        "success": COLORS["success"],
        "danger": COLORS["danger"],
        "warning": COLORS["warning"],
    }.get(variant, COLORS["border"])
    children = [
        html.Span(
            "\u25CF",
            style={"color": color, "fontSize": "18px", "marginRight": "6px"},
        ),
    ]
    if text:
        children.append(
            html.Span(text, style={"color": color, "fontSize": "13px"}),
        )
    return html.Span(
        style={"display": "inline-flex", "alignItems": "center"},
        children=children,
    )


def _status_badge(text: str, variant: str) -> html.Div:
    color = {
        "success": COLORS["success"],
        "danger": COLORS["danger"],
        "warning": COLORS["warning"],
    }.get(variant, COLORS["text_muted"])
    icon = {
        "success": "bi-check-circle-fill",
        "danger": "bi-x-circle-fill",
        "warning": "bi-exclamation-triangle-fill",
    }.get(variant, "")
    return html.Div(
        style={"display": "flex", "alignItems": "center"},
        children=[
            html.I(
                className=f"bi {icon}",
                style={"color": color, "marginRight": "8px"},
            ),
            html.Span(text, style={"color": color}),
        ],
    )


def _placeholder(text: str) -> html.Div:
    return html.Div(
        text,
        style={
            "textAlign": "center",
            "color": COLORS["text_muted"],
            "padding": "60px 20px",
            "fontSize": "16px",
        },
    )


def _too_many_alert(n_plots: int) -> dbc.Alert:
    return dbc.Alert(
        [
            html.I(className="bi bi-exclamation-triangle-fill me-2"),
            html.Strong(f"{n_plots} plots generated.  "),
            "This exceeds the inline display limit.  "
            "Use the Save controls below to export images.",
        ],
        color="warning",
        className="mt-3",
    )


def _make_lims(lo, hi) -> list[float] | None:
    if lo is not None and hi is not None:
        return [lo, hi]
    return None


def _parse_port_input(text: str) -> list[int]:
    """
    Parse a port number input string into a sorted list of unique integers.

    Supports comma-separated values and ranges::

        '1,5,10'      -> [1, 5, 10]
        '1-10'        -> [1, 2, ..., 10]
        '1-5,10,20-25' -> [1, 2, 3, 4, 5, 10, 20, 21, ..., 25]
    """
    ports: list[int] = []
    for part in text.split(","):
        part = part.strip()
        if "-" in part:
            try:
                start, end = part.split("-", maxsplit=1)
                ports.extend(range(int(start), int(end) + 1))
            except ValueError:
                continue
        else:
            try:
                ports.append(int(part))
            except ValueError:
                continue
    return sorted(set(ports))


def _save_figures(cache: dict, save_dir: str | None, prefix: str) -> html.Div:
    """Save all cached figures as PNG images to *save_dir*."""
    if not save_dir:
        return _status_badge("Enter a save directory", "warning")
    if not cache:
        return _status_badge("No figures to save \u2013 generate first", "warning")

    try:
        os.makedirs(save_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        for key, fig in cache.items():
            filename = f"{timestamp}_{prefix}_{key}.png"
            fig.write_image(os.path.join(save_dir, filename), scale=2)
        return _status_badge(f"Saved {len(cache)} images", "success")
    except ImportError:
        return _status_badge(
            "Install 'kaleido' to enable image export  (pip install kaleido)",
            "danger",
        )
    except Exception as exc:
        return _status_badge(f"Save failed: {exc}", "danger")
