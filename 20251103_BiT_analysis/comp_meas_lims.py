# -*- coding: utf-8 -*-
"""
CSV Measurement Processor
Created on Mon Oct 27 10:58:41 2025
@desc: Match measured limits to v1 processed limits, attach limit ranges,
       compute derived statistics, and write updated limit workbook.
@author: jmitchell
"""

import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt; plt.close('all')


# =============================================================================
# functions
# =============================================================================

def normalize_status(s):
    """
    Normalise log status names to consistent mapping keys.

    Parameters
    ----------
    s : str
        Raw log status string.

    Returns
    -------
    str
        Normalised log name.
    """
    # most specific → least specific
    if s.startswith("logStatusCombiner"):
        suffix = s[len("logStatusCombiner"):]
        return f"COMBINER_{suffix}"

    elif s.startswith("logProcStatus"):
        suffix = s[len("logProcStatus"):]
        return f"{suffix}_PROCESSOR_STATUS"

    elif s.startswith("logStatus"):
        return s[len("logStatus"):]

    else:
        return s


# =============================================================================
# load inputs
# =============================================================================

generation = 1

meas_lims = pd.read_excel(
    r"C:\GitHub\jm_post_processing\20251103_BiT_analysis\lims_current\meas_lims.xlsx",
    engine="openpyxl"
)

all_lims = pd.read_excel(
    r"C:\GitHub\jm_post_processing\20251103_BiT_analysis\lims_new\all_Lims_v1.xlsx",
    engine="openpyxl"
)

with open("bit_configuration.json", "r") as f:
    bit_configuration = json.load(f)


# =============================================================================
# match to limit file
# =============================================================================

meas_lims["files_found"] = "yes"
meas_lims["lim_min"] = np.nan
meas_lims["lim_max"] = np.nan

for idx in range(len(meas_lims)):

    row = meas_lims.iloc[idx]

    # restrict v1 limits by matching parameter substring
    all_lims_param = all_lims[
        all_lims["concatenated"].str.contains(row["param"], na=False)
    ]

    # normalised log name
    norm_log = normalize_status(row["log_name"])

    # lookup INPUT_FILE for this log and generation
    input_file = bit_configuration[norm_log]["INPUT_FILE"][f"GEN{generation}"]["NPI"]

    # fallback: if mapping does not return a string
    if not isinstance(input_file, str):
        input_file = row["test"]

    if len(input_file) > 0:

        # filter to matching limit_file
        all_lims_param_limitfile = all_lims_param[
            all_lims_param["limit_file"] == input_file
        ]

        if len(all_lims_param_limitfile) > 0:

            # debug if multiple matches found
            if len(all_lims_param_limitfile) > 1:
                print(f"Limit {idx}: {str(len(all_lims_param_limitfile))} limit matches")
                

            meas_lims.loc[idx, "lim_min"] = all_lims_param_limitfile["lower_lim"].iloc[0]
            meas_lims.loc[idx, "lim_max"] = all_lims_param_limitfile["upper_lim"].iloc[0]

        else:
            meas_lims.loc[idx, "files_found"] = "no limit found"
            meas_lims.loc[idx, ["lim_min", "lim_max"]] = [np.nan, np.nan]

    else:
        meas_lims.loc[idx, "files_found"] = "no test found"
        meas_lims.loc[idx, ["lim_min", "lim_max"]] = [np.nan, np.nan]


# =============================================================================
# derived columns
# =============================================================================

meas_lims["lim_mid"] = meas_lims["lim_max"] - (meas_lims["lim_max"] - meas_lims["lim_min"]) / 2
meas_lims["lim_range"] = meas_lims["lim_max"] - meas_lims["lim_min"]

meas_lims["meas_max"] = meas_lims["av"] + meas_lims["std"] * 2.0
meas_lims["meas_min"] = meas_lims["av"] - meas_lims["std"] * 2.0
meas_lims["meas_range"] = meas_lims["meas_max"] - meas_lims["meas_min"]

meas_lims["av/std"] = meas_lims["av"] / meas_lims["std"]
meas_lims["lim_range/meas_range"] = meas_lims["lim_range"] / meas_lims["meas_range"]


# =============================================================================
# quick diagnostic plot
# =============================================================================

plt.figure()
plt.plot(meas_lims["lim_range/meas_range"], "o", label="lim_range/meas_range")
plt.plot(meas_lims["av/std"], "o", label="meas_av/meas_std")
plt.yscale("log")
plt.legend()


# =============================================================================
# write-out
# =============================================================================

meas_lims.to_excel(
    r"C:\GitHub\jm_post_processing\20251103_BiT_analysis\lims_new\comp_meas_lims.xlsx",
    index=True
)