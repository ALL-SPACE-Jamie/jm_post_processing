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
# import seaborn as sns
from matplotlib.markers import MarkerStyle
plt.close('all')

# definitions
def find_measFiles(path, fileString, beam, freq_set):
    global measFiles, files
    files = []
    for root, directories, file in os.walk(path):
        for file in file:
            if (file.endswith(".csv")) == True:
                files.append(os.path.join(root, file))
    measFiles = []
    for i in range(len(files)):
        if fileString in files[i] and 'eam' + str(beam) in files[i] and f'{freq_set}_GHz_4' in files[i] and f'teration_2' not in files[i]:
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

## code

# files
file_path = r'C:\Users\jmitchell\Downloads\P3Tx____'

# params
freq_set = '29.50'
beam = 1
freq_list = ['29.50', '28.00', '28.50', '29.00', '27.50', '30.00', '30.50', '31.00']
freq_list = ['29.50']
# freq_list = ['17.70', '18.20', '18.70', '19.20', '19.70', '20.20', '20.70', '21.20']

# run

df = pd.DataFrame()

plt.figure(figsize=(24,8))
gain_delta_array = np.zeros([456,0])
for beam in [1]:
    for freq_set in freq_list:  
        # 143
        find_measFiles(r'C:\Users\jmitchell\Downloads\MCR1_Rig1_TLM_00143', 'OP_2', beam, freq_set)
        load__measFiles(measFiles[0])
        col = np.argmin((meas_frequencies-float(freq_set))**2)
        gain_143 = meas_array_gain[:, col]
        plt.plot(gain_143, 'k', linewidth=3)
        
        find_measFiles(file_path, 'OP_2', beam, freq_set)
        for meas_file in measFiles[0:3]:
            load__measFiles(meas_file)
            col = np.argmin((meas_frequencies-float(freq_set))**2)
            gain_delta = (meas_array_gain[:, col]-gain_143).reshape(456,1)
            gain_delta_array = np.concatenate((gain_delta_array, gain_delta), axis=1)
            plt.plot(meas_array_gain[:, col])
# plt.hist(gain_delta_array[0,:], bins=11)


stop
plt.figure(figsize=(12,8))
for i in range(int(len(gain_delta_array))):
    port_gain_log = gain_delta_array[i,:]
    median = np.median(port_gain_log)
    # median = 0.0
    # plt.plot([i,i], [np.min(port_gain_log), np.max(port_gain_log)],'r--')
    # plt.plot([i,i], [median-np.std(port_gain_log), median+np.std(port_gain_log)],'k-', linewidth=3)
    plt.plot(i, median, 'bx')
    # plt.plot(i, np.std(port_gain_log), 'ko')
    # plt.plot(i, np.max(port_gain_log)-np.min(port_gain_log), 'ro')
plt.grid()
        

plt.figure(figsize=(24,8))
for i in range(int(len(gain_delta_array))):
    plt.plot(gain_delta_array[i,:])
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

