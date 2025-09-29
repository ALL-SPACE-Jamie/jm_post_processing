# -*- coding: utf-8 -*-
"""
Created on Fri Sep 12 17:54:50 2025

@author: jmitchell
"""

import pandas as pd
import openpyxl
import matplotlib.pyplot as plt; plt.close('all')
plt.rcParams.update(plt.rcParamsDefault)
plt.rcParams.update({'font.size': plt.rcParams['font.size'] * 1.25})
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import math
import re


# load in data
df = pd.read_excel(r"C:\Users\jmitchell\OneDrive - ALL.SPACE\RF Testing\5 Laboratory\Sanmina\Yields\420-0361 Failure Aug-11Sep2025.xlsx")

# Loop through columns that contain 'Defect' in their name
defect_entries = []
for col in df.columns:
    if 'Defect' in col:
        # Drop NaNs and extend the list with valid entries
        defect_entries.extend(df[col].dropna().tolist())

split_entries = [re.split(r'[.:]', entry) for entry in defect_entries]
df_defects = pd.DataFrame(split_entries, columns=['Fault', 'Des', 'Component', 'Beam'])
df_defects['Fault'] = df_defects['Fault'].astype(str).str[:-3]


fault_counts = df_defects['Fault'].value_counts()

# Calculate cumulative percentage
cumulative_pct = fault_counts.cumsum() / fault_counts.sum() * 100

# Plotting
fig, ax1 = plt.subplots(figsize=(7,7))

# Bar chart for fault frequency
fault_counts.plot(kind='bar', color='skyblue', ax=ax1)
ax1.set_ylabel('Frequency')
ax1.set_title('PCS Faults (batch 3)')
plt.xticks(rotation=45)

# Line chart for cumulative percentage
ax2 = ax1.twinx()
cumulative_pct.plot(marker='o', color='darkred', ax=ax2)
ax2.set_ylabel('Cumulative %')
ax2.axhline(83, color='gray', linestyle='--')  # Optional: 80% threshold line

# Annotate cumulative % points
for i, pct in enumerate(cumulative_pct):
    ax2.annotate(f'{pct:.1f}%', (i, pct), textcoords="offset points", xytext=(0,5), ha='center')

plt.tight_layout()
plt.show()
fig.savefig('pareto.png', dpi=400)
