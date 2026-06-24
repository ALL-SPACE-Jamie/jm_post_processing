# -*- coding: utf-8 -*-
"""
TLM Glass - Theme configuration and constants.

Defines ALL.SPACE brand colours, plot styling, geometry references
and Dash component themes.

@author: jmitchell
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Version
# ---------------------------------------------------------------------------

VERSION = "1.0.0"

CHANGELOG = {
    "1.0.0": [
        "Renamed project to TLM Glass (new maintained repo)",
        "Data tab: background callbacks with real progress for index scan and full DataFrame build",
        "Pipeline state store for index vs full-export readiness",
        "Statistics: patch coordinates match mcr_file_stats / cal_utils.lens_rotation (-102.5° step)",
        "Statistics: RFIC boundary outlines per lens (aligned with reference script)",
        "Statistics: colorbars anchored to subplot domains; beam-specific boxplot legend labels",
        "Statistics: histogram context in dcc.Store; 2×2 H/V × Beam layout; port range from data",
        "Segmented frequency plot: extra measurement sample before each segment boundary",
        "Improved contrast for inputs and light-themed controls",
    ],
    "0.1": [
        "Initial release with data loading and recursive file discovery",
        "1D port plot (all traces, median, spread)",
        "1D frequency plot (all traces, median, spread)",
        "File index CSV download",
        "Further development roadmap",
    ],
    "0.2": [
        "Full results DataFrame export (Parquet / CSV)",
        "Segmented frequency plot option",
        "Statistics tab with interactive patch map visualisation",
        "Click-to-histogram on patch map (stretch goal)",
        "Documentation tab with version history and architecture",
        "Improved iteration selector labels",
        "Delta-pol toggle for patch maps",
    ],
    "0.3": [
        "Improved loading UX with step-by-step status feedback",
        "Button state management for data export workflow",
        "1D port plot rendering optimisation (batched WebGL traces)",
        "Segmented frequency plot includes overlap point from adjacent segment",
        "Statistics: polarisation selector (H / V / Average / ΔPol)",
        "Statistics: diamond markers match physical device geometry",
        "Statistics: port-input histogram replaces click-to-histogram",
        "Coordinate align toggle for patch map rotation",
        "Improved input text contrast for dark theme",
    ],
    "0.4": [
        "Data tab: 3-section layout with status indicators (blank/green/red)",
        "Download buttons disabled until data is loaded (no auto-downloads)",
        "Loading indicators use progress bars instead of spinning dots",
        "Statistics: per-lens rotation (each lens rotated around its own centre)",
        "Statistics: always shows H-pol and V-pol sections (4-row layout)",
        "Statistics: colorbars consistently placed beside each plot",
        "Statistics: lens legend visible for both Beam 1 and Beam 2",
        "Removed single-rotation TX_LENS_ROTATION_DEG in favour of CSV angles",
        "Improved text contrast in light input boxes",
    ],
}

# TX lens alignment angle [deg] for statistics patch maps (see mcr_file_stats.plot_stats_patches)
TX_STATS_LENS_ALIGN_ANGLE_DEG = -102.5

# ---------------------------------------------------------------------------
# Geometry file paths (bundled with the package)
# ---------------------------------------------------------------------------

GEOMETRY_DIR = Path(__file__).parent / "geometry"
TX_GEOMETRY_CSV = GEOMETRY_DIR / "Mrk1_S2000_TLM_TX_ArrayGeometry_V20062022_CalInfo.csv"
TX_RFIC_CSV = GEOMETRY_DIR / "MK1_TX_TLM_RFIC_Patch_Feed_Mapping.csv"
# ---------------------------------------------------------------------------
# ALL.SPACE brand colours
# ---------------------------------------------------------------------------
COLORS = {
    "background": "#0B1120",
    "card_bg": "#131C31",
    "sidebar": "#0F1729",
    "primary": "#00A3E0",
    "secondary": "#0077B6",
    "accent": "#48CAE4",
    "success": "#2ECC71",
    "danger": "#E74C3C",
    "warning": "#F39C12",
    "text": "#E8E8E8",
    "text_muted": "#8899AA",
    "border": "#1E2D45",
    "plot_bg": "#0D1B2A",
    "grid": "#1E2D45",
}

PLOT_COLORS = {
    "all_traces": "rgba(255, 255, 255, 0.15)",
    "average": "#00A3E0",
    "spread": "#E74C3C",
    "fill": "rgba(0, 163, 224, 0.3)",
}

SEGMENT_COLORS = [
    "#00A3E0", "#E74C3C", "#2ECC71", "#F39C12",
    "#9B59B6", "#1ABC9C", "#E67E22", "#3498DB",
]

PATCH_COLORSCALE = "Jet"

PLOTLY_LAYOUT_DEFAULTS = dict(
    paper_bgcolor=COLORS["card_bg"],
    plot_bgcolor=COLORS["plot_bg"],
    font=dict(color=COLORS["text"], family="Inter, Arial, sans-serif", size=12),
    margin=dict(l=60, r=20, t=50, b=50),
)

PLOTLY_AXIS_DEFAULTS = dict(
    gridcolor=COLORS["grid"],
    zerolinecolor=COLORS["grid"],
    linecolor=COLORS["border"],
)

TAB_STYLE = {
    "backgroundColor": COLORS["sidebar"],
    "color": COLORS["text_muted"],
    "border": "none",
    "borderBottom": "2px solid transparent",
    "padding": "12px 24px",
    "fontWeight": "500",
    "cursor": "pointer",
}

TAB_SELECTED_STYLE = {
    **TAB_STYLE,
    "backgroundColor": COLORS["background"],
    "color": COLORS["primary"],
    "borderBottom": f"2px solid {COLORS['primary']}",
    "fontWeight": "600",
}

CARD_STYLE = {
    "backgroundColor": COLORS["card_bg"],
    "border": f"1px solid {COLORS['border']}",
    "borderRadius": "8px",
    "padding": "20px",
    "marginBottom": "16px",
}

FILE_TYPES = ["OP", "RFA", "SEC", "UnclippedRfa"]

MAX_INLINE_PLOTS = 10
