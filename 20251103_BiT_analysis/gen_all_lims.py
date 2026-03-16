# -*- coding: utf-8 -*-
"""
Created on Mon Oct 27 10:58:41 2025
@desc: Process a folder of limit files (v0 or v1 formats), expand ranges,
       concatenate tokens, and output a dataframe and Excel file.
@author: jmitchell
"""

import pandas as pd
import numpy as np
import glob
import json
import os


# =============================================================================
# functions
# =============================================================================

def expand_ranges_all_cols(df):
    """
    Expand rows where any column contains a numeric range such as "1-3".

    The function scans all columns; when a range is detected, the row is expanded
    into multiple rows covering the full integer range. Non-numeric ranges are
    left unchanged.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe.

    Returns
    -------
    pd.DataFrame
        Expanded dataframe.
    """

    expanded_rows = []

    for _, row in df.iterrows():

        expanded = [row]

        for col in df.columns:
            new_rows = []

            for r in expanded:
                cell = r[col]

                if isinstance(cell, str) and "-" in cell:
                    part1, part2 = cell.split("-")

                    try:
                        start, end = int(part1), int(part2)

                        for v in range(start, end + 1):
                            r_new = r.copy()
                            r_new[col] = v
                            new_rows.append(r_new)

                    except ValueError:
                        new_rows.append(r)

                else:
                    new_rows.append(r)

            expanded = new_rows

        expanded_rows.extend(expanded)

    return pd.DataFrame(expanded_rows)


def concat_after_limit_file_deux(df, output_col="concatenated"):
    """
    Concatenate token fields following 'limit_file'. If the final two tokens
    are numeric, extract them as lower/upper limits.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe containing a 'limit_file' column.
    output_col : str, optional
        Name of concatenated output field.

    Returns
    -------
    pd.DataFrame
        Dataframe containing 'lower_lim', 'upper_lim', and concatenated values.
    """

    if "limit_file" not in df.columns:
        raise ValueError("'limit_file' column not found.")

    df = df.copy()
    df["lower_lim"] = np.nan
    df["upper_lim"] = np.nan

    start_idx = df.columns.get_loc("limit_file") + 1
    cols = df.columns[start_idx:]

    def _is_number(x):
        try:
            if isinstance(x, (bool, np.bool_)):
                return False
            float(x)
            return True
        except Exception:
            return False

    def _normalise(v):
        try:
            if isinstance(v, (bool, np.bool_)):
                return str(v)
            f = float(v)
            return str(int(f)) if f.is_integer() else str(v)
        except Exception:
            return str(v)

    def _process_one(row):
        values = list(row[cols])

        first_nan = next((i for i, val in enumerate(values)
                          if pd.isna(val)), None)
        active = values if first_nan is None else values[:first_nan]

        if (len(active) >= 2 and
                _is_number(active[-2]) and
                _is_number(active[-1])):

            try:
                lower = float(active[-2])
                upper = float(active[-1])
            except Exception:
                lower = upper = np.nan

            row["lower_lim"] = lower
            row["upper_lim"] = upper

            remaining = active[:-2]
            row[output_col] = "".join(_normalise(v) for v in remaining)

        else:
            row["lower_lim"] = np.nan
            row["upper_lim"] = np.nan
            row[output_col] = "".join(_normalise(v) for v in active)

        return row

    return df.apply(_process_one, axis=1)


# =============================================================================
# main
# =============================================================================

def main(limit_dir, limit_version):
    """
    Main routine for expanding ranges and concatenating limit strings.

    Parameters
    ----------
    limit_dir : str
        Directory containing limit CSV files.
    limit_version : {"v0", "v1"}
        Version of limit file format.

    Returns
    -------
    df : pd.DataFrame
        Output dataframe after transformation.
    """

    os.chdir(limit_dir)
    file_paths = glob.glob("*.csv")

    df = pd.DataFrame()
    for file_path in file_paths:
        df_tmp = pd.read_csv(file_path)
        df_tmp["limit_file"] = file_path[:-4]
        df = pd.concat([df, df_tmp])

    if limit_version == "v0":

        df = df[["limit_file", "metric", "lowerRange", "upperRange"]]
        df = df.reset_index(drop=True)
        df.to_excel("all_lims_v0.xlsx")

        return df

    elif limit_version == "v1":

        # ensure limit_file leading column
        df = df[["limit_file"] + [c for c in df.columns if c != "limit_file"]]

        df = expand_ranges_all_cols(df)
        df = concat_after_limit_file_deux(df, output_col="concatenated")
        df = df.reset_index(drop=True)

        df.to_excel("all_lims_v1.xlsx")

        return df

    else:
        raise ValueError("limit_version must be 'v0' or 'v1'")


# standard execution block
if __name__ == "__main__":
    # Example usage:
    df_out = main(r"C:\GitHub\jm_post_processing\20251103_BiT_analysis\lims_new", "v1")
    pass