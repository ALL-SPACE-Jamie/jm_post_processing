import pandas as pd
import numpy as np
import matplotlib.pyplot as plt;
plt.rcParams['font.size'] = 12
import matplotlib.backends.backend_pdf
from matplotlib import cm, colors
from scipy.stats import norm
import os
import glob
import copy
import csv
import json
import time
from pylab import *
import seaborn as sns
colMap = ['r','g','b']*100
plt.close('all')

# file path
dirScript = os.getcwd()

# parameters
file_path = r'C:\Users\jmitchell\Desktop\Cal Rig\2023-12-02_col-05-33_F2 terminal_both_27.95GHz_-1C\2023-12-02_col-05-33_F2 terminal_both_27.95GHz_-1C\iteration_2'
file_path = r'C:\Users\jmitchell\Desktop\Cal Rig\rfa_manual_patch_f2\1_20_121\2023-11-24_15-50-06_F2 terminal_both_19.7GHz_-1C\iteration_1'

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

def load__measFiles(file_path):
    global meas_info, meas_params, meas_array, meas_frequencies, meas_array_gain, meas_array_phase, paramName, i
    if os.path.getsize(file_path) > 2000:
        meas_params = {}
        meas_info = []
    
        # meas_info, array and measurement frequencies
        with open(file_path, 'r') as file:
            filecontent = csv.reader(file, delimiter=',')
            for row in filecontent:
                meas_info.append(row)
            index_start = [index for index in range(len(meas_info)) if 'barcodes' in meas_info[index]][0] + 2
            meas_info = meas_info[0:index_start]
            meas_array = np.genfromtxt(file_path, delimiter=',', skip_header=index_start)
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



def my_def(file_path):
    find_measFiles(file_path, 'RFA', 2)
    load__measFiles(measFiles[0])

    col = np.argmin((meas_frequencies-float(meas_params['f_c']))**2)
    no_ports = int(len(meas_array_gain)/18)
    
    plt.figure()
    for i in range(18):
        if i%3 == 0:
            tlm = 0
            ref_ports = list(range(int(float(tlm)*no_ports), int(float(tlm+1)*no_ports)))
            ref_tlm = meas_array_phase[ref_ports,col]
            plt.axvline(x=ref_ports[0])
        
        ports = list(range(int(float(i)*no_ports), int(float(i+1)*no_ports)))
        # plt.plot(ref_ports, meas_array_phase[ports,col], '-')
        
        values = (ref_tlm-meas_array_phase[ports,col])
        for jj in range(len(values)):
            if values[jj] < -100.0:
                values[jj] = values[jj] + 360.0
                
        plt.plot(ports, values, colMap[i]+'s')
        plt.plot([min(ports), max(ports)], [np.median(ref_tlm-meas_array_phase[ports, col]), np.median(ref_tlm-meas_array_phase[ports, col])], 'k')
        plt.plot([min(ports), max(ports)], [np.median(ref_tlm-meas_array_phase[ports, col])+20.0, np.median(ref_tlm-meas_array_phase[ports, col])+20.0], 'k')
        plt.plot([min(ports), max(ports)], [np.median(ref_tlm-meas_array_phase[ports, col])-20.0, np.median(ref_tlm-meas_array_phase[ports, col])-20.0], 'k')

        plt.text(np.average(ports), np.median(ref_tlm-meas_array_phase[ports, col])+3, str(round(np.median(ref_tlm-meas_array_phase[ports, col]),1))+'deg')
        plt.ylim([-360,360])
    plt.title(measFiles[0].split('\\')[-1])
    plt.grid('on')
    
# my_def(r'C:\Users\jmitchell\Desktop\Cal Rig\20231213\f2_rx_mpm\2023-11-21_17-40-22_F2 terminal_both_19.7GHz_-1C\iteration_2')
my_def(r'C:\Users\jmitchell\Desktop\Cal Rig\20231213\f2_rx_rfa_mpm\2023-11-24_15-50-06_F2 terminal_both_19.7GHz_-1C\iteration_2')










def find_measFiles_CATR(path, fileString, fileString2, beam):
    global measFiles, files
    files = []
    for root, directories, file in os.walk(path):
        for file in file:
            if (file.endswith(".csv")) == True:
                files.append(os.path.join(root, file))
    measFiles = []
    for i in range(len(files)):
        if fileString in files[i] and fileString2 in files[i] and 'eam' + str(beam) in files[i] and 'rchive' not in files[i] and 'Len3' in files[i]:
            measFiles.append(files[i])

find_measFiles_CATR(r'C:\Users\jmitchell\Desktop\Cal Rig\CATR data\AllFiles', 'rxCombPnt', 'LHCP', 1)

def load__measFiles_CATR(file_path):
    global meas_info, meas_params, meas_array, meas_frequencies, meas_array_gain, meas_array_phase, paramName, i
    if os.path.getsize(file_path) > 2000:
        meas_params = {}
        meas_info = []
    
        # meas_info, array and measurement frequencies
        with open(file_path, 'r') as file:
            filecontent = csv.reader(file, delimiter=',')
            for row in filecontent:
                meas_info.append(row)
    
            index_start = [index for index in range(len(meas_info)) if 'RawAtten' in meas_info[index][0]][0] + 1
            meas_info = meas_info[0:index_start]
            meas_array = np.genfromtxt(file_path, delimiter=',', skip_header=index_start)
            meas_array_gain = meas_array[:, ::2]
            meas_array_phase = meas_array[:, 1:][:, ::2]
        
    # meas_params
    for i in range(len(meas_info) - 1):
        if len(meas_info[i][0]) > 1:
            paramName = meas_info[i][0]
            if paramName[0:2] == '# ':
                paramName = paramName[2:]
            if len(meas_info[i][1]) != 0:
                meas_params[paramName] = meas_info[i][1]
                if len(meas_params[paramName]) > 0:
                    if meas_params[paramName][0] == ' ':
                        meas_params[paramName] = meas_params[paramName][1:]

meas_files_selected = []
for measFile in measFiles:
    load__measFiles_CATR(measFile)
    if meas_params['Frequency'] == '19700':
        meas_files_selected.append(measFile)
        if np.average(meas_array_phase) == 0.0:
            ref_tlm = meas_params['TriLensQR']
            
# plt.figure()
count = 0
for measFile in meas_files_selected:
    load__measFiles_CATR(measFile)
    print(meas_params['TriLensQR'])
    print(np.average(meas_array_phase))
    
    plt.plot(count*288+144, np.average(meas_array_phase), 'kX', markersize=20)
    plt.errorbar(count*288+144, np.average(meas_array_phase), yerr=np.std(meas_array_phase), fmt='b-o')
    
    count = count + 1

    
stop
theta_list = np.linspace(float(meas_params['FirstTheta']), float(meas_params['NumTheta'])*float(meas_params['DeltaTheta']), num = int(meas_params['NumTheta']))
phi_list = np.linspace(float(meas_params['FirstPhi']), float(meas_params['NumPhi'])*float(meas_params['DeltaPhi']), num = int(meas_params['NumPhi']))

fig, ax = plt.subplots()
cs = ax.contourf(theta_list, phi_list, meas_array_phase, levels=np.arange(0, 360, 0.1), cmap='jet')
print(meas_params['TriLensQR'])