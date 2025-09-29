# -*- coding: utf-8 -*-
"""
Created on Tue Jul 22 12:27:46 2025

@author: jmitchell
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from datetime import datetime, timedelta

# inputs
customer = False
file_path = r"C:\scratch\20250722\input14.csv"

# inputs that are less likely to change
open_list = ['DONE', 'REMOVED', 'COMP', 'PASS']
start_date = datetime(2025,1,1)
end_date = datetime(2025,12,31)

# read in data frame
df = pd.read_csv(file_path, encoding='ISO-8859-1')
keys = df.keys()

# make a customer only data frame
df_customer = df[df['Issue Type'] == 'Customer NC']

# change the main data frame to the customer one if selected
if customer == True:
    df = df_customer.copy()

# deperate closed from open and split into new dataframes
df_open = df[~df['Status'].isin(open_list)]
df_closed = df[df['Status'].isin(open_list)]

# create some lists for created and resolved dates
# scrappy code, should be functioned up, does the job
date_list = []
value_list = []
date_list_created = []
created_list = []
date_list_resolved = []
resolved_list = []

for _, row in df.iterrows():
    date_str = row['Created']
    timestamp = datetime.strptime(date_str, '%d/%b/%y %I:%M %p')
    value_list.append(1)
    date_list_created.append(timestamp)
    created_list.append(1)
    
    if row['Status'] in ['NC Complete', 'NC Cancelled']:
        date_str = row['Updated']
        value_list.append(-1)
        timestamp = datetime.strptime(date_str, '%d/%b/%y %I:%M %p')
        date_list_resolved.append(timestamp)
        resolved_list.append(1)
        
    date_list.append(timestamp)
    
# created zipped lists for created and combined
# should be functioned up, but works fine
combined = sorted(zip(date_list_created, created_list))
date_list_created_sorted, created_list_sorted = zip(*combined)
date_list_created_sorted = list(date_list_created_sorted)
created_list_sorted = list(created_list_sorted)
created_list_sorted = np.cumsum(created_list_sorted)

combined = sorted(zip(date_list_resolved, resolved_list))
date_list_resolved_sorted, resolved_list_sorted = zip(*combined)
date_list_resolved_sorted = list(date_list_resolved_sorted)
resolved_list_sorted = list(resolved_list_sorted)
resolved_list_sorted = np.cumsum(resolved_list_sorted)

# interpolation function
def interpolate_to_grid(date_list, value_list, date_grid):
    grid_values = []
    idx = 0
    current_value = 0
    for day in date_grid:
        # Advance index if the next event is on or before this day
        while idx < len(date_list) and date_list[idx].date() <= day.date():
            current_value = value_list[idx]
            idx += 1
        grid_values.append(current_value)
    return grid_values

# interpolate
start_date = min(date_list_created_sorted[0], date_list_resolved_sorted[0])
end_date = max(date_list_created_sorted[-1], date_list_resolved_sorted[-1])
num_days = (end_date - start_date).days + 1
date_grid = [start_date + timedelta(days=i) for i in range(num_days)]

created_list_sorted_interp = interpolate_to_grid(date_list_created_sorted, created_list_sorted, date_grid)
resolved_list_sorted_interp = interpolate_to_grid(date_list_resolved_sorted, resolved_list_sorted, date_grid)

# figure
fig, axs = plt.subplots(nrows=2, ncols=1, figsize=(4,7))
axs[0].set_facecolor('#000033')
axs[1].set_facecolor('#000033')
axs[0].plot(date_grid, np.array(created_list_sorted_interp), 'r', linewidth=4, label='NCs Created')
axs[0].plot(date_grid, np.array(resolved_list_sorted_interp), 'g', linewidth=4, label='NCs Closed')
axs[1].plot(date_grid, np.array(created_list_sorted_interp)-np.array(resolved_list_sorted_interp), 'white', linewidth=4,  label='NCs Open')

# limits
if customer == False:
    y_lim_max = 350
    y_lim_open = 150
if customer == True:
    y_lim_max = 50
    y_lim_open = 20
axs[0].set_xlim(datetime(2025, 5, 1), datetime(2025, 10, 1))
y_lim_max_50 = ((max(created_list_sorted_interp) + 49) // 50) * 50
axs[0].set_ylim([0,y_lim_max])

axs[1].set_xlim(datetime(2025, 5, 1), datetime(2025, 10, 1))
axs[1].set_ylim([0,y_lim_open])

# axes
axs[0].set_xlabel('Date')
for label in axs[0].get_xticklabels():
    label.set_rotation(45)
for label in axs[1].get_xticklabels():
    label.set_rotation(45)
axs[1].set_xlabel('Date')

# grids
axs[0].grid(True)
axs[0].legend(loc='lower right')
axs[1].grid(True)
axs[1].legend(loc='upper right')

# figure formatting and saving
open_no = list(np.array(created_list_sorted_interp)-np.array(resolved_list_sorted_interp))[-1]
if customer is True:
    plt.suptitle(f'Gen1 Customer NCs (HIGH PRIO.) \n {open_no} Open')
else:
    plt.suptitle(f'Gen1 NCs (HIGH PRIO.) \n {open_no} Open')

fig.tight_layout()
plt.savefig(rf'C:\scratch\figs\NC_HighPrio_Customer{customer}.png', dpi=200)
