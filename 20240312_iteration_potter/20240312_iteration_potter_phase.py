# -*- coding: utf-8 -*-
"""
Created on Mon Dec 18 16:40:42 2023

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
import seaborn as sns
from matplotlib.markers import MarkerStyle
plt.close('all')

# definitions
def find_measFiles(path, fileString, beam, freq_set, it):
    global measFiles, files
    files = []
    for root, directories, file in os.walk(path):
        for file in file:
            if (file.endswith(".csv")) == True:
                files.append(os.path.join(root, file))
    measFiles = []
    for i in range(len(files)):
        if fileString in files[i] and 'eam' + str(beam) in files[i] and f'{freq_set}_GHz_4' in files[i] and f'teration_{it}' in files[i]:
            measFiles.append(files[i])

def load__measFiles(file_path):
    global meas_info, meas_params, meas_array, meas_frequencies, meas_array_gain, meas_array_phase, paramName, i
    if os.path.getsize(file_path) > 2000:
        meas_params = {}
        meas_info = []
    
        # meas_info, array and measurement frequencies
        with open(file_path, 'r') as file:
            filecontent = csv.reader(file, delimiter=',')
            for row in filecontent:
                meas_info.append(row)
            index_start = [index for index in range(len(meas_info)) if 'barcodes' in meas_info[index]][0] + 2
            meas_info = meas_info[0:index_start]
            meas_array = np.genfromtxt(file_path, delimiter=',', skip_header=index_start)
            meas_array_gain = meas_array[:, ::2]
            meas_array_phase = meas_array[:, 1:][:, ::2]
            meas_frequencies = np.array(meas_info[index_start - 1])[::2].astype(float)
        
    # meas_params
    for i in range(len(meas_info) - 1):
        if len(meas_info[i]) > 1:
            paramName = meas_info[i][0]
            if paramName[0:2] == '# ':
                paramName = paramName[2:]
            meas_params[paramName] = meas_info[i][1]
            if len(meas_params[paramName]) > 0:
                if meas_params[paramName][0] == ' ':
                    meas_params[paramName] = meas_params[paramName][1:]


file_path = r'C:\Users\jmitchell\Downloads\5_iteration'
f_set_list = ['27.50', '29.00', '31.00']
fig, axs = plt.subplots(nrows=2, ncols=3, figsize=(30, 20))
for beam in [1,2]:
    for fig_no in [0,1,2]:
        f_set = f_set_list[fig_no]
        std_list = []
        for it in [1,2,3,4,5]:
            find_measFiles(file_path, 'OP_2', beam, f_set, it=it)
            load__measFiles(measFiles[0])
            col = np.argmin((meas_frequencies-float(f_set))**2)
            stdev = round(np.std(meas_array_phase[:,col]),2)
            pkpk = round(max(meas_array_phase[:,col])-min(meas_array_phase[:,col]),2)
            std_list.append(stdev)
            axs[beam-1, fig_no].plot(meas_array_phase[:,col], alpha=0.4, label=f'iteration {it}, stdev = {stdev}, pkpk = {pkpk}')
            axs[beam-1, fig_no].set_title(f'{f_set} GHz, beam {beam}')
            axs[beam-1, fig_no].set_xlabel('port')
            axs[beam-1, fig_no].set_ylabel('gain')
        ax2 = axs[beam-1, fig_no].twiny()
        ax2.plot([1,2,3,4,5],std_list, 'ro-')
        ax2.set_xlabel('iteation', color='red')
        ax2.set_xticks([1,2,3,4,5,6,7,8])
        axs[beam-1, fig_no].legend(loc='upper right')
        axs[beam-1, fig_no].set_ylim([-5,360])
        axs[beam-1, fig_no].grid()
plt.tight_layout()
plt.savefig('temp.pdf')