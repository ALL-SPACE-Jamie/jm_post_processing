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

f_set_list = [27.5, 28.0, 28.5, 29.0, 29.5, 30.0, 30.5, 31.0]
f_set_list = [17.7, 18.2, 18.7, 19.2, 19.7, 20.2, 20.7, 21.2]

# file path
dirScript = os.getcwd()
# definitions
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
            

def load_measFiles(filePath):
    global meas_info, meas_array, meas_frequencies, meas_params, meas_array_gain, meas_array_phase
    meas_params = {}
    meas_info = []
    # meas_info, array and measurement frequencies
    with open(filePath, 'r') as file:
        filecontent = csv.reader(file, delimiter=',')
        time.sleep(0.10)
        for row in filecontent:
            meas_info.append(row)
        index_start = [index for index in range(len(meas_info)) if 'barcodes' in meas_info[index]][0] + 2
        meas_info = meas_info[0:index_start]
        meas_array = np.genfromtxt(filePath, delimiter=',', skip_header=index_start)
        meas_array_gain = meas_array[:,::2]
        meas_array_phase = meas_array[:,1:][:,::2]
        meas_frequencies = np.array(meas_info[index_start - 1])[::2].astype(float)    
        
    # meas_params
    for i in range(len(meas_info) - 1):
        if len(meas_info[i]) > 1:
            paramName = meas_info[i][0]

            if paramName[0:2] == '# ':
                paramName = paramName[2:]
            meas_params[paramName] = meas_info[i][1]
            
for beamChoice in range(2):
    beamChoice = beamChoice+1
    for f_set in f_set_list:
        plt.figure()
        find_measFiles('C:\\Scratch', 'OP', beamChoice)
        for measFile in measFiles:
            load_measFiles(measFile)
            if float(meas_params['f_c']) == float(f_set):
                plt.plot(meas_frequencies, np.average(meas_array_gain, axis=0), label = meas_params['acu_version'] + ' Port mean')
                plt.fill_between(meas_frequencies, np.min(meas_array_gain, axis=0), np.max(meas_array_gain, axis=0), alpha=0.2, label = 'Port min/max')
        plt.xlabel('Frequency [GHz]'); plt.ylabel('S$_{21}$ (arb.) [dB]')
        plt.ylim([-10,50]); plt.xlim([17.7, 21.2]); plt.xlim([min(f_set_list), max(f_set_list)])
        plt.yticks(np.linspace(-10, 50, num=int(60/5)+1))
        plt.grid('on')   
        plt.legend(ncol=2, loc='lower right', fontsize=7)
        plt.tight_layout()
        plt.title('f_set = ' + str(f_set) + ' GHz, Beam ' + str(beamChoice))
        plt.savefig('C:\\Scratch\\Figures\\' + 'f_set_' + str(f_set) + 'GHz_Beam_' + str(beamChoice) + '.png', dpi=400)