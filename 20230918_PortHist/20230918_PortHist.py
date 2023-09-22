import pandas as pd
import numpy as np
import matplotlib.pyplot as plt; plt.rcParams['font.size'] = 12
from scipy.stats import norm
from scipy.stats import norm
import os
import glob
import copy
import csv
import json
import time
import math
import statistics
import shutil

plt.close('all')

# file path
dirScript = os.getcwd()

# parmas
filePath = r'C:\Users\JamieMitchell\Downloads\test2\20230606'
txrx = 'rx'

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
        if fileString in files[i] and 'eam' + str(beam) in files[i] and 'rchive' not in files[i]:
            measFiles.append(files[i])

def load__measFiles(filePath):
    global meas_info, meas_params, meas_array, meas_frequencies, meas_array_gain, meas_array_phase
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
            if meas_params[paramName][0] == ' ':
                meas_params[paramName] = meas_params[paramName][1:]

def dict__maps(txrx):
    global S2000_TX_RFIC_CHANNEL_MAP, S2000_TX_RFIC_PORT_MAP
    if txrx == 'rx':
        with open('rx_s2000_channel_map.json') as json_file:
            S2000_TX_RFIC_CHANNEL_MAP = json.load(json_file)
        with open('rx_s2000_rfic_map.json') as json_file:
            S2000_TX_RFIC_PORT_MAP = json.load(json_file)
    if txrx == 'tx':
        with open('S2000_TX_RFIC_CHANNEL_MAP.json') as json_file:
            S2000_TX_RFIC_CHANNEL_MAP = json.load(json_file)
        with open('S2000_TX_RFIC_PORT_MAP.json') as json_file:
            S2000_TX_RFIC_PORT_MAP = json.load(json_file)
            
def portSort():
    global port2IC, port2chan, ports, port2pol
    ports = np.linspace(1, len(meas_array_gain), num=len(meas_array_gain))
    port2IC = []
    port2chan = []
    port2pol = []
    for i in range(int(len(ports) / 3)):
        for j in range(len(S2000_TX_RFIC_PORT_MAP)):
            forCheck = S2000_TX_RFIC_PORT_MAP[str(j + 1)]
            if int(i + 1) in forCheck:
                port2IC.append(j + 1)
                port2chan.append(S2000_TX_RFIC_CHANNEL_MAP[str(i + 1)][0])
                port2pol.append(S2000_TX_RFIC_CHANNEL_MAP[str(i + 1)][1])

## run
freqLog = [17.7, 19.2, 20.2, 21.2]
for freq in freqLog:

    beam = 1
    dict__maps(txrx)
    find_measFiles(filePath, 'OP', beam)
    fig, axs = plt.subplots(4, 2, figsize=(25, 15))
    
    
    chanMap = ['0','1','2','3']
    polMap = ['V','H']
    
    for j in range(4):
        for k in range(2):
            selectedPorts = []
            for measFile in measFiles:
                load__measFiles(measFile)
                portSort()
                if meas_params['f_c'] == str(freq):
                    freqCol = np.argmin((meas_frequencies-freq)**2)
                    for l in range(len(port2chan)):
                        if port2chan[l] == int(chanMap[j]):
                            if port2pol[l] == polMap[k]:
                                selectedPorts.append(meas_array_gain[l,freqCol])
            axs[j,k].hist(np.array(selectedPorts), bins=6)
            axs[j,k].set_xlim([0,30]); axs[j,k].set_ylim([0,10])
            axs[j,k].set_title(chanMap[j]+polMap[k])
            axs[j,k].set_xlabel('S21 (arb) [dB]'); axs[j,k].set_ylabel('count')
            
            ymax1 = 10.0
            mean = np.mean(np.array(selectedPorts))
            variance = np.var(np.array(selectedPorts))
            sigma = np.sqrt(variance)
            x = np.linspace(-50, 50, 10001)
            axs[j,k].plot(x, ymax1 * norm.pdf(x, mean, sigma) / (max(norm.pdf(x, mean, sigma))), 'r', linewidth=3)
            
            axs[j,k].set_xlim([-50,50]); axs[j,k].set_ylim([0,ymax1])
            axs[j,k].set_title(chanMap[j]+polMap[k])
            axs[j,k].set_xlabel('S21 (arb) [dB]'); axs[j,k].set_ylabel('count')
            
            axs[j,k].grid('on')
    
    fig.suptitle(str(freq) + ' GHz', fontsize=18)
    plt.tight_layout()






