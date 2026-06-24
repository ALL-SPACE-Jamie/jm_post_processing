# -*- coding: utf-8 -*-
"""
TLM Glass - Plotly figure generation.

Creates interactive 2x3 subplot figures for port-domain and
frequency-domain analysis of MCR calibration data.  Adapted from the
matplotlib-based mcr_file_plotter.py but using Plotly for interactivity.

@author: jmitchell
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .config import (
    COLORS, PLOT_COLORS, SEGMENT_COLORS, PATCH_COLORSCALE,
    PLOTLY_LAYOUT_DEFAULTS, PLOTLY_AXIS_DEFAULTS,
    TX_STATS_LENS_ALIGN_ANGLE_DEG,
)
from .geometry_transforms import (
    lens_rotation,
    load_merged_tx_geometry,
    xy_clockwise,
)
from . import parser


def create_port_figure(
    files_b1: list[str],
    files_b2: list[str],
    depvar: str,
    frequency: float,
    spread_type: str,
    y_lims: list[float] | None = None,
    spread_lims: list[float] | None = None,
) -> go.Figure:
    """Create a 2x3 port-domain plot figure (one row per beam)."""
    fig = make_subplots(
        rows=2, cols=3,
        subplot_titles=[
            "All Files – Beam 1", "Median – Beam 1", f"{spread_type} – Beam 1",
            "All Files – Beam 2", "Median – Beam 2", f"{spread_type} – Beam 2",
        ],
        vertical_spacing=0.14, horizontal_spacing=0.06,
    )

    for beam_idx, beam_files in enumerate([files_b1, files_b2], start=1):
        if not beam_files:
            continue
        arrays, freq_array = _load_arrays(beam_files, depvar)
        col_idx = int(np.argmin((freq_array - frequency) ** 2))
        stacked = np.stack([a[:, col_idx] for a in arrays], axis=0)
        ports = np.arange(1, stacked.shape[1] + 1)
        median_vals = np.nanmedian(stacked, axis=0)
        spread = _compute_spread(stacked, spread_type)

        x_all, y_all = _batch_traces(ports, stacked, len(arrays))
        fig.add_trace(go.Scattergl(
            x=x_all, y=y_all, mode="lines",
            line=dict(color=PLOT_COLORS["all_traces"], width=1),
            showlegend=False, hoverinfo="skip",
        ), row=beam_idx, col=1)

        _add_median_fill(fig, ports, median_vals, spread, beam_idx, 2)

        fig.add_trace(go.Scatter(
            x=ports, y=spread, mode="lines",
            line=dict(color=PLOT_COLORS["spread"], width=2),
            showlegend=False,
        ), row=beam_idx, col=3)

    n_total = max(len(files_b1), len(files_b2))
    fig.update_layout(
        title=dict(text=(
            f"Port Plot  |  {depvar.capitalize()}  |  "
            f"f = {frequency:.2f} GHz  |  N = {n_total} files"
        ), font=dict(size=14)),
        height=680, **PLOTLY_LAYOUT_DEFAULTS,
    )
    _apply_axis_formatting(fig, "Port", depvar, y_lims, spread_lims)
    return fig


def create_freq_figure(
    files_b1: list[str],
    files_b2: list[str],
    depvar: str,
    port_number: int,
    spread_type: str,
    y_lims: list[float] | None = None,
    spread_lims: list[float] | None = None,
) -> go.Figure:
    """Create a 2x3 frequency-domain plot figure (one row per beam)."""
    fig = make_subplots(
        rows=2, cols=3,
        subplot_titles=[
            "All Files – Beam 1", "Median – Beam 1", f"{spread_type} – Beam 1",
            "All Files – Beam 2", "Median – Beam 2", f"{spread_type} – Beam 2",
        ],
        vertical_spacing=0.14, horizontal_spacing=0.06,
    )
    port_idx = port_number - 1

    for beam_idx, beam_files in enumerate([files_b1, files_b2], start=1):
        if not beam_files:
            continue
        arrays = []
        freq_array = None
        for fp in beam_files:
            data = parser.get_file_data(fp)
            arr = data["gain"] if depvar == "gain" else data["phase"]
            arrays.append(arr[port_idx, :])
            if freq_array is None:
                freq_array = data["frequencies"]

        stacked = np.stack(arrays, axis=0)
        median_vals = np.nanmedian(stacked, axis=0)
        spread = _compute_spread(stacked, spread_type)

        x_all, y_all = _batch_traces(freq_array, stacked, len(arrays))
        fig.add_trace(go.Scattergl(
            x=x_all, y=y_all, mode="lines",
            line=dict(color=PLOT_COLORS["all_traces"], width=1),
            showlegend=False, hoverinfo="skip",
        ), row=beam_idx, col=1)

        _add_median_fill(fig, freq_array, median_vals, spread, beam_idx, 2)

        fig.add_trace(go.Scatter(
            x=freq_array, y=spread, mode="lines",
            line=dict(color=PLOT_COLORS["spread"], width=2),
            showlegend=False,
        ), row=beam_idx, col=3)

    n_total = max(len(files_b1), len(files_b2))
    fig.update_layout(
        title=dict(text=(
            f"Frequency Plot  |  {depvar.capitalize()}  |  "
            f"Port {port_number}  |  N = {n_total} files"
        ), font=dict(size=14)),
        height=680, **PLOTLY_LAYOUT_DEFAULTS,
    )
    _apply_axis_formatting(fig, "Frequency [GHz]", depvar, y_lims, spread_lims)
    return fig


# ===================================================================
# Segmented frequency plot
# ===================================================================

def create_segmented_freq_figure(
    files_per_setpoint_b1: dict[float, list[str]],
    files_per_setpoint_b2: dict[float, list[str]],
    depvar: str,
    port_number: int,
    spread_type: str,
    y_lims: list[float] | None = None,
    spread_lims: list[float] | None = None,
) -> go.Figure:
    """Create a segmented frequency-domain plot stitching all setpoints.
    Each segment includes one overlap point from the previous segment."""
    fig = make_subplots(
        rows=2, cols=3,
        subplot_titles=[
            "All Files – Beam 1", "Median – Beam 1", f"{spread_type} – Beam 1",
            "All Files – Beam 2", "Median – Beam 2", f"{spread_type} – Beam 2",
        ],
        vertical_spacing=0.14, horizontal_spacing=0.06,
    )
    all_setpoints = sorted(
        set(list(files_per_setpoint_b1.keys()) + list(files_per_setpoint_b2.keys()))
    )
    boundaries = _compute_segment_boundaries(all_setpoints)
    port_idx = port_number - 1
    n_total = 0

    for beam_idx, fps_dict in enumerate(
        [files_per_setpoint_b1, files_per_setpoint_b2], start=1
    ):
        for sp_i, sp in enumerate(all_setpoints):
            files = fps_dict.get(sp, [])
            if not files:
                continue
            n_total = max(n_total, len(files))
            lo, hi = boundaries[sp]
            color = SEGMENT_COLORS[sp_i % len(SEGMENT_COLORS)]

            arrays = []
            freq_array = None
            for fp in files:
                data = parser.get_file_data(fp)
                arr = data["gain"] if depvar == "gain" else data["phase"]
                arrays.append(arr[port_idx, :])
                if freq_array is None:
                    freq_array = data["frequencies"]

            stacked = np.stack(arrays, axis=0)
            mask = (freq_array >= lo) & (freq_array < hi)
            # Include boundary overlap + extra sample below lo (RFIC set-point switch)
            if sp_i > 0:
                below = np.where(freq_array < lo)[0]
                if len(below) > 0:
                    mask[below[-1]] = True
                    if len(below) >= 2:
                        mask[below[-2]] = True

            seg_freqs = freq_array[mask]
            seg_data = stacked[:, mask]
            if seg_data.size == 0:
                continue

            x_all, y_all = _batch_traces(seg_freqs, seg_data, len(files))
            fig.add_trace(go.Scattergl(
                x=x_all, y=y_all, mode="lines",
                line=dict(color=color, width=1), opacity=0.25,
                showlegend=False, hoverinfo="skip",
            ), row=beam_idx, col=1)

            median_vals = np.nanmedian(seg_data, axis=0)
            spread = _compute_spread(seg_data, spread_type)

            fig.add_trace(go.Scatter(
                x=seg_freqs, y=median_vals + spread,
                mode="lines", line=dict(width=0),
                showlegend=False, hoverinfo="skip",
            ), row=beam_idx, col=2)
            fig.add_trace(go.Scatter(
                x=seg_freqs, y=median_vals - spread,
                mode="lines", line=dict(width=0),
                fill="tonexty", fillcolor=_rgba(color, 0.3),
                showlegend=False, hoverinfo="skip",
            ), row=beam_idx, col=2)
            fig.add_trace(go.Scatter(
                x=seg_freqs, y=median_vals, mode="lines",
                line=dict(color=color, width=2),
                name=f"{sp:.2f} GHz", showlegend=(beam_idx == 1),
            ), row=beam_idx, col=2)
            fig.add_trace(go.Scatter(
                x=seg_freqs, y=spread, mode="lines",
                line=dict(color=color, width=2), showlegend=False,
            ), row=beam_idx, col=3)

    fig.update_layout(
        title=dict(text=(
            f"Segmented Frequency Plot  |  {depvar.capitalize()}  |  "
            f"Port {port_number}  |  N = {n_total} files"
        ), font=dict(size=14)),
        height=680, legend=dict(font=dict(size=10)),
        **PLOTLY_LAYOUT_DEFAULTS,
    )
    _apply_axis_formatting(fig, "Frequency [GHz]", depvar, y_lims, spread_lims)
    return fig


# ===================================================================
# Patch map (statistics) — always shows both H-pol and V-pol
# ===================================================================

def _subplot_xy_names(row: int, col: int, ncols: int = 3) -> tuple[str, str]:
    idx = (row - 1) * ncols + col
    xn = "x" if idx == 1 else f"x{idx}"
    yn = "y" if idx == 1 else f"y{idx}"
    return xn, yn


def _yaxis_name_from_x(xaxis_name: str) -> str:
    return "y" if xaxis_name == "x" else f"y{xaxis_name[1:]}"


def _colorbar_dict(
    title: str,
    xaxis_name: str,
) -> dict:
    """Colorbar anchored just outside the subplot x-domain (median / spread)."""
    yaxis_name = _yaxis_name_from_x(xaxis_name)
    return dict(
        title=dict(text=title, side="right", font=dict(size=11)),
        len=0.42,
        thickness=14,
        x=1.02,
        xanchor="left",
        xref=f"{xaxis_name} domain",
        y=0.5,
        yref=f"{yaxis_name} domain",
        yanchor="middle",
        tickfont=dict(size=10),
    )


def _add_rfic_outline_traces(
    fig: go.Figure,
    merged_df: pd.DataFrame,
    align_coords: bool,
    row: int,
    col: int,
) -> None:
    """Per-lens / per-RFIC loops matching ``mcr_file_stats.plot_stats_patches``."""
    angle = TX_STATS_LENS_ALIGN_ANGLE_DEG
    rfics = sorted({int(r) for r in merged_df["RFIC Number"]})
    for lens_number in (1, 2, 3):
        df_lens = merged_df[merged_df["Lens no."] == lens_number]
        for rfic in rfics:
            df_lr = df_lens[df_lens["RFIC Number"] == rfic]
            if len(df_lr) < 2:
                continue
            if align_coords:
                ox, oy = lens_rotation(angle, df_lr)
            else:
                ox = np.asarray(df_lr[" Feed x [mm]"], dtype=float)
                oy = np.asarray(df_lr[" Feed y [mm]"], dtype=float)
            ox, oy = xy_clockwise(ox, oy)
            fig.add_trace(
                go.Scatter(
                    x=ox, y=oy,
                    mode="lines",
                    line=dict(color="black", width=2),
                    opacity=0.5,
                    showlegend=False,
                    hoverinfo="skip",
                ),
                row=row, col=col,
            )


def create_patch_map_figure(
    files_b1: list[str],
    files_b2: list[str],
    depvar: str,
    frequency: float,
    spread_type: str,
    avg_lims: list[float] | None = None,
    spread_lims: list[float] | None = None,
    align_coords: bool = True,
) -> go.Figure:
    """
    Create a 4-row patch-map figure.

    Aligned coordinates use ``lens_rotation`` with fixed TX angle
    (``TX_STATS_LENS_ALIGN_ANGLE_DEG``), matching ``mcr_file_stats.py``.

    Layout (per beam):
        Row 1/3 – H-pol: Median | Spread | RFIC boxplot
        Row 2/4 – V-pol: Median | Spread | RFIC boxplot
    """
    merged = load_merged_tx_geometry()
    angle = TX_STATS_LENS_ALIGN_ANGLE_DEG
    if align_coords:
        x, y = lens_rotation(angle, merged)
    else:
        x = np.asarray(merged[" Feed x [mm]"], dtype=float)
        y = np.asarray(merged[" Feed y [mm]"], dtype=float)

    lens = np.asarray(merged["Lens no."], dtype=int)
    rfic = np.asarray(merged["RFIC Number"], dtype=int)
    patch = np.asarray(merged["Patch Number"], dtype=int)

    fig = make_subplots(
        rows=4, cols=3,
        subplot_titles=[
            "H-pol Median – B1", f"H-pol {spread_type} – B1", "RFIC Box – B1",
            "V-pol Median – B1", f"V-pol {spread_type} – B1", "",
            "H-pol Median – B2", f"H-pol {spread_type} – B2", "RFIC Box – B2",
            "V-pol Median – B2", f"V-pol {spread_type} – B2", "",
        ],
        vertical_spacing=0.06,
        horizontal_spacing=0.14,
    )

    zmin_a = avg_lims[0] if avg_lims else None
    zmax_a = avg_lims[1] if avg_lims else None
    zmin_s = spread_lims[0] if spread_lims else None
    zmax_s = spread_lims[1] if spread_lims else None

    for beam_idx, beam_files in enumerate([files_b1, files_b2], start=1):
        if not beam_files:
            continue

        arrays, freq_array = _load_arrays(beam_files, depvar)
        col_idx = int(np.argmin((freq_array - frequency) ** 2))
        stacked = np.stack([a[:, col_idx] for a in arrays], axis=0)
        median_all = np.nanmedian(stacked, axis=0)
        spread_all = _compute_spread(stacked, spread_type)

        z_h = median_all[::2]
        z_v = median_all[1::2]
        sp_h = spread_all[::2]
        sp_v = spread_all[1::2]

        n_pts = min(len(x), len(z_h), len(z_v))
        if n_pts == 0:
            continue

        xb, yb = x[:n_pts], y[:n_pts]
        lu, ru, pu = lens[:n_pts], rfic[:n_pts], patch[:n_pts]
        z_h, z_v = z_h[:n_pts], z_v[:n_pts]
        sp_h, sp_v = sp_h[:n_pts], sp_v[:n_pts]
        feed_ids = np.arange(n_pts)

        r_h = (beam_idx - 1) * 2 + 1
        r_v = r_h + 1

        def _hover(z_arr, sp_arr, pol_label):
            return [
                f"Patch {p}<br>Lens {l}<br>RFIC {r}<br>"
                f"Pol: {pol_label}<br>Median: {z_arr[i]:.2f}<br>"
                f"Spread: {sp_arr[i]:.2f}<br>ΔPol: {abs(z_h[i]-z_v[i]):.2f}"
                for i, (p, l, r) in enumerate(zip(pu, lu, ru))
            ]

        xa_h1, _ = _subplot_xy_names(r_h, 1)
        xa_h2, _ = _subplot_xy_names(r_h, 2)
        xa_v1, _ = _subplot_xy_names(r_v, 1)
        xa_v2, _ = _subplot_xy_names(r_v, 2)

        for rc in ((r_h, 1), (r_h, 2), (r_v, 1), (r_v, 2)):
            _add_rfic_outline_traces(fig, merged, align_coords, rc[0], rc[1])

        fig.add_trace(go.Scatter(
            x=xb, y=yb, mode="markers",
            marker=dict(
                size=9, symbol="diamond", color=z_h,
                colorscale=PATCH_COLORSCALE,
                cmin=zmin_a, cmax=zmax_a, showscale=True,
                colorbar=_colorbar_dict("Median", xa_h1),
                line=dict(width=0.5, color="black"),
                angle=0,
                angleref="up",
            ),
            text=_hover(z_h, sp_h, "H"), hoverinfo="text",
            showlegend=False, customdata=feed_ids,
        ), row=r_h, col=1)

        fig.add_trace(go.Scatter(
            x=xb, y=yb, mode="markers",
            marker=dict(
                size=9, symbol="diamond", color=sp_h,
                colorscale=PATCH_COLORSCALE,
                cmin=zmin_s, cmax=zmax_s, showscale=True,
                colorbar=_colorbar_dict(spread_type, xa_h2),
                line=dict(width=0.5, color="black"),
                angle=0,
                angleref="up",
            ),
            text=_hover(z_h, sp_h, "H"), hoverinfo="text",
            showlegend=False, customdata=feed_ids,
        ), row=r_h, col=2)

        fig.add_trace(go.Scatter(
            x=xb, y=yb, mode="markers",
            marker=dict(
                size=9, symbol="diamond", color=z_v,
                colorscale=PATCH_COLORSCALE,
                cmin=zmin_a, cmax=zmax_a, showscale=True,
                colorbar=_colorbar_dict("Median", xa_v1),
                line=dict(width=0.5, color="black"),
                angle=180,
                angleref="up",
            ),
            text=_hover(z_v, sp_v, "V"), hoverinfo="text",
            showlegend=False, customdata=feed_ids,
        ), row=r_v, col=1)

        fig.add_trace(go.Scatter(
            x=xb, y=yb, mode="markers",
            marker=dict(
                size=9, symbol="diamond", color=sp_v,
                colorscale=PATCH_COLORSCALE,
                cmin=zmin_s, cmax=zmax_s, showscale=True,
                colorbar=_colorbar_dict(spread_type, xa_v2),
                line=dict(width=0.5, color="black"),
                angle=180,
                angleref="up",
            ),
            text=_hover(z_v, sp_v, "V"), hoverinfo="text",
            showlegend=False, customdata=feed_ids,
        ), row=r_v, col=2)

        rfic_labels = np.repeat(ru, 2)
        lens_labels = np.repeat(lu, 2)
        median_pair = np.column_stack((z_h, z_v)).reshape(-1)
        for l_no in sorted(set(lu)):
            l_mask = lens_labels == l_no
            fig.add_trace(go.Box(
                x=rfic_labels[l_mask], y=median_pair[l_mask],
                name=f"B{beam_idx} · Lens {l_no}",
                marker_color=SEGMENT_COLORS[(l_no - 1) % len(SEGMENT_COLORS)],
                showlegend=True,
                legendgroup=f"b{beam_idx}_l{l_no}",
                boxpoints=False,
            ), row=r_h, col=3)

    n_total = max(len(files_b1), len(files_b2))
    fig.update_layout(
        title=dict(text=(
            f"Patch Map  |  {depvar.capitalize()}  |  "
            f"f = {frequency:.2f} GHz  |  N = {n_total} files"
        ), font=dict(size=14)),
        height=1400,
        legend=dict(font=dict(size=10)),
        **PLOTLY_LAYOUT_DEFAULTS,
    )

    for row in range(1, 5):
        for col in (1, 2):
            xa, _ = _subplot_xy_names(row, col)
            fig.update_xaxes(
                title_text="", row=row, col=col,
                showgrid=False, zeroline=False, showticklabels=False,
                showline=True, mirror=True, linecolor=COLORS["border"],
                constrain="domain",
            )
            fig.update_yaxes(
                title_text="", row=row, col=col,
                showgrid=False, zeroline=False, showticklabels=False,
                showline=True, mirror=True, linecolor=COLORS["border"],
                scaleanchor=xa,
                scaleratio=1.0,
            )
        fig.update_xaxes(
            title_text="RFIC Number", row=row, col=3,
            **PLOTLY_AXIS_DEFAULTS,
        )
        fig.update_yaxes(
            title_text=depvar.capitalize(), row=row, col=3,
            range=avg_lims, **PLOTLY_AXIS_DEFAULTS,
        )

    for ann in fig.layout.annotations:
        ann.font.color = COLORS["text_muted"]
        ann.font.size = 11

    return fig


# ===================================================================
# Port histogram (H/V × both beams)
# ===================================================================

def create_port_histogram(
    files_b1: list[str],
    files_b2: list[str],
    depvar: str,
    frequency: float,
    port_number: int,
    max_ports: int | None = None,
) -> go.Figure:
    """
    2×2 histograms: H-pol then V-pol, columns Beam 1 / Beam 2.

    *port_number* selects a port; the paired H/V indices are derived
    (odd port → H, even → V for the same feed).
    """
    if max_ports is None:
        ref_files = files_b1 or files_b2
        if not ref_files:
            raise ValueError("No files loaded for histogram.")
        max_ports = int(parser.get_file_data(ref_files[0])["gain"].shape[0])

    p = int(port_number)
    if p < 1 or p > max_ports:
        raise ValueError(f"Port must be between 1 and {max_ports}.")

    if p % 2 == 1:
        h_port, v_port = p, p + 1
    else:
        h_port, v_port = p - 1, p

    if v_port > max_ports or h_port < 1:
        raise ValueError("H/V port pair is out of range for this dataset.")

    hi, vi = h_port - 1, v_port - 1
    geometry = parser.load_tx_geometry()
    feed_index = hi // 2
    patch_no = (
        geometry["patch_no"][feed_index]
        if feed_index < geometry["n_feeds"] else "?"
    )
    lens_no = (
        geometry["lens_no"][feed_index]
        if feed_index < geometry["n_feeds"] else "?"
    )

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[
            "H-pol — Beam 1", "H-pol — Beam 2",
            "V-pol — Beam 1", "V-pol — Beam 2",
        ],
        vertical_spacing=0.12,
        horizontal_spacing=0.10,
    )

    def _collect(beam_files: list[str], port_idx: int) -> list[float]:
        vals: list[float] = []
        for fp in beam_files:
            data = parser.get_file_data(fp)
            arr = data["gain"] if depvar == "gain" else data["phase"]
            freq_array = data["frequencies"]
            col_idx = int(np.argmin((freq_array - frequency) ** 2))
            if port_idx < arr.shape[0]:
                v = arr[port_idx, col_idx]
                if np.isfinite(v):
                    vals.append(float(v))
        return vals

    any_data = False
    positions = (
        (1, 1, files_b1, hi, PLOT_COLORS["average"]),
        (1, 2, files_b2, hi, PLOT_COLORS["spread"]),
        (2, 1, files_b1, vi, PLOT_COLORS["average"]),
        (2, 2, files_b2, vi, PLOT_COLORS["spread"]),
    )
    for row, col, bfiles, pidx, color in positions:
        vals = _collect(bfiles, pidx) if bfiles else []
        if not vals:
            continue
        any_data = True
        fig.add_trace(
            go.Histogram(
                x=vals,
                name=f"r{row}c{col}",
                marker_color=color,
                opacity=0.88,
                nbinsx=24,
                showlegend=False,
            ),
            row=row, col=col,
        )

    if not any_data:
        raise ValueError("No finite samples for this port / frequency.")

    fig.update_layout(
        title=dict(text=(
            f"Ports H{h_port} / V{v_port}  (feed patch {patch_no}, lens {lens_no})  |  "
            f"{depvar.capitalize()}  |  f = {frequency:.2f} GHz"
        ), font=dict(size=14)),
        height=520,
        barmode="overlay",
        **PLOTLY_LAYOUT_DEFAULTS,
    )
    for row in (1, 2):
        for col in (1, 2):
            fig.update_xaxes(
                title_text=depvar.capitalize(), row=row, col=col,
                **PLOTLY_AXIS_DEFAULTS,
            )
            fig.update_yaxes(
                title_text="Count", row=row, col=col,
                **PLOTLY_AXIS_DEFAULTS,
            )

    return fig


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _load_arrays(
    beam_files: list[str], depvar: str,
) -> tuple[list[np.ndarray], np.ndarray]:
    """Load gain/phase arrays and frequency vector from a list of files."""
    arrays: list[np.ndarray] = []
    freq_array = None
    for fp in beam_files:
        data = parser.get_file_data(fp)
        arr = data["gain"] if depvar == "gain" else data["phase"]
        arrays.append(arr)
        if freq_array is None:
            freq_array = data["frequencies"]
    return arrays, freq_array


def _batch_traces(
    x_vals: np.ndarray, stacked: np.ndarray, n_files: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Combine multiple line traces into one array with NaN separators."""
    sep = np.array([np.nan])
    x_parts: list[np.ndarray] = []
    y_parts: list[np.ndarray] = []
    for i in range(n_files):
        x_parts.append(x_vals)
        x_parts.append(sep)
        y_parts.append(stacked[i])
        y_parts.append(sep)
    return np.concatenate(x_parts), np.concatenate(y_parts)


def _add_median_fill(fig, x, median, spread, row, col):
    """Add median line with spread envelope to subplot."""
    fig.add_trace(go.Scatter(
        x=x, y=median + spread, mode="lines", line=dict(width=0),
        showlegend=False, hoverinfo="skip",
    ), row=row, col=col)
    fig.add_trace(go.Scatter(
        x=x, y=median - spread, mode="lines", line=dict(width=0),
        fill="tonexty", fillcolor=PLOT_COLORS["fill"],
        showlegend=False, hoverinfo="skip",
    ), row=row, col=col)
    fig.add_trace(go.Scatter(
        x=x, y=median, mode="lines",
        line=dict(color=PLOT_COLORS["average"], width=2),
        showlegend=False,
    ), row=row, col=col)


def _compute_spread(stacked: np.ndarray, spread_type: str) -> np.ndarray:
    """Compute the spread metric across the file axis (axis 0)."""
    if spread_type == "STD":
        return np.nanstd(stacked, axis=0)
    elif spread_type == "IQR":
        return (
            np.nanpercentile(stacked, 75, axis=0)
            - np.nanpercentile(stacked, 25, axis=0)
        )
    else:
        return np.nanmax(stacked, axis=0) - np.nanmin(stacked, axis=0)


def _compute_segment_boundaries(
    setpoints: list[float],
) -> dict[float, tuple[float, float]]:
    """Compute frequency segment boundaries as midpoints between setpoints."""
    boundaries: dict[float, tuple[float, float]] = {}
    for i, sp in enumerate(setpoints):
        if i == 0:
            lo = sp - (setpoints[1] - sp) / 2 if len(setpoints) > 1 else sp - 0.25
        else:
            lo = (setpoints[i - 1] + sp) / 2
        if i == len(setpoints) - 1:
            hi = sp + (sp - setpoints[-2]) / 2 if len(setpoints) > 1 else sp + 0.25
        else:
            hi = (sp + setpoints[i + 1]) / 2
        boundaries[sp] = (lo, hi)
    return boundaries


def _rgba(hex_color: str, alpha: float) -> str:
    """Convert ``#RRGGBB`` to ``rgba(r, g, b, alpha)``."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"


def _apply_axis_formatting(
    fig: go.Figure, x_title: str, depvar: str,
    y_lims: list[float] | None, spread_lims: list[float] | None,
) -> None:
    """Apply consistent axis labels, ranges and grid colours to all subplots."""
    y_label = depvar.capitalize()
    for row in range(1, 3):
        for col in range(1, 4):
            fig.update_xaxes(title_text=x_title, row=row, col=col, **PLOTLY_AXIS_DEFAULTS)
            if col < 3:
                fig.update_yaxes(
                    title_text=y_label, row=row, col=col,
                    range=y_lims, **PLOTLY_AXIS_DEFAULTS,
                )
            else:
                fig.update_yaxes(
                    title_text=y_label, row=row, col=col,
                    range=spread_lims, **PLOTLY_AXIS_DEFAULTS,
                )
    for ann in fig.layout.annotations:
        ann.font.color = COLORS["text_muted"]
        ann.font.size = 12
