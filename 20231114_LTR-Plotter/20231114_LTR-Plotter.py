import pandas as pd
import numpy as np
import matplotlib.pyplot as plt;
plt.rcParams['font.size'] = 12
from scipy.stats import norm
import os
import glob
import copy
import csv
import json
import time
from pylab import *
colMap = ['r','g','b','k','m','c','r','g','b','k','m','c','r','g','b','k','m','c','r','g','b','k','m','c','r','g','b','k','m','c','r','g','b','k','m','c','r','g','b','k','m','c']

plt.close('all')

# file path
dirScript = os.getcwd()

# parmas
filePath = r'C:\Scratch\Cal_RFC_att0'

# definitions
def find_measFiles(path, fileString, notString):
    global measFiles, files
    files = []
    for root, directories, file in os.walk(path):
        for file in file:
            if (file.endswith(".csv")) == True:
                files.append(os.path.join(root, file))
    measFiles = []
    for i in range(len(files)):
        if fileString in files[i] and notString not in files[i]:
            measFiles.append(files[i])

def load__measFiles(filePath):
    global meas_info, meas_params, meas_array, meas_frequencies, meas_array_gain, meas_array_phase, paramName, index_start
    if os.path.getsize(filePath) > 2000:
        meas_params = {}
        meas_info = []
    
        # meas_info, array and measurement frequencies
        with open(filePath, 'r') as file:
            filecontent = csv.reader(file, delimiter=',')
            for row in filecontent:
                meas_info.append(row)
            index_start = [index for index in range(len(meas_info)) if '# vna_sweep_time_s' in meas_info[index][0]][0]
            meas_info = meas_info[0:index_start]
            meas_array = np.genfromtxt(filePath, delimiter=',', skip_header=index_start)
        
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

find_measFiles(filePath, 'LTR_r', 'ERROR')
load__measFiles(measFiles[0])
