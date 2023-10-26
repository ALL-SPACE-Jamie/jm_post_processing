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
from scipy.stats import skewnorm
from scipy import stats
from scipy.stats import weibull_min

plt.close('all')

# file path
dirScript = os.getcwd()

# parmas
filePath = r'C:\Users\jmitchell\OneDrive - ALL.SPACE\G-Type\Tx_TLM_G-Type\TLM_Evaluation_Measurements\All_TLMs\G-Type_ES2i_E-fused_Bias\2023-10-04_20-45-45_MCR3_Rig1_eval_QR420-0230-00009\frequency_29.5_GHz'
# filePath = r'C:\Users\JamieMitchell\OneDrive - ALL.SPACE\G-Type\Tx_TLM_G-Type\TLM_Evaluation_Measurements\All_TLMs\G-Type_ES2i_ES2c_Opt_Bias'
# filePath = r'C:\Users\JamieMitchell\OneDrive - ALL.SPACE\G-Type\Tx_TLM_G-Type\TLM_Evaluation_Measurements\All_TLMs\G-Type_ES2i_ES2i_Opt_Bias'
# filePath = r'C:\Users\JamieMitchell\OneDrive - ALL.SPACE\F-Type\Tx_TLM_F-Type\TLM_Evaluation_Measurements'
# filePath = r'C:\Users\JamieMitchell\OneDrive - ALL.SPACE\G-Type\Rx_TLM_G-Type\TLM_Evaluation_Measurements\All_TLMs'
# filePath = r'C:\Users\JamieMitchell\OneDrive - ALL.SPACE\F-Type\Rx_TLM_F-Type\TLM_Evaluation_Measurements'
txrx = 'tx'
saveFolder = filePath + '\\Figures\\'
freqLog = [29.5]
f_meas = 29.5

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
        if fileString in files[i] and 'eam' + str(beam) in files[i] and 'rchive' not in files[i] and 'ALL_' not in files[i]:# and '0011' in files[i]:# and '0022' not in files[i] and '0021' not in files[i]:
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
    for i in range(int(len(ports)/3)):
        for j in range(len(S2000_TX_RFIC_PORT_MAP)):
            forCheck = S2000_TX_RFIC_PORT_MAP[str(j + 1)]
            if int(i + 1) in forCheck:
                port2IC.append(j + 1)
                port2chan.append(S2000_TX_RFIC_CHANNEL_MAP[str(i + 1)][0])
                port2pol.append(S2000_TX_RFIC_CHANNEL_MAP[str(i + 1)][1])
    # port2IC = port2IC + port2IC + port2IC
    # port2chan = port2chan + port2chan + port2chan
    # port2pol = port2pol + port2pol + port2pol

lensLog = [1,2,3]
beamLog = [1,2]
for lens in lensLog:
    print('lens ' + str(lens))
    for beam in beamLog:
        meanLog = []
        varianceLog = []
        ymax1Log = []
        weibLog = []
        for freq in freqLog:
        
            
            dict__maps(txrx)
            find_measFiles(filePath, 'OP_2', beam)
            fig, axs = plt.subplots(4, 2, figsize=(25, 15))
            
            
            chanMap = ['0','1','2','3']
            polMap = ['V','H']
            
            for j in range(4):
                for k in range(2):
                    print(chanMap[j] + polMap[k])
                    print('beam ' + str(beam))
                    selectedPorts = []
                    badBoards = 0
                    for measFile in measFiles:
                        load__measFiles(measFile)
                        meas_array_gain = meas_array_gain[(lens-1)*int(len(meas_array_gain)/3):(lens)*int(len(meas_array_gain)/3),:] * 1.0
                        portSort()
                        if meas_params['f_c'] == str(freq):
                            freqCol = np.argmin((meas_frequencies-f_meas)**2) 
                            for l in range(len(port2chan)):
                                if port2chan[l] == int(chanMap[j]):
                                    if port2pol[l] == polMap[k]:
                                        if len(np.array(meas_array_gain[l,freqCol])[np.array(meas_array_gain[l,freqCol]) < -30.0]) < 1:
                                            selectedPorts.append(meas_array_gain[l,freqCol])
                                            print('RFIC ' + str(port2IC[l]) + ', port ' + str(l+1) + ', ' + str(meas_array_gain[l,freqCol]))
                                            print()
                                        else:
                                            badBoards = badBoards+1.0
                    w = 1
                    # axs[j,k].hist(np.array(selectedPorts), bins=np.arange(min(selectedPorts), max(selectedPorts) + w, w))
                    count = np.histogram(np.array(selectedPorts), bins=np.arange(min(selectedPorts), max(selectedPorts) + w, w))
                    axs[j,k].set_xlim([0,30]); axs[j,k].set_ylim([0,10])
                    axs[j,k].set_title(chanMap[j]+polMap[k])
                    # print(chanMap[j]+polMap[k])
                    axs[j,k].set_xlabel('S21 (arb) [dB]'); axs[j,k].set_ylabel('count')
                    
                    ymax1 = np.max(count[0])
                    ymax1Log.append(ymax1)
                    mean = np.mean(np.array(selectedPorts)); meanLog.append(mean)
                    
                    variance = np.var(np.array(selectedPorts)); varianceLog.append(variance)
                    sigma = np.sqrt(variance)
                    x = np.linspace(-50, 50, 10001)

                    # axs[j,k].plot(x, ymax1 * norm.pdf(x, mean, sigma) / (max(norm.pdf(x, mean, sigma))), 'r', linewidth=3)
                    
                    # gamma = stats.gamma
                    a, loc, scale = 3, 0, 2
                    size = 20000
                    # y = gamma.rvs(a, loc, scale, size=size)
                    # y = np.array(selectedPorts)
                    
                    # x = np.linspace(0, y.max(), 100)
                    # fit
                    # param = gamma.fit(y, floc=1)
                    # pdf_fitted = gamma.pdf(x, *param)
                    # axs[j,k].plot(x, pdf_fitted, color='r')
                    
                    # plot the histogram
                    weights = np.ones_like(selectedPorts)/float(len(selectedPorts))
                    axs[j,k].hist(selectedPorts, weights=weights, bins=np.arange(min(selectedPorts), max(selectedPorts) + w, w))

                    
                    axs[j,k].set_xlim([-50,50]); axs[j,k].set_ylim([0,0.5])
                    axs[j,k].set_title(chanMap[j]+polMap[k])
                    axs[j,k].set_xlabel('S21 (arb) [dB]'); axs[j,k].set_ylabel('count')
                    
                    shape, loc, scale = weibull_min.fit(selectedPorts, loc=2)
                    
                    axs[j,k].plot(x, weibull_min.pdf(x, shape, loc, scale), 'r-', label='Fitted Weibull PDF')
                    # axs[j,k].plot(x, norm.pdf(x, mean, sigma), 'r', linewidth=3)
                    axs[j,k].grid('on')
                    
                    weibLog.append([shape, loc, scale])
                    
                    # print(meas_params['barcodes'])
                    # print(min(count[1]))
                    
                    
                    # print(selectedPorts)
                    

                    

                    
                    
            if not os.path.exists(saveFolder):
                os.makedirs(saveFolder)
            fig.suptitle('f$_{set}$ = ' + str(freq) + ' GHz (' 'f$_{meas}$ = ' + str(f_meas) + ' GHz)' + ' [N = ' + str(len(measFiles)-int(badBoards)) + ']', fontsize=18)
            plt.tight_layout()
            plt.savefig(saveFolder +  'Channel Spread Lens ' + str(lens) + ' beam ' + str(beam) + ' fset' + str(freq) + 'GHz ' + 'fmeas' + str(f_meas) + 'GHz' + '.png')
        
        plt.figure(figsize=(10, 7))
        portLog = ['0V','0H','1V','1H','2V','2H','3V','3H']
        colLog = ['r','r','g','g','b','b','k','k']
        lineLog = ['-','--','-','--','-','--','-','--']
        for i in range(8):
            mean = meanLog[i]
            variance = varianceLog[i]
            sigma = np.sqrt(variance)
            # plt.plot(x, norm.pdf(x, mean, sigma) , colLog[i], linestyle=lineLog[i],linewidth=3,label=portLog[i],alpha=0.5)
            plt.plot(x, weibull_min.pdf(x, weibLog[i][0], weibLog[i][1], weibLog[i][2]), colLog[i], linestyle=lineLog[i],linewidth=3,label=portLog[i],alpha=0.5)
            plt.xlim([-10,50]); plt.ylim([0,0.5])
            plt.legend(loc='upper right')
            plt.xlabel('S21 (arb) [dB]'); plt.ylabel('count')
            plt.title('Lens ' + str(lens) + ', beam ' + str(beam) + '\n f$_{set}$ = ' + str(freq) + ' GHz (' 'f$_{meas}$ = ' + str(f_meas) + ' GHz)' + ' [N = ' + str(len(measFiles)-int(badBoards)) + ']', fontsize=18)
            plt.savefig(saveFolder +  'Channel Spread Overview Lens ' + str(lens) + ' beam ' + str(beam) + ' fset' + str(freq) + 'GHz ' + 'fmeas' + str(f_meas) + 'GHz' + '.png')
            plt.grid('on')
            
            
        
        
        
        
        
        
