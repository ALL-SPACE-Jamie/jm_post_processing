# -*- coding: utf-8 -*-
"""
Created on Mon Oct 27 10:58:41 2025

@author: jmitchell
"""

import pandas as pd
import os
import glob

os.chdir(r'C:\scratch\20251014\all_lims')
file_paths = glob.glob('*.csv')

df = pd.DataFrame()
for file_path in file_paths:
    df_file_path = pd.read_csv(file_path)
    df_file_path['limit_file']=file_path[0:-4]
    df = pd.concat([df, df_file_path])

new_column_order = ['limit_file', 'metric', 'lowerRange', 'upperRange']
df = df[new_column_order]
df.to_excel('BiT_Lims.xlsx')