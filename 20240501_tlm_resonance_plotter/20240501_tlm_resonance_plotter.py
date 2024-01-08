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


file_path = r'C:\Users\jmitchell\Downloads\Points_1001'
map_tlm = np.genfromtxt(r'C:\Users\jmitchell\Downloads\OP_231204-10_20_23-MCR1_Rig2__QR440-0329-00077_1001_nPoints_tx_Beam1_27.50_31.00_GHz_28.50_GHz_45C.csv', skip_header=2, dtype=float, delimiter=',')

def find_measFiles(path, fileString, beam):
    global measFiles, files
    files = []
    for root, directories, file in os.walk(path):
        for file in file:
            if (file.endswith(".csv")) == True:
                files.append(os.path.join(root, file))
    measFiles = []
    for i in range(len(files)):
        if fileString in files[i] and 'eam' + str(beam) in files[i]:
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

for beam in [1,2]:
    find_measFiles(file_path, 'OP_2', beam)
    
    for measFile in measFiles:
        load__measFiles(measFile)
        freq = float(meas_params['f_c'])
        plt.figure(figsize=(9,6))
        for j in range(len(meas_array_gain)):
            loc_min = np.argmin((meas_frequencies-(freq-0.5))**2)
            loc_max = np.argmin((meas_frequencies-(freq+0.5))**2)
            loc = np.argmin((meas_frequencies-freq)**2)
            if max(meas_array_gain[j,:][loc_min:loc_max]) - min(meas_array_gain[j,:][loc_min:loc_max]) > 13:
                plt.plot(meas_frequencies, meas_array_gain[j,:], label='port'+str((j+1)%152))
            else:
                plt.plot(meas_frequencies, meas_array_gain[j,:], 'k', alpha=0.1)
        plt.legend(fontsize=8, loc='lower left')
        plt.axvline(x=(freq-0.5))
        plt.axvline(x=(freq+0.5))
        plt.axvline(x=freq, color='k',linestyle='--')
        plt.xlabel('freq [GHz]')
        plt.ylabel('S21 [dB]')
        plt.grid()
        plt.ylim([-20,40])
        plt.xlim([27.5, 31.0])
        plt.title(f'beam{beam}')
        plt.savefig(f'{freq}GHz_beam{beam}'+'.png')