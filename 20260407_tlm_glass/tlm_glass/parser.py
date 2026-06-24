# -*- coding: utf-8 -*-
"""
TLM Glass - File parsing and data discovery.

Handles parsing of MCR calibration CSV files (OP, RFA, SEC) and recursive
discovery of TLM data directories. Adapted from cal_utils.py patterns but
using pathlib and regex-based folder name parsing for robustness.

@author: jmitchell
"""

import csv
import logging
import re
from collections.abc import Callable
from pathlib import Path

import numpy as np
import pandas as pd

from .config import TX_GEOMETRY_CSV, TX_RFIC_CSV

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Regex patterns for parsing folder and file names
# ---------------------------------------------------------------------------

# Measurement CSV filenames, e.g.:
#   OP_250904-10_12_47-MCR1_Rig1__QR420-0345-01373_tx_Beam1_27.50_31.00_GHz_27.50_GHz_45C.csv
_CSV_FILENAME_RE = re.compile(
    r"^(?P<file_type>OP|RFA|SEC|UnclippedRfa|CT1|CT2)_"
    r"(?P<timestamp>\d{6}-\d{2}_\d{2}_\d{2})-"
    r"MCR(?P<mcr>\d+)_Rig(?P<rig>\d+)__"
    r"(?P<qr>QR[\w-]+)_"
    r"(?P<lens_type>tx|rx)_"
    r"Beam(?P<beam>\d+)_"
    r"(?P<freq_start>[\d.]+)_(?P<freq_end>[\d.]+)_GHz_"
    r"(?P<setpoint>[\d.]+)_GHz_"
    r"(?P<temperature>\d+)C\.csv$",
    re.IGNORECASE,
)

# Top-level TLM result folder, e.g.:
#   PASS_2025-09-04_10-09-58_0_QR420-0345-01373_ERc005a90f
_TLM_FOLDER_RE = re.compile(
    r"^(?P<passfail>PASS|FAIL|ERR)?_?"
    r"(?P<date>\d{4}-\d{2}-\d{2})_(?P<time>\d{2}-\d{2}-\d{2})_"
    r"\d+_"
    r"(?P<qr>QR[\w-]+)_"
    r"(?P<er_id>ER\w+)$",
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# Module-level cache for parsed file data
# ---------------------------------------------------------------------------

_file_cache: dict[str, dict] = {}


def parse_mcr_csv(path: str) -> dict:
    """
    Parse a single MCR calibration CSV file (OP, RFA, SEC, or UnclippedRfa).

    The file format consists of metadata header lines, a 'barcodes' marker row,
    a frequency header row, then rows of gain/phase pairs per port.

    Parameters
    ----------
    path : str
        Full path to the CSV file.

    Returns
    -------
    dict
        Dictionary containing:
        - metadata : dict
            Key-value pairs from the file header.
        - gain : numpy.ndarray
            Gain values, shape (n_ports, n_frequencies).
        - phase : numpy.ndarray
            Phase values, shape (n_ports, n_frequencies).
        - frequencies : numpy.ndarray
            Measurement frequencies in GHz.
        - sec_headers : list[str], optional
            Extra column headers (SEC files only).
        - sec_data : numpy.ndarray, optional
            Extra column data (SEC files only).
    """
    path_str = str(path)
    path_obj = Path(path_str)
    is_sec = path_obj.name.upper().startswith("SEC_")

    header_lines = []
    with open(path_str, "r") as f:
        reader = csv.reader(f, delimiter=",")
        for row in reader:
            header_lines.append(row)

    barcodes_idx = _find_row_containing(header_lines, "barcodes")
    if barcodes_idx is None:
        raise ValueError(f"Could not find 'barcodes' row in {path_str}")

    metadata = _parse_header_metadata(header_lines[:barcodes_idx])

    freq_header_idx = barcodes_idx + 1
    data_start_idx = barcodes_idx + 2
    freq_header_row = header_lines[freq_header_idx]

    if is_sec:
        freq_col_start = _find_freq_column_start(freq_header_row)
        sec_headers = [h.strip() for h in freq_header_row[:freq_col_start]]
        freq_entries = freq_header_row[freq_col_start:]

        full_array = np.genfromtxt(
            path_str, delimiter=",", skip_header=data_start_idx
        )
        sec_data = full_array[:, :freq_col_start]
        meas_array = full_array[:, freq_col_start:]
    else:
        freq_entries = freq_header_row
        meas_array = np.genfromtxt(
            path_str, delimiter=",", skip_header=data_start_idx
        )

    frequencies = np.array(
        [float(v) for v in freq_entries[::2] if v.strip()]
    )
    gain = meas_array[:, ::2]
    phase = meas_array[:, 1::2]

    result = {
        "metadata": metadata,
        "gain": gain,
        "phase": phase,
        "frequencies": frequencies,
    }
    if is_sec:
        result["sec_headers"] = sec_headers
        result["sec_data"] = sec_data

    return result


def get_file_data(file_path: str) -> dict:
    """
    Load and cache parsed MCR CSV data.

    Uses a module-level cache so repeated access to the same file is fast.

    Parameters
    ----------
    file_path : str
        Full path to the CSV file.

    Returns
    -------
    dict
        Parsed file data (see parse_mcr_csv).
    """
    if file_path not in _file_cache:
        _file_cache[file_path] = parse_mcr_csv(file_path)
    return _file_cache[file_path]


def clear_cache():
    """Clear the file data cache."""
    _file_cache.clear()


# ---------------------------------------------------------------------------
# Geometry loading
# ---------------------------------------------------------------------------

_geometry_cache: dict | None = None


def load_tx_geometry() -> dict:
    """
    Load TX array geometry and RFIC patch-feed mapping.

    The aligned (rotated) coordinates are computed per-lens: each lens's
    feeds are rotated around that lens's centre by the lens-assembly
    rotation angle from the CSV.  This produces a view where all three
    lenses are oriented identically, matching the physical device layout.

    Returns
    -------
    dict
        ``feed_x``, ``feed_y`` : ndarray(228,) – per-lens-rotated positions.
        ``feed_x_raw``, ``feed_y_raw`` : ndarray(228,) – un-rotated (global CS).
        ``lens_no`` : ndarray(228,) – lens number per feed (1-3).
        ``rfic_no`` : ndarray(228,) – RFIC number per feed.
        ``patch_no`` : ndarray(228,) – patch number per feed (1-76 per lens).
        ``n_feeds`` : int – total number of feeds (228 for Tx).
    """
    global _geometry_cache
    if _geometry_cache is not None:
        return _geometry_cache

    df_geom = pd.read_csv(TX_GEOMETRY_CSV, header=1)
    feed_x = df_geom[" Feed x [mm]"].values.astype(float)
    feed_y = df_geom[" Feed y [mm]"].values.astype(float)
    lens_x = df_geom[" Lens x [mm]"].values.astype(float)
    lens_y = df_geom[" Lens y [mm]"].values.astype(float)
    lens_rot = df_geom[
        " Lens-assembly +x axis rotation with respect to array CS [deg]"
    ].values.astype(float)
    lens_no = df_geom["Lens no."].values.astype(int)

    df_rfic = pd.read_csv(TX_RFIC_CSV)
    rfic_no = np.tile(df_rfic["RFIC Number"].values, 3)
    patch_no = np.tile(df_rfic["Patch Number"].values, 3)

    # Per-lens rotation: rotate each feed around its own lens centre
    x_rot = np.empty_like(feed_x)
    y_rot = np.empty_like(feed_y)
    for l_no in np.unique(lens_no):
        mask = lens_no == l_no
        cx = lens_x[mask][0]
        cy = lens_y[mask][0]
        angle_rad = np.radians(lens_rot[mask][0])
        dx = feed_x[mask] - cx
        dy = feed_y[mask] - cy
        x_rot[mask] = cx + dx * np.cos(angle_rad) - dy * np.sin(angle_rad)
        y_rot[mask] = cy + dx * np.sin(angle_rad) + dy * np.cos(angle_rad)

    _geometry_cache = {
        "feed_x": x_rot,
        "feed_y": y_rot,
        "feed_x_raw": feed_x,
        "feed_y_raw": feed_y,
        "lens_no": lens_no,
        "rfic_no": rfic_no,
        "patch_no": patch_no,
        "n_feeds": len(feed_x),
    }
    return _geometry_cache


# ---------------------------------------------------------------------------
# Full results builder
# ---------------------------------------------------------------------------


def build_full_results(
    df_index: pd.DataFrame,
    progress_hook: Callable[[int, str], None] | None = None,
) -> pd.DataFrame:
    """
    Build a wide DataFrame with gain and phase at each file's setpoint
    frequency for every port in every indexed file.

    Parameters
    ----------
    df_index : pd.DataFrame
        File index DataFrame returned by :func:`discover_files`.
    progress_hook : callable, optional
        If provided, called as ``progress_hook(percent, message)`` during
        processing (``percent`` in 0--100).
    """
    meta_cols = [
        "qr", "file_type", "beam", "setpoint", "iteration",
        "temperature", "mcr", "rig",
    ]
    chunks: list[pd.DataFrame] = []
    n_rows = len(df_index)
    if n_rows == 0:
        return pd.DataFrame()

    for i, (_, row) in enumerate(df_index.iterrows()):
        if progress_hook is not None and (i % max(1, n_rows // 40) == 0 or i == n_rows - 1):
            pct = int(100 * (i + 1) / n_rows)
            progress_hook(pct, f"Reading files ({i + 1:,} / {n_rows:,})…")

        try:
            data = get_file_data(row["file_path"])
            freq_array = data["frequencies"]
            col_idx = int(np.argmin((freq_array - row["setpoint"]) ** 2))

            n_ports = data["gain"].shape[0]
            file_df = pd.DataFrame({
                "port": np.arange(1, n_ports + 1),
                "gain": data["gain"][:, col_idx],
                "phase": data["phase"][:, col_idx],
            })
            for col in meta_cols:
                file_df[col] = row[col]

            chunks.append(file_df)
        except Exception as exc:
            logger.warning("Failed to parse %s: %s", row["file_path"], exc)

    if not chunks:
        return pd.DataFrame()

    if progress_hook is not None:
        progress_hook(100, "Merging tables…")

    result = pd.concat(chunks, ignore_index=True)
    col_order = meta_cols + ["port", "gain", "phase"]
    return result[col_order]


def discover_files(
    root_path: str,
    progress_hook: Callable[[int, str], None] | None = None,
) -> pd.DataFrame:
    """
    Recursively discover all MCR measurement CSV files under a directory.

    Walks the directory tree looking for ``iteration_N`` folders containing
    OP, RFA, SEC and other measurement CSV files.  Parses folder and file
    names to extract metadata.

    Parameters
    ----------
    root_path : str
        Root directory path to search.

    Returns
    -------
    pd.DataFrame
        Index of discovered files with columns: file_path, file_type, qr,
        beam, setpoint, temperature, mcr, rig, lens_type, iteration,
        passfail, datetime_str.
    """
    root = Path(root_path)
    if not root.is_dir():
        raise FileNotFoundError(f"Directory not found: {root_path}")

    if progress_hook is not None:
        progress_hook(2, "Scanning for CSV files under iteration folders…")

    csv_paths = list(root.rglob("iteration_*/*.csv"))
    n_paths = len(csv_paths)

    empty_cols = [
        "file_path", "file_type", "qr", "beam", "setpoint",
        "temperature", "mcr", "rig", "lens_type", "iteration",
        "passfail", "datetime_str",
    ]
    if n_paths == 0:
        return pd.DataFrame(columns=empty_cols)

    records = []
    step = max(1, n_paths // 50)
    for i, csv_path in enumerate(csv_paths):
        if progress_hook is not None and (i % step == 0 or i == n_paths - 1):
            pct = 2 + int(85 * (i + 1) / n_paths)
            progress_hook(
                min(pct, 90),
                f"Indexing ({i + 1:,} / {n_paths:,} files)…",
            )

        try:
            if csv_path.stat().st_size < 10_000:
                continue
        except OSError:
            continue

        file_info = _parse_csv_filename(csv_path.name)
        if file_info is None:
            continue

        iter_folder = csv_path.parent
        iteration = _extract_iteration_number(iter_folder.name)
        tlm_folder = iter_folder.parent.parent
        tlm_info = _parse_tlm_folder_name(tlm_folder.name)
        passfail = tlm_info.get("passfail", "") if tlm_info else ""

        records.append(
            {
                "file_path": str(csv_path),
                "file_type": file_info["file_type"],
                "qr": file_info["qr"],
                "beam": int(file_info["beam"]),
                "setpoint": float(file_info["setpoint"]),
                "temperature": int(file_info["temperature"]),
                "mcr": int(file_info["mcr"]),
                "rig": int(file_info["rig"]),
                "lens_type": file_info["lens_type"],
                "iteration": iteration,
                "passfail": passfail,
                "datetime_str": file_info["timestamp"],
            }
        )

    if not records:
        return pd.DataFrame(columns=empty_cols)

    if progress_hook is not None:
        progress_hook(95, "Sorting index…")

    df = pd.DataFrame(records)
    df.sort_values(
        ["qr", "datetime_str", "beam", "setpoint", "file_type"],
        inplace=True,
    )
    df.reset_index(drop=True, inplace=True)

    if progress_hook is not None:
        progress_hook(100, "Done.")

    return df


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _find_row_containing(lines: list[list[str]], keyword: str) -> int | None:
    """Find the index of the first row whose first element contains *keyword*."""
    for i, row in enumerate(lines):
        if row and keyword in row[0].lower():
            return i
    return None


def _parse_header_metadata(header_lines: list[list[str]]) -> dict:
    """Extract key-value metadata from CSV header lines."""
    metadata: dict[str, str] = {}
    for row in header_lines:
        if len(row) >= 2:
            key = row[0].lstrip("# ").strip()
            value = row[1].strip()
            if key:
                metadata[key] = value
    return metadata


def _find_freq_column_start(header_row: list[str]) -> int:
    """
    Find the column index where frequency data begins in a SEC header row.

    Looks for the first column whose value parses as a float in the
    Ka-band frequency range (10-50 GHz).
    """
    for i, val in enumerate(header_row):
        val = val.strip()
        if not val:
            continue
        try:
            f = float(val)
            if 10.0 <= f <= 50.0:
                return i
        except ValueError:
            continue
    raise ValueError("Could not locate frequency columns in SEC header row")


def _parse_csv_filename(filename: str) -> dict | None:
    """Extract metadata from a measurement CSV filename using regex."""
    match = _CSV_FILENAME_RE.match(filename)
    if match is None:
        return None
    return match.groupdict()


def _parse_tlm_folder_name(name: str) -> dict | None:
    """Extract metadata from a top-level TLM result folder name."""
    match = _TLM_FOLDER_RE.match(name)
    if match is None:
        return None
    return match.groupdict()


def _extract_iteration_number(folder_name: str) -> int:
    """Extract the iteration number from a folder name like ``iteration_1``."""
    for part in folder_name.split("_"):
        if part.isdigit():
            return int(part)
    return 1
