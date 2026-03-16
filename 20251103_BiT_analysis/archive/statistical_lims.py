# -*- coding: utf-8 -*-
"""
CSV Measurement Processor
Created on Mon Oct 27 10:58:41 2025
Author: jmitchell
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def process_measurements(file_path, file_strings, fig_save=False):
    global measurement_params
    """
    Process measurement CSVs matching the required substrings.
    Loads all files, extracts numeric data, computes mean/std, plots results,
    and returns a dataframe containing (param, av, std, min, max, n).
    """

    # ----------------------------------------------------------
    # Helper functions
    # ----------------------------------------------------------

    def find_meas_files(path, substrings):
        """
        Recursively search for CSV files whose full path contains
        all required substrings. Returns a deduplicated list of paths.
        """
        matched = []
        for root, _, files in os.walk(path):
            for fname in files:
                if fname.endswith(".csv"):
                    full_path = os.path.join(root, fname)
                    if all(s in full_path for s in substrings):
                        matched.append(full_path)
        return list(dict.fromkeys(matched))

    def safe_to_float(value):
        """Convert value to float; return NaN if conversion fails."""
        try:
            return float(value)
        except (ValueError, TypeError):
            return np.nan

    # ----------------------------------------------------------
    # File discovery
    # ----------------------------------------------------------

    meas_files = find_meas_files(file_path, file_strings)
    log_names = [os.path.basename(d.rstrip(r"\/")).split('_')[0] for d in meas_files]
    log_names = list(dict.fromkeys(log_names))

    if not meas_files:
        raise RuntimeError(
            "No measurement files matched.\n"
            f"Path checked: {file_path}\n"
            f"Required substrings: {file_strings}\n"
            "Matching is performed on the full file path."
        )

    # ----------------------------------------------------------
    # Load CSVs
    # ----------------------------------------------------------

    array_list = []
    for mf in meas_files:
        arr = np.genfromtxt(
            mf,
            delimiter=',',
            skip_header=11,
            dtype=None,
            encoding=None
        )
        if arr.size == 0:
            raise RuntimeError(f"Empty or unreadable CSV: {mf}")
        array_list.append(arr)

    final_3d_array = np.stack(array_list, axis=0)

    # ----------------------------------------------------------
    # Extract numeric data and compute statistics
    # ----------------------------------------------------------

    column_data = final_3d_array[:, 1:, 2]
    numeric_column_data = np.vectorize(safe_to_float)(column_data).astype(float)

    average_value = np.nanmean(numeric_column_data, axis=0)
    std_value = np.nanstd(numeric_column_data, axis=0)
    measurement_params = final_3d_array[0, 1:, 1]

    # ----------------------------------------------------------
    # Plot
    # ----------------------------------------------------------
    if fig_save == True:
    
        x = np.arange(len(measurement_params))
        fig, ax = plt.subplots(figsize=(24, 6))
    
        ax.bar(
            x, average_value,
            yerr=std_value,
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
        plt.show()
        
        plt.savefig(f'C:\\scratch\\figs\\{file_strings[0]}_{file_strings[1]}.png', dpi=200)

    # ----------------------------------------------------------
    # Output dataframe
    # ----------------------------------------------------------

    new_lims = (
        pd.DataFrame({
            'param': measurement_params,
            'av': average_value,
            'std': std_value
        })
        .groupby('param', as_index=False).mean()
        .assign(
            n=len(meas_files)
        )
    )
    
    new_lims['test'] = file_strings[0]
    new_lims['log_name'] = file_strings[1]

    return new_lims


# ----------------------------------------------------------------------
# Process the measurements into measured ranges
# ----------------------------------------------------------------------

if __name__ == "__main__":
    file_path = r"C:\scratch\20251103"
    test_types = ["Prod PSU", "NPI Pre Check TLMs Fitted", "Prod Lower House CCU", "NPI Pre Check NO TLMs", "NPI Pre Check NO", "NPI Pre Check TLMs"]
    log_names = ['logProcStatusACU', 'logProcStatusCAL', 'logProcStatusFAN', 'logProcStatusPCS', 'logProcStatusTLM', 'logProcStatusTMU', 'logProcStatusTPB', 'logStatusACU', 'logStatusCombinerRFIC', 'logStatusMPB', 'logStatusTLM', 'logStatusVN300']
    
    new_lims = pd.DataFrame(columns=["test", "log_name", "param", "av", "std", "n"])

    for test_type in test_types:
        for log_name in log_names:
            plt.close('all')
            print(f'{test_type}, {log_name}')
            file_strings = [
                test_type,
                log_name,
                ".csv",
                "PASS"
            ]
            try:
                lims = process_measurements(file_path, file_strings, fig_save=False)
                new_lims = pd.concat([new_lims, lims], ignore_index=True)
            except:
                ('No file')

new_lims.to_excel(r"C:\GitHub\jm_post_processing\20251103_BiT_analysis\lims_current\meas_lims.xlsx")

# ----------------------------------------------------------
# Attach existing limits
# ----------------------------------------------------------

new_lims['lim_min'] = 0
new_lims['lim_max'] = 0

all_lims = pd.read_excel(
    r"C:\GitHub\jm_post_processing\20251103_BiT_analysis\lims_current\all_Lims.xlsx",
    engine="openpyxl"
)

# match the existing limits to the measured data
for idx in range(len(new_lims)):
    entry = new_lims.iloc[idx]

    # Normalise log_name
    log_name_search = (
        entry['log_name']
        .replace("logProcStatus", "")
        .replace("logStatus", "")
    )

    # Filter matching limit file and metric
    all_lims_cut = all_lims[
        all_lims['limit_file'].str.contains(log_name_search, case=False, na=False)
    ]
    all_lims_cut = all_lims_cut[
        all_lims_cut['metric'].str.contains(entry['param'], case=False, na=False)
    ]

    if len(all_lims_cut) > 0:
        new_lims.loc[idx, 'lim_min'] = float(all_lims_cut['lowerRange'].iloc[0])
        new_lims.loc[idx, 'lim_max'] = float(all_lims_cut['upperRange'].iloc[0])
    else:
        new_lims.loc[idx, 'lim_min'] = 'No limits'
        new_lims.loc[idx, 'lim_max'] = 'No limits'

# ----------------------------------------------------------
# Final write-out
# ----------------------------------------------------------

new_lims = new_lims.fillna("NaN")
new_lims.to_excel(r"C:\GitHub\jm_post_processing\20251103_BiT_analysis\lims_current\meas_lims.xlsx")

