# -*- coding: utf-8 -*-
"""
Lens coordinate transforms for TX statistics plots.

Mirrors ``cal_utils.lens_rotation`` and ``xy_clockwise`` from RF_Space
``data_processing/cal_utils.py`` so patch maps match ``mcr_file_stats.py``.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .config import TX_GEOMETRY_CSV, TX_RFIC_CSV


def lens_rotation(angle: float, df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """
    Rotate lens coordinates based on feed coordinates and patch rotations.

    ``patch_rotations = angle * (Lens no. - 1)`` per row (cumulative per lens).
    """
    x_shift = np.array(df[" Feed x [mm]"]) - np.array(df[" Lens x [mm]"])
    y_shift = np.array(df[" Feed y [mm]"]) - np.array(df[" Lens y [mm]"])
    patch_rotations = angle * (np.array(df["Lens no."]) - 1)
    x_rot = (
        x_shift * np.cos(patch_rotations * np.pi / 180.0)
        - y_shift * np.sin(patch_rotations * np.pi / 180.0)
    )
    y_rot = (
        y_shift * np.cos(patch_rotations * np.pi / 180.0)
        + x_shift * np.sin(patch_rotations * np.pi / 180.0)
    )
    x_new = x_rot + np.array(df[" Lens x [mm]"])
    y_new = y_rot + np.array(df[" Lens y [mm]"])
    return x_new.copy(), y_new.copy()


def xy_clockwise(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Sort coordinates clockwise; append first point to close the RFIC loop."""
    centroid_x = np.mean(x)
    centroid_y = np.mean(y)
    angles = np.arctan2(y - centroid_y, x - centroid_x)
    sorted_indices = np.argsort(angles)
    x = np.append(x[sorted_indices], x[sorted_indices[0]])
    y = np.append(y[sorted_indices], y[sorted_indices[0]])
    return x, y


def load_merged_tx_geometry(
    geometry_csv: Path | None = None,
    rfic_csv: Path | None = None,
) -> pd.DataFrame:
    """
    Same merge as ``mcr_file_stats.plot_stats_patches``: geometry × RFIC map × 3 lenses.
    """
    geom_path = geometry_csv or TX_GEOMETRY_CSV
    rfic_path = rfic_csv or TX_RFIC_CSV
    df_maps_tlm = pd.read_csv(geom_path, header=1).reset_index(drop=True)
    df_maps_rfic = pd.read_csv(rfic_path)
    df_right = pd.concat([df_maps_rfic] * 3, axis=0).reset_index(drop=True)
    df = pd.concat([df_maps_tlm, df_right], axis=1)
    return df
