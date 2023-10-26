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
filePath = r'C:\Users\JamieMitchell\OneDrive - ALL.SPACE\G-Type\Rx_TLM_G-Type\TLM_Evaluation_Measurements\All_TLMs'
filePath = r'C:\Users\jmitchell\OneDrive - ALL.SPACE\G-Type\Rx_TLM_G-Type\TLM_Evaluation_Measurements\All_TLMs\2023-10-05_13-59-02_MCR4_Rig1_eval_QR420-0231-00022\frequency_19.2_GHz'

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
    global meas_info, meas_array, meas_frequencies, meas_params, meas_array_gain, meas_array_phase, meas_powers, f_s, port, rfic, f_c, index_start
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
    for i in range(int(len(ports))):
        for j in range(len(S2000_TX_RFIC_PORT_MAP)):
            forCheck = S2000_TX_RFIC_PORT_MAP[str(j + 1)]
            if int(i + 1) in forCheck:
                port2IC.append(j + 1)
                port2chan.append(S2000_TX_RFIC_CHANNEL_MAP[str(i + 1)][0])
                port2pol.append(S2000_TX_RFIC_CHANNEL_MAP[str(i + 1)][1])
    port2IC = port2IC + port2IC + port2IC
                
combMap = {

		"L1BEAM2IN_A1": [5, 6, 7, 9, 10, 12],
		"L1BEAM2IN_B1": [1, 2, 3, 4, 8, 11],
		"L1BEAM1IN_A1": [5, 6, 7, 9, 10, 12],
		"L1BEAM1IN_B1": [1, 2, 3, 4, 8, 11],


		"L2BEAM1IN_A2": [5, 6, 7, 9, 10, 12],
		"L2BEAM1IN_B2": [1, 2, 3, 4, 8, 11],
		"L2BEAM2IN_A2": [5, 6, 7, 9, 10, 12],
		"L2BEAM2IN_B2": [1, 2, 3, 4, 8, 11],


		"L3BEAM1IN_A3": [5, 6, 7, 9, 10, 12],
		"L3BEAM1IN_B3": [1, 2, 3, 4, 8, 11],
		"L3BEAM2IN_A3": [5, 6, 7, 9, 10, 12],
		"L3BEAM2IN_B3": [1, 2, 3, 4, 8, 11]

}

find_measFiles(filePath, 'OP', 1)
f_set = 19.2
for measFile in measFiles:
    load__measFiles(measFile)
    dict__maps('rx')
    portSort()
    col = np.argmin((meas_frequencies-(float(f_set)))**2)
    # plt.plot(meas_array_gain[:,col],'o-')
    for i in range(len(meas_array_gain[:,col])):
        IC = port2IC[i]
        if IC in combMap['L1BEAM2IN_A1']:
            plt.plot(i+1,meas_array_gain[i,col], 'ro')
        else:
            plt.plot(i+1,meas_array_gain[i,col], 'gs')
    
plt.ylim([20,50]); plt.xlim([1,len(meas_array_gain[:,col])])
plt.xticks(np.linspace(1,len(meas_array_gain[:,col]), num=288),rotation=90)
plt.grid()