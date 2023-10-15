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
filePath = r'C:\Scratch\temp'

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
    for i in range(int(len(ports) / 3)):
        for j in range(len(S2000_TX_RFIC_PORT_MAP)):
            forCheck = S2000_TX_RFIC_PORT_MAP[str(j + 1)]
            if int(i + 1) in forCheck:
                port2IC.append(j + 1)
                port2chan.append(S2000_TX_RFIC_CHANNEL_MAP[str(i + 1)][0])
                port2pol.append(S2000_TX_RFIC_CHANNEL_MAP[str(i + 1)][1])

find_measFiles(filePath, 'OP', 1)
f_set = 19.2
for measFile in measFiles:
    load__measFiles(measFile)
    col = np.argmin((meas_frequencies-(float(f_set)))**2)
    plt.plot(meas_array_gain[:,col],'o-')
plt.ylim([-20,60])