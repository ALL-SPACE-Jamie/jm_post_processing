import pandas as pd
import numpy as np
import matplotlib.pyplot as plt; plt.rcParams['font.size'] = 12
from scipy.stats import norm
import os
import glob
import copy
import csv
import json
import time
from pylab import *
plt.close('all')

# file path
dirScript = os.getcwd()

# parmas
filePath = r'C:\Users\JamieMitchell\Downloads\example'

# definitions
def find_measFiles(path, fileString, beam):
    global measFiles, files
    files = []
    for root, directories, file in os.walk(path):
        for file in file:
            if (file.endswith(".csv"))==True:
                files.append(os.path.join(root,file))
    measFiles = []
    for i in range(len(files)):
        if fileString in files[i] and 'eam' + str(beam) in files[i]:
            measFiles.append(files[i])
            
def load__measFiles(filePath):
    global meas_info, meas_array, meas_frequencies, meas_params, meas_array_gain, meas_array_phase, meas_powers, f_s, port, rfic, f_c
    meas_params = {}
    meas_info = []
    # meas_info, array and measurement frequencies
    with open(filePath, 'r') as file:
        filecontent = csv.reader(file, delimiter=',')
        time.sleep(0.10)
        for row in filecontent:
            meas_info.append(row)
        index_start = [index for index in range(len(meas_info)) if 'barcodes' in meas_info[index]][0]+2
        meas_info = meas_info[0:index_start]
        f_c = meas_info[[index for index in range(len(meas_info)) if '# f_c' in meas_info[index]][0]][1]
        port = filePath.split('\\')[-1].split('_')[filePath.split('\\')[-1].split('_').index('PORT')+1]
        rfic = filePath.split('\\')[-1].split('_')[filePath.split('\\')[-1].split('_').index('RFIC') + 1]

        meas_array = np.genfromtxt(filePath, delimiter=',', skip_header=index_start)[:,1:]
        meas_array_gain = meas_array[:,::2]
        meas_array_phase = meas_array[:,1:][:,::2]
        meas_frequencies = np.array(meas_info[index_start-1])[1:][::2].astype(float)
        meas_powers = np.genfromtxt(filePath, delimiter=',', skip_header=index_start)[:,0]
        
find_measFiles(filePath, 'P_SWEEP', 1)
for measFile in measFiles:
    load__measFiles(measFile)
    f_meas = float(f_c)*1.0
    f_col = np.argmin((meas_frequencies-float(f_meas))**2)
    plt.plot(meas_powers, meas_array_gain[:,f_col])