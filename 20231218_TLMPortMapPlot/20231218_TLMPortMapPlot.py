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


file_path = r'C:\Users\jmitchell\OneDrive - ALL.SPACE\I-Type\Tx_TLM_I-Type\TLM_Calibration_Measurements\Batch_7\Raw_Data'
map_tlm = np.genfromtxt(r'C:\Users\jmitchell\Documents\GitHub\Post-Processing\20230601_TLM-Comparison\Mrk1_S2000_TLM_TX_ArrayGeometry_V20062022_CalInfo.csv', skip_header=2, dtype=float, delimiter=',')

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


def plot_phaseDrift(deltaNew, title, cmin, cmax, cstp, f_set):
    global Z, Y
    x = []
    y=[]
    rot = []
    for i in range(len(map_tlm)):
        x.append(map_tlm[i,4])
        # x.append(map_tlm[i,4])
        y.append(map_tlm[i,5])
        # y.append(map_tlm[i,5])
        rot.append(map_tlm[i,8])
        # rot.append(map_tlm[i,8])
    x = np.array(x)
    y = np.array(y)

    plt.figure()
    print(meas_frequencies-f_set)
    col = np.argmin((meas_frequencies-f_set)**2)
    Z = deltaNew[:,col]#-np.mean(deltaNew)
    Z = Z[1:][::2]
    Y=3e8/(f_set*1e9)
    # Z = 1000.0*Z/360.0*Y

    m = MarkerStyle("s")
    m._transform.rotate_deg(float(rot[i]))
    cseg = int((cmax-cmin)/cstp)
    plt.scatter(x, y, c=Z, marker=m, s=50, edgecolors='black', cmap = cm.get_cmap('jet', cseg))
    plt.colorbar()

    plt.clim(cmin, cmax)
    plt.xlabel('X [mm]'); plt.ylabel('Y [mm]')
    plt.title(title)
    plt.tight_layout()
    
find_measFiles(file_path, 'OP_2', 1)
load__measFiles(measFiles[0])
plot_phaseDrift(meas_array_gain, 'Gain (arb.) [dB]', 10.0, 40.0, 0.5, float(meas_params['f_c']))
plot_phaseDrift(meas_array_phase, 'Phase (arb.) [dB]', 0.0, 360.0, 0.5, float(meas_params['f_c']))