# -*- coding: utf-8 -*-
"""
CSV Measurement Processor
Created on Mon Oct 27 10:58:41 2025
@desc: Load measurement CSVs matching substring filters, compute stats,
       optionally plot, and attach existing limits to produce an output table.
@author: jmitchell
"""

import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# =============================================================================
# functions
# =============================================================================

def process_measurements(meas_dir, file_strings, fig_save=False, fig_dir=r"C:\scratch\figs"):
    """
    Process measurement CSVs matching required substrings.

    Loads CSV files recursively under `meas_dir` whose full path contains all
    `file_strings`, extracts numeric data, computes mean/std, optionally plots,
    and returns a dataframe containing (param, av, std, n, test, log_name).

    Parameters
    ----------
    meas_dir : str
        Root directory to search for measurement CSV files.
    file_strings : list[str]
        Substrings that must be present in the file path (e.g., [test_type, log_name, ".csv", "PASS"]).
    fig_save : bool, optional
        Save summary figure, by default False.
    fig_dir : str, optional
        Directory to save figures (created if missing), by default r"C:\\scratch\\figs".

    Returns
    -------
    pd.DataFrame
        Dataframe with columns: ['test', 'log_name', 'param', 'av', 'std', 'n'].
    """

    # -------------------------------------------------------------------------
    # helpers
    # -------------------------------------------------------------------------

    def _find_meas_files(path, substrings):
        """Recursive search for CSVs whose full path contains all substrings."""
        matched = []
        for root, _, files in os.walk(path):
            for fname in files:
                if fname.endswith(".csv"):
                    full_path = os.path.join(root, fname)
                    if all(s in full_path for s in substrings):
                        matched.append(full_path)
        # deduplicate preserving order
        return list(dict.fromkeys(matched))

    def _safe_to_float(value):
        """Convert to float; NaN on failure."""
        try:
            return float(value)
        except (ValueError, TypeError):
            return np.nan

    # -------------------------------------------------------------------------
    # file discovery
    # -------------------------------------------------------------------------

    meas_files = _find_meas_files(meas_dir, file_strings)

    if not meas_files:
        raise RuntimeError(
            "No measurement files matched.\n"
            f"Path checked: {meas_dir}\n"
            f"Required substrings: {file_strings}\n"
            "Matching is performed on the full file path."
        )

    # -------------------------------------------------------------------------
    # load CSVs
    # -------------------------------------------------------------------------

    array_list = []
    for mf in meas_files:
        arr = np.genfromtxt(
            mf,
            delimiter=",",
            skip_header=11,
            dtype=None,
            encoding=None
        )
        if arr.size == 0:
            raise RuntimeError(f"Empty or unreadable CSV: {mf}")
        array_list.append(arr)

    final_3d_array = np.stack(array_list, axis=0)

    # -------------------------------------------------------------------------
    # extract numeric data and compute statistics
    # -------------------------------------------------------------------------

    column_data = final_3d_array[:, 1:, 2]
    numeric_column_data = np.vectorize(_safe_to_float)(column_data).astype(float)

    av = np.nanmean(numeric_column_data, axis=0)
    std = np.nanstd(numeric_column_data, axis=0)
    measurement_params = final_3d_array[0, 1:, 1]

    # -------------------------------------------------------------------------
    # plot
    # -------------------------------------------------------------------------
    if fig_save is True:

        os.makedirs(fig_dir, exist_ok=True)

        x = np.arange(len(measurement_params))
        fig, ax = plt.subplots(figsize=(24, 6))

        ax.bar(
            x, av,
            yerr=std,
            capsize=5,
            color='white',
            ecolor='black',
            width=0.6
        )

        for row in numeric_column_data:
            ax.plot(x, row, 'k.', alpha=0.2)

        ax.set_ylabel('Values')
        ax.set_xticks(x)
        ax.set_xticklabels(measurement_params)
        ax.yaxis.grid(True, linestyle='--', linewidth=0.5)

        plt.xticks(rotation=90, ha='right')
        plt.title(f'{file_strings[0]}_{file_strings[1]}')
        plt.tight_layout()

        fig_path = os.path.join(fig_dir, f'{file_strings[0]}_{file_strings[1]}.png')
        plt.savefig(fig_path, dpi=200)
        plt.close(fig)

    # -------------------------------------------------------------------------
    # output dataframe
    # -------------------------------------------------------------------------

    new_lims = (
        pd.DataFrame({
            'param': measurement_params,
            'av': av,
            'std': std
        })
        .groupby('param', as_index=False).mean()
        .assign(n=len(meas_files))
    )

    new_lims['test'] = file_strings[0]
    new_lims['log_name'] = file_strings[1]

    # order columns
    new_lims = new_lims[['test', 'log_name', 'param', 'av', 'std', 'n']]

    return new_lims


def attach_existing_limits_v0(measured_df, existing_lims_path):
    """
    Attach existing limits (min/max) to the measured dataframe.

    The function matches each (log_name, param) against rows in the existing
    limits workbook. The workbook should contain columns: 'limit_file',
    'metric', 'lowerRange', 'upperRange'.

    Parameters
    ----------
    measured_df : pd.DataFrame
        Output from `process_measurements(...)`.
    existing_lims_path : str
        Path to the Excel workbook containing historical limits.

    Returns
    -------
    pd.DataFrame
        Dataframe with added 'lim_min' and 'lim_max' columns.
    """

    if not os.path.isfile(existing_lims_path):
        raise FileNotFoundError(f"Existing limits not found: {existing_lims_path}")

    all_lims = pd.read_excel(existing_lims_path, engine="openpyxl")

    def _normalize_for_lookup(name):
        # keep your previous lookup logic, wrapped for clarity
        return name.replace("logProcStatus", "").replace("logStatus", "")

    df = measured_df.copy()
    df['lim_min'] = np.nan
    df['lim_max'] = np.nan

    for idx in range(len(df)):
        entry = df.iloc[idx]

        log_name_search = _normalize_for_lookup(entry['log_name'])

        # filter by limit file and metric
        lims_cut = all_lims[
            all_lims['limit_file'].str.contains(log_name_search, case=False, na=False)
        ]
        lims_cut = lims_cut[
            lims_cut['metric'].str.contains(entry['param'], case=False, na=False)
        ]

        if len(lims_cut) > 0:
            df.loc[idx, 'lim_min'] = float(lims_cut['lowerRange'].iloc[0])
            df.loc[idx, 'lim_max'] = float(lims_cut['upperRange'].iloc[0])
        else:
            df.loc[idx, 'lim_min'] = 'No limits'
            df.loc[idx, 'lim_max'] = 'No limits'

    return df.fillna("NaN")


# =============================================================================
# main
# =============================================================================

def main(meas_dir,
         test_types,
         log_names,
         existing_lims_path,
         out_excel_path,
         fig_save=False,
         fig_dir=r"C:\scratch\figs"):
    """
    Run full workflow: process measurements, attach existing limits, write Excel.

    Parameters
    ----------
    meas_dir : str
        Root directory of measurement CSV files.
    test_types : list[str]
        List of test type substrings to match.
    log_names : list[str]
        List of log names to match.
    existing_lims_path : str
        Path to Excel file containing existing limits (v0 style).
    out_excel_path : str
        Path to write the final Excel output.
    fig_save : bool, optional
        Save plots, by default False.
    fig_dir : str, optional
        Directory to save plots, by default r"C:\\scratch\\figs".

    Returns
    -------
    pd.DataFrame
        Final dataframe written to Excel.
    """

    new_lims_all = pd.DataFrame(columns=["test", "log_name", "param", "av", "std", "n"])

    for test in test_types:
        for log in log_names:
            print(f'{test}, {log}')
            file_strings = [test, log, ".csv", "PASS"]

            try:
                lims = process_measurements(meas_dir, file_strings,
                                            fig_save=fig_save, fig_dir=fig_dir)
                new_lims_all = pd.concat([new_lims_all, lims], ignore_index=True)
            except Exception as ex:
                # continue on missing groups; keep loop resilient
                print(f'No matching files for: {test}, {log} ({ex})')
                continue

    # attach existing limits (v0 functionality only)
    # new_lims_all = attach_existing_limits(new_lims_all, existing_lims_path)

    # write output
    out_dir = os.path.dirname(out_excel_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    new_lims_all.to_excel(out_excel_path, index=True)

    return new_lims_all


# standard execution block
if __name__ == "__main__":
    # example usage
    meas_dir = r"C:\scratch\20251103"
    test_types = [
        "Prod PSU",
        "NPI Pre Check TLMs Fitted",
        "Prod Lower House CCU",
        #"NPI Pre Check NO TLMs",
        "NPI Pre Check NO",
        "NPI Pre Check TLMs"
    ]
    log_names = [
        'logProcStatusACU', 'logProcStatusCAL', 'logProcStatusFAN',
        'logProcStatusPCS', 'logProcStatusTLM', 'logProcStatusTMU',
        'logProcStatusTPB', 'logStatusACU', 'logStatusCombinerRFIC',
        'logStatusMPB', 'logStatusTLM', 'logStatusVN300'
    ]
    existing_lims_path = r"C:\GitHub\jm_post_processing\20251103_BiT_analysis\lims_current\all_Lims_v1.xlsx"
    out_excel_path = r"C:\GitHub\jm_post_processing\20251103_BiT_analysis\lims_new\meas_lims.xlsx"

    df = main(
        meas_dir=meas_dir,
        test_types=test_types,
        log_names=log_names,
        existing_lims_path=existing_lims_path,
        out_excel_path=out_excel_path,
        fig_save=False,
        fig_dir=r"C:\scratch\figs"
    )