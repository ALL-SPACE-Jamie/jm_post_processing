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
filePath = r'C:\Users\jmitchell\Downloads\20231115'

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

find_measFiles(filePath, 'OP_2', 1, '28.5')
load__measFiles(measFiles[0])

xdata = np.linspace(1,len(meas_array_gain),len(meas_array_gain))
ydata = meas_frequencies.copy()
X, Y = np.meshgrid(ydata, xdata)
Z = meas_array_gain.copy()



fig, ax = plt.subplots(figsize=(6,6))

mycmap1 = plt.get_cmap('jet')




cf = ax.contourf(X,Y,Z, cmap=mycmap1)
fig.colorbar(cf, ax=ax)

plt.show()
