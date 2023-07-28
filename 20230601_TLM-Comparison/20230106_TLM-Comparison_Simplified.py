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

f_set_list = [27.5, 28, 28.5, 29, 29.5, 30, 30.5, 31]
f_set_list = [17.7, 18.2, 18.7, 19.2, 19.7, 20.2, 20.7, 21.2]
chop = False
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

# colMap = ['b','orange','g','r','purple','brown','pink','grey']
# plt.figure(figsize=(7,4))          
for beamChoice in range(2):
    beamChoice = beamChoice+1
    plt.figure(figsize=(7,4))
    count = 0
    for f_set in f_set_list:
        # plt.figure(figsize=(7,4))
        find_measFiles(r'C:\Scratch\ComparisonRx\1-16-8', 'OP', beamChoice)
        for measFile in measFiles:
            load_measFiles(measFile)
            if float(meas_params['f_c']) == float(f_set):
                if chop == True:
                    locLeft = np.argmin((meas_frequencies-(float(f_set)-0.25))**2); locRight = np.argmin((meas_frequencies-(float(f_set)+0.25))**2)
                if chop == False:
                    locLeft = 0; locRight = len(meas_frequencies)-1
                # if beamChoice == 1:
                #     plt.plot(meas_frequencies[locLeft:locRight+1], np.median(meas_array_gain, axis=0)[locLeft:locRight+1], color = colMap[count], linewidth = 5, label = str(f_set) + ' GHz')
                # if beamChoice == 2:
                #     plt.plot(meas_frequencies[locLeft:locRight+1], np.median(meas_array_gain, axis=0)[locLeft:locRight+1], color = colMap[count], linestyle = '--', linewidth = 5, label = str(f_set) + ' GHz')
                plt.plot(meas_frequencies[locLeft:locRight+1], np.median(meas_array_gain, axis=0)[locLeft:locRight+1], linewidth = 5, label = str(f_set) + ' GHz')
                count = count + 1
                # plt.fill_between(meas_frequencies, np.min(meas_array_gain, axis=0), np.max(meas_array_gain, axis=0), alpha=0.2, label = '\n Port min/max')
                temp = meas_array_gain*1.0
        plt.xlabel('Frequency [GHz]'); plt.ylabel('S$_{21}$ (arb.) [dB]')
        plt.ylim([10,50]); plt.xlim([17.7, 21.2]); plt.xlim([min(f_set_list), max(f_set_list)])
        plt.yticks(np.linspace(10, 50, num=int(40/5)+1))
        plt.grid('on')   
        # plt.legend(ncol=2, loc='lower right', fontsize=12)
        plt.tight_layout()
        plt.title('f_set = ' + str(f_set) + ' GHz, Beam ' + str(beamChoice))
        plt.title('Beam ' + str(beamChoice))
        plt.savefig('C:\\Scratch\\Figures\\' + 'f_set_' + str(f_set) + 'GHz_Beam_' + str(beamChoice) + '.png', dpi=400)