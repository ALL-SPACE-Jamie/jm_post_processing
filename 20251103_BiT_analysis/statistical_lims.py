# -*- coding: utf-8 -*-
"""
Created on Mon Oct 27 10:58:41 2025

@author: jmitchell
"""

import pandas as pd
import os
import glob
import numpy as np
import matplotlib.pyplot as plt

file_path = (r'C:\scratch\20251103')
file_strings = ['logProcStatusFAN', '.csv', 'NPI Pre Check TLMs Fitted', 'PASS']

def find_meas_files(path, file_strings):
    files = []
    for root, directories, file in os.walk(path):
        for file in file:
            if (file.endswith(".csv")) == True:
                files.append(os.path.join(root, file))
    meas_files = []
    for i in range(len(files)):
        append = True
        for file_string in file_strings:
            if file_string not in files[i]:
                append = False
            if append == True:
                meas_files.append(files[i])

    return meas_files

meas_files = find_meas_files(file_path, file_strings)
fnames = [item.split('\\')[-1] for item in meas_files]
array_list = []

for meas_file in meas_files:
    np_array = np.genfromtxt(meas_file, delimiter=',', skip_header=11, dtype=None, encoding=None)
    array_list.append(np_array)
final_3d_array = np.stack(array_list, axis=0)

column_data = final_3d_array[:, 1:, 2] 

def safe_to_float(value):
    """Attempts to convert a value to float, returns NaN if it fails."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return np.nan

vectorized_safe_to_float = np.vectorize(safe_to_float)

numeric_column_data = vectorized_safe_to_float(column_data).astype(float)

average_value = np.nanmean(numeric_column_data, axis=0)
std_value = np.std(numeric_column_data, axis=0)

# plot
measurement_params = final_3d_array[0, 1:, 1]
x_positions = np.arange(len(measurement_params))
fig, ax = plt.subplots(figsize=(8, 6))

ax.bar(x_positions, average_value, yerr=std_value, capsize=5, color='skyblue', ecolor='black', width=0.6)

# Set the y-axis to a logarithmic scale
# ax.set_yscale('log')

ax.set_ylabel('Values')
ax.set_xticks(x_positions) # Set the tick locations
ax.set_xticklabels(measurement_params) # Set the measurement names as labels
ax.yaxis.grid(True, which='both', linestyle='--', linewidth=0.5) # Add grid lines

plt.xticks(rotation=45, ha='right')
# Display the plot
plt.tight_layout() # Adjust layout to prevent labels from being cut off
plt.show()

