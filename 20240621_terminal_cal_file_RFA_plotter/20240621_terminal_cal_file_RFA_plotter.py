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
from matplotlib.markers import MarkerStyle
import zipfile
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
        if fileString in files[i] and 'eam' + str(beam) in files[i] and f'{f_set}_GHz_4' in files[i]:# and f'teration_{it}' in files[i]:
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



file_path = r'C:\scratch\20240621'
f_set = '19.70'
cal_folders = [d for d in os.listdir(file_path) if os.path.isdir(os.path.join(file_path, d))]
all_files = []
for cal_folder in cal_folders:
    path = os.path.join(file_path, cal_folder)
    for root, directories, file in os.walk(path):
        for file in file:
            if 'All' in file:
                all_files.append(os.path.join(root, file))

extracted_paths = []
for all_file_path in all_files:
    with zipfile.ZipFile(all_file_path, 'r') as zip_ref:
        zip_ref.extractall(all_file_path[0:-4]+'_extract')
        extracted_paths.append(all_file_path[0:-4]+'_extract')

meas_files_dict = {}
for extracted_path in extracted_paths:
    find_measFiles(extracted_path, 'RFA', 1, f'{f_set}', 1)
    # print(measFiles)
    meas_files_dict[extracted_path] = measFiles

ports = 288

plt.figure()
terminal_log = []
median_log = []
average_array = np.zeros([len(list(meas_files_dict.keys())), ports])
count = 0
for key in list(meas_files_dict.keys()):
    measFiles = meas_files_dict[key]
    tlm_array = np.zeros([ports,18])
    for idx in range(len(measFiles)):
        measFile = measFiles[idx]
        load__measFiles(measFile)
        col = np.argmin((meas_frequencies-float(f_set))**2)
        tlm_array[:,idx] = meas_array_gain[:,col]
    
    x = np.linspace(1,ports, num=ports)
    average = np.median(tlm_array, axis=1)
    average_array[count,:] = average
    stdev = np.std(tlm_array, axis=1)
    plt.plot(x, average, '--', label=key.split('\\')[-2])
    plt.fill_between(x, average-2.0*stdev, average+2.0*stdev,alpha=0.5)
    
    string_loc = [i for i, s in enumerate(measFile.split('\\')[-1].split('_')) if '45C' in s][-1]
    proc_type = measFile.split('\\')[-1].split('_')[string_loc:]
    print(measFile)
    print(proc_type)
    print('----')
    terminal_log.append(key.split('\\')[-2] +  '\n' + meas_params['date time'] + '\n' + str(proc_type))
    median_log.append(np.median(average))
    
    count = count + 1
    
plt.legend()
plt.ylim([0,20])
plt.grid()
plt.ylabel('RFA [dB]')
plt.title(f'{f_set} GHz')

plt.figure()
plt.bar(terminal_log, median_log)
plt.ylabel('Median RFA value [dB]')
plt.xticks(fontsize=6)
plt.title(f'{f_set} GHz')
plt.ylim([0,15])
plt.grid()

plt.figure()
plt.hist(median_log)

plt.figure()
plt.plot(x, np.std(average_array, axis=0))


    
                
    





