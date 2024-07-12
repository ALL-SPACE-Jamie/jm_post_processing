# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 10:55:50 2024

@author: jmitchell
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt;
plt.rcParams['font.size'] = 12
import matplotlib.backends.backend_pdf
from matplotlib import cm, colors
from scipy.stats import norm
import os
import glob
import copy
import csv
import json
import time
from pylab import *
# import seaborn as sns
from matplotlib.markers import MarkerStyle
import datetime
plt.close('all')


def find_measFiles_matlab_txt(path, fileString):
    global files
    files = []
    for root, directories, file in os.walk(path):
        for file in file:
            if (file.endswith(".txt")) == True and fileString in file:
                full_file = os.path.join(root, file)
                file_name = full_file.split('\\')[-1]
                files.append(full_file)

file_path = r'C:\scratch\20240701'
find_measFiles_matlab_txt(file_path, '')

t = pd.date_range(start='2024-06-24', end='2024-07-01', periods=10001)
y = np.zeros([len(t)])

plt.figure()
for file in files:
    # print(file)
    text_file = open(file, "r")
    content = text_file.readlines()
    
    if '24' in file.split('\\')[-1]:
        
        start_index = file.split('\\')[-1].index('24')
        start_time_str = file.split('\\')[-1][start_index:start_index+1+11]
    
    
        
        try: 
            start_time = datetime.datetime.strptime(start_time_str, '%y%m%d %H-%M')
            # print('1 passed')
        except:
            # print('1')
            a=1
        try:
            start_time = datetime.datetime.strptime(start_time_str, '%y%m%d_%H_%M')
            # print('2 passed')
        except:
            a=2
            # print('2')
           
            
        for idx in range(len(content)):
            if 'Total execution' in content[idx]:
                line_no_exec = idx
                exec_time_str = content[idx].split(' ')[-1]
                hours, minutes, seconds = map(int, exec_time_str.split(':'))
                total_hours = hours + minutes / 60 + seconds / 3600
                end_time = start_time + datetime.timedelta(hours = total_hours)
            else:
                # print(f'NOT FOUND \n' + str(file.split('\\')[-1]) + '\n')
                a = 3
            if 'Total execution' in content[idx]:
                if 'P1' in file or 'P2' in file:
                    colour = 'g'
                else:
                    colour = 'b'
                plt.plot([start_time,start_time, end_time,end_time], [0,1,1,0], f'{colour}-')
                plt.fill_between([start_time, end_time], 1, color='r', alpha=0.5)
                for time_step in range(len(t)):
                    if start_time <= t[time_step] <= end_time:
                        y[time_step] = 1.0
            
plt.xlim([datetime.datetime(2024, 6, 1), datetime.datetime(2024, 7, 1)])
plt.ylim([-1,2])

plt.figure()
# plt.plot(t,y)
plt.fill_between(t, y, color='g', alpha=1.0)
# plt.fill_between(t, np.abs(y-1), color='r', alpha=1.0)
percentage_allocation = 100.0*(np.sum(y)/float(len(y)))

plt.figure()
plt.plot(t, np.cumsum(7*(percentage_allocation/100) * y/(np.sum(y))), color='g', linewidth=3.0, alpha=1.0)
plt.ylim([0,7])
plt.axhline(y=7*0.8, 'k--', linewidth=3.0, )
plt.title('Wk 26 automated CATR useage')
