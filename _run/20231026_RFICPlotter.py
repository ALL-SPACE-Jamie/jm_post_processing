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
filePath = r'C:\Users\jmitchell\Downloads\iteration_1'

# definitions
def find_measFiles(path, fileString, beam, freqSelect):
    global measFiles, files
    files = []
    for root, directories, file in os.walk(path):
        for file in file:
            if (file.endswith(".csv")) == True:
                files.append(os.path.join(root, file))
    measFiles = []
    for i in range(len(files)):
        if fileString in files[i] and 'eam' + str(beam) in files[i] and 'rchive' not in files[i] and freqSelect in files[i]:
            measFiles.append(files[i])

def load__measFiles(filePath):
    global meas_info, meas_params, meas_array, meas_frequencies, meas_array_gain, meas_array_phase, paramName, i
    if os.path.getsize(filePath) > 2000:
        meas_params = {}
        meas_info = []
    
        # meas_info, array and measurement frequencies
        with open(filePath, 'r') as file:
            filecontent = csv.reader(file, delimiter=',')
            for row in filecontent:
                meas_info.append(row)
            index_start = [index for index in range(len(meas_info)) if 'barcodes' in meas_info[index]][0] + 2
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

plt.figure(figsize=(7,7))
find_measFiles(r'C:\Users\jmitchell\Downloads\iteration_1', 'TEM', 1, '17.7_GHz')
for measFile in measFiles:
    load__measFiles(measFile)
    plt.plot(meas_array[0,0], meas_array[0,4], 'rs')
    plt.plot(meas_array[0,0], meas_array[1,4], 'gs')
    plt.plot(meas_array[0,0], meas_array[2,4], 'bo')
    plt.plot(meas_array[0,0], meas_array[0,6], 'k.')
    plt.plot(meas_array[0,0], meas_array[1,6], 'k.')
    plt.plot(meas_array[0,0], meas_array[2,6], 'k.')
plt.plot(meas_array[0,0], meas_array[0,4], 'rs', label='RFIC lens 1')
plt.plot(meas_array[0,0], meas_array[1,4], 'gs', label='RFIC lens 2')
plt.plot(meas_array[0,0], meas_array[2,4], 'bo', label='RFIC lens 3')
plt.plot(meas_array[0,0], meas_array[0,6], 'k.', label='Plate lens 1')
plt.plot(meas_array[0,0], meas_array[1,6], 'k.', label='Plate lens 2')
plt.plot(meas_array[0,0], meas_array[2,6], 'k.', label='Plate lens 3')
plt.legend()
plt.xlim([0, 160])
plt.ylim([50, 80])
plt.xlabel('port')
plt.ylabel('Temperature [degC]')
plt.grid('on')
plt.title('Rx')
plt.tight_layout()



plt.figure(figsize=(7,7))
find_measFiles(r'C:\Users\jmitchell\Downloads\cal_port_temperatures', 'TEM', 1, '27.5_GHz')
for measFile in measFiles:
    load__measFiles(measFile)
    plt.plot(meas_array[0,0], meas_array[0,4], 'rs')
    plt.plot(meas_array[0,0], meas_array[1,4], 'gs')
    plt.plot(meas_array[0,0], meas_array[2,4], 'bo')
    plt.plot(meas_array[0,0], meas_array[0,6], 'k.')
    plt.plot(meas_array[0,0], meas_array[1,6], 'k.')
    plt.plot(meas_array[0,0], meas_array[2,6], 'k.')
plt.plot(meas_array[0,0], meas_array[0,4], 'rs', label='RFIC lens 1')
plt.plot(meas_array[0,0], meas_array[1,4], 'gs', label='RFIC lens 2')
plt.plot(meas_array[0,0], meas_array[2,4], 'bo', label='RFIC lens 3')
plt.plot(meas_array[0,0], meas_array[0,6], 'k.', label='Plate lens 1')
plt.plot(meas_array[0,0], meas_array[1,6], 'k.', label='Plate lens 2')
plt.plot(meas_array[0,0], meas_array[2,6], 'k.', label='Plate lens 3')
plt.legend()
plt.xlim([0, 160])
plt.ylim([50, 80])
plt.xlabel('port')
plt.ylabel('Temperature [degC]')
plt.grid('on')
plt.title('Tx')
plt.tight_layout()