# -*- coding: utf-8 -*-
"""
Created on Mon Oct 27 10:58:41 2025

@author: jmitchell
"""

import pandas as pd
import os
import glob
import json
import numpy as np

new=True
gen=1

# functions
def expand_ranges_all_cols(df):
    """
    Expand rows where ANY column contains a range like '1-3'.
    Works across all dataframe columns automatically.
    
    Returns:
        pd.DataFrame
    """
    
    expanded_rows = []

    for _, row in df.iterrows():

        # Start with a single version of this row
        expanded = [row]

        # Loop through all columns
        for col in df.columns:
            new_expanded = []

            for r in expanded:
                cell = r[col]

                # Detect a range "x-y"
                if isinstance(cell, str) and "-" in cell:
                    part1, part2 = cell.split("-")
                    try:
                        start, end = int(part1), int(part2)
                        # Create new rows for each value
                        for v in range(start, end + 1):
                            new_r = r.copy()
                            new_r[col] = v
                            new_expanded.append(new_r)
                    except ValueError:
                        # Not a numeric range → treat as normal string
                        new_expanded.append(r)
                else:
                    new_expanded.append(r)

            expanded = new_expanded

        expanded_rows.extend(expanded)

    return pd.DataFrame(expanded_rows)


def concat_after_limit_file_deux(df, output_col="concatenated"):
    """
    For each row:
      - Look at columns after 'limit_file'
      - Consider values up to (but not including) the first NaN ("active" segment)
      - If the active segment ends with two numbers (i.e., pattern is number, number, then NaNs only):
          * Move those two numbers to 'lower_lim' and 'upper_lim'
          * Concatenate the remaining active values (no spaces)
      - Else:
          * No limits extracted
          * Concatenate the entire active segment (no spaces)
      - During concatenation, normalise integer-like numbers (e.g., '0.0' → '0').
    """

    if "limit_file" not in df.columns:
        raise ValueError("'limit_file' column not found in dataframe")

    # Prepare output columns
    df = df.copy()
    df["lower_lim"] = np.nan
    df["upper_lim"] = np.nan

    # Columns after 'limit_file'
    start_idx = df.columns.get_loc("limit_file") + 1
    cols = df.columns[start_idx:]

    def is_number(x):
        """Return True if x can be parsed as a number (int/float)."""
        try:
            # Reject booleans (they are instances of int in Python)
            if isinstance(x, (bool, np.bool_)):
                return False
            float(x)
            return True
        except Exception:
            return False

    def normalise(v):
        """
        Normalise values for concatenation:
          - If numeric and integer-like (e.g., 0.0), render as '0'
          - Otherwise, return original string representation unchanged
        """
        try:
            # Avoid treating booleans as numbers
            if isinstance(v, (bool, np.bool_)):
                return str(v)
            f = float(v)
            if f.is_integer():
                return str(int(f))
            # Keep original formatting for non-integers
            return str(v)
        except Exception:
            return str(v)

    def process_row(row):
        values = list(row[cols])  # keep order

        # Find first NaN (defines end of "active" segment)
        first_nan_idx = None
        for i, v in enumerate(values):
            if pd.isna(v):
                first_nan_idx = i
                break

        active = values if first_nan_idx is None else values[:first_nan_idx]

        # Check strict pattern: active ends with two numbers
        if len(active) >= 2 and is_number(active[-2]) and is_number(active[-1]):
            # Extract limits
            try:
                lower = float(active[-2])
                upper = float(active[-1])
            except Exception:
                lower = upper = np.nan

            remaining = active[:-2]
            row["lower_lim"] = lower
            row["upper_lim"] = upper
            row[output_col] = "".join(normalise(v) for v in remaining)
        else:
            # No limits; concatenate entire active segment
            row["lower_lim"] = np.nan
            row["upper_lim"] = np.nan
            row[output_col] = "".join(normalise(v) for v in active)

        return row

    return df.apply(process_row, axis=1)




## old format concatonated
if new==False:
    os.chdir(r'C:\GitHub\jm_post_processing\20251103_BiT_analysis\lims_current')
    file_paths = glob.glob('*.csv')
    
    df = pd.DataFrame()
    for file_path in file_paths:
        df_file_path = pd.read_csv(file_path)
        df_file_path['limit_file']=file_path[0:-4]
        df = pd.concat([df, df_file_path])

    new_column_order = ['limit_file', 'metric', 'lowerRange', 'upperRange']
    df = df[new_column_order]
    df = df.reset_index(drop=True)
    df.to_excel('all_lims.xlsx')

## new format
if new==True:
    # map
    os.chdir(r'C:\GitHub\jm_post_processing\20251103_BiT_analysis')
    bit_configuration = pd.read_json('bit_configuration.json')
    
    # all_lims concatonated
    os.chdir(r'C:\GitHub\jm_post_processing\20251103_BiT_analysis\lims_new')
    file_paths = glob.glob('*.csv')
    
    df = pd.DataFrame()
    for file_path in file_paths:
        df_file_path = pd.read_csv(file_path)
        df_file_path['limit_file']=file_path[0:-4]
        df = pd.concat([df, df_file_path])
    
    df = df[['limit_file'] + [c for c in df.columns if c != 'limit_file']]
    df = expand_ranges_all_cols(df)
    df = concat_after_limit_file_deux(df, output_col="concatenated")
    df = df.reset_index(drop=True)
    
    df.to_excel('all_lims_new.xlsx')
    
