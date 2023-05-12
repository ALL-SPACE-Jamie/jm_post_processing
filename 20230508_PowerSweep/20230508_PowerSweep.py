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
filePath = r'C:\codeRun\full_tlm_40db_QR00001-es2bu_45C\2023-05-09_17-58-32_Minicalrig_powersweep_1_QR00001-es2bu_45C'
beam=2
lens=3

# definitions
def find_measFiles(path, fileString, lens, beam):
    global measFiles, files
    files = []
    for root, directories, file in os.walk(path):
        for file in file:
            if (file.endswith(".csv"))==True:
                files.append(os.path.join(root,file))
    measFiles = []
    for i in range(len(files)):
        if fileString in files[i] and 'eam' + str(beam) in files[i] and 'LENS_' + str(lens) in files[i]:
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

## run
with open('S2000_TX_RFIC_CHANNEL_MAP.json') as json_file:
    S2000_TX_RFIC_CHANNEL_MAP = json.load(json_file)
with open('S2000_TX_RFIC_PORT_MAP.json') as json_file:
    S2000_TX_RFIC_PORT_MAP = json.load(json_file)

fig, axs = plt.subplots(4, 2, figsize=(15, 10))
find_measFiles(filePath, 'P_SWEEP', lens, beam)
for file in measFiles:
    load__measFiles(file)
    f_meas = float(f_c)*1.0
    f_col = np.argmin((meas_frequencies-float(f_meas))**2)
    if S2000_TX_RFIC_CHANNEL_MAP[str(port)] == [0, 'V']:
        axs[0,0].plot(meas_powers, meas_array_gain[:,f_col], 'o-', label = '(' + str(rfic) + ')' + ' ' + str(port))
    if S2000_TX_RFIC_CHANNEL_MAP[str(port)] == [0, 'H']:
        axs[0,1].plot(meas_powers, meas_array_gain[:,f_col], 'o-', label = '(' + str(rfic) + ')' + ' ' + str(port))
    if S2000_TX_RFIC_CHANNEL_MAP[str(port)] == [1, 'V']:
        axs[1,0].plot(meas_powers, meas_array_gain[:,f_col], 'o-', label = '(' + str(rfic) + ')' + ' ' + str(port))
    if S2000_TX_RFIC_CHANNEL_MAP[str(port)] == [1, 'H']:
        axs[1,1].plot(meas_powers, meas_array_gain[:,f_col], 'o-', label = '(' + str(rfic) + ')' + ' ' + str(port))
    if S2000_TX_RFIC_CHANNEL_MAP[str(port)] == [2, 'V']:
        axs[2,0].plot(meas_powers, meas_array_gain[:,f_col], 'o-', label = '(' + str(rfic) + ')' + ' ' + str(port))
    if S2000_TX_RFIC_CHANNEL_MAP[str(port)] == [2, 'H']:
        axs[2,1].plot(meas_powers, meas_array_gain[:,f_col], 'o-', label = '(' + str(rfic) + ')' + ' ' + str(port))
    if S2000_TX_RFIC_CHANNEL_MAP[str(port)] == [3, 'V']:
        axs[3,0].plot(meas_powers, meas_array_gain[:,f_col], 'o-', label = '(' + str(rfic) + ')' + ' ' + str(port))
    if S2000_TX_RFIC_CHANNEL_MAP[str(port)] == [3, 'H']:
        axs[3,1].plot(meas_powers, meas_array_gain[:,f_col], 'o-', label = '(' + str(rfic) + ')' + ' ' + str(port))
    chanCycle = [0,1,2,3]
    linCycle = ['V', 'H']
    for row in range(4):
        for col in range(2):
            axs[row,col].legend(); axs[row,col].set_xlabel('Frequency [GHz]'); axs[row,col].set_ylabel('S$_{21}$ [dB]')
            axs[row,col].set_ylim([-10,25]); axs[row,col].set_xlim([-30, 0.0])
            axs[row,col].set_yticks(np.linspace(-10, 25, num=int(35/5)+1))
            axs[row,col].grid('on')
            axs[row,col].legend(fontsize=8, ncol=5, loc='lower right')
            axs[row,col].set_title('C'+str(chanCycle[row])+'-'+linCycle[col])
beam = meas_info[[index for index in range(len(meas_info)) if 'Beam' in meas_info[index]][0]][1]
f_c = meas_info[[index for index in range(len(meas_info)) if '# f_c' in meas_info[index]][0]][1]
qr = meas_info[[index for index in range(len(meas_info)) if 'barcodes' in meas_info[index]][0]][1]
title = 'Board ' + qr + ', Lens ' + str(lens) + ', Beam' + str(beam) + ', f$_{set}$=' + str(f_c) + ', f$_{meas}$=' + str(f_meas) + ' GHz'
fig.suptitle(title, fontsize=25)
plt.tight_layout()
plt.savefig('C:\\codeRun\\powerSweepFigures\\'+title+'.png',dpi=400)
time.sleep(1)
plt.close('all')

print('fin.')