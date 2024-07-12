# -*- coding: utf-8 -*-
"""
Created on Mon Dec 18 16:40:42 2023

@author: jmitchell
"""

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
# import seaborn as sns
from matplotlib.markers import MarkerStyle
plt.close('all')

# definitions
def find_measFiles(path, fileString, beam, freq_set, board):
    global measFiles, files
    files = []
    for root, directories, file in os.walk(path):
        for file in file:
            if (file.endswith(".csv")) == True:
                files.append(os.path.join(root, file))
    measFiles = []
    for i in range(len(files)):
        if fileString in files[i] and 'eam' + str(beam) in files[i] and f'{freq_set}_GHz_4' in files[i] and f'teration_2' not in files[i] and board in files[i]:
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

## code

# files
file_path = r'C:\scratch\20240710'
map_tlm_df = pd.read_csv(r'C:\GitHub\jm_post_processing\20240227_tlm_map_plotter\20221019_TLMCalInputs\Mrk1_S2000_TLM_TX_ArrayGeometry_V20062022_CalInfo.csv', header=1)
map_rfic = pd.read_csv(r'C:\GitHub\jm_post_processing\20240227_tlm_map_plotter\20221019_TLMCalInputs\MK1_TX_TLM_RFIC_Patch_Feed_Mapping.csv')

# params
freq_set = '29.50'
normalise = True
board = '00143'
for board in ['00143', '00172', '00169']:
    # boards
    find_measFiles(file_path, 'OP_2', 1, freq_set, board)
    
        
    rfics = list(set(map_rfic['RFIC Number']))
    
    meas_file_overview_dict = {}
    for meas_file in measFiles:
        meas_file_overview_dict[meas_file] = {}
        fig, axs = plt.subplots(nrows=3, ncols=2, figsize=(20,15))
        for beam in [1,2]:
            find_measFiles(file_path, 'OP_2', beam, freq_set, board)
            for lens in [0,1,2]:
                load__measFiles(meas_file)
                col = np.argmin((meas_frequencies-float(freq_set))**2)
                ports = np.linspace(1,len(meas_array_gain), num=len(meas_array_gain))
                rfic_offset_log = []
                rfic_std_log = []
                for rfic in rfics:
                    df_rfic = map_rfic[map_rfic['RFIC Number']==rfic]
                    ports_rfic = np.array(df_rfic['Patch Number'])
                    ports_rfic = list(np.concatenate((ports_rfic, ports_rfic+1), axis=0))
                    ports_rfic.sort()
                    col_map = ['r', 'g', 'b', 'k', 'c', 'm', 'y', 'pink']; col_count = 0
                    port_gain_log = []
                    
                    for port_rfic in ports_rfic:
                        port_number = (port_rfic-1) + (lens*(len(meas_array_gain)/3))
                        port_gain_log.append(meas_array_gain[int(port_number), col])
                    rfic_offset_log.append(np.median(port_gain_log))
                    rfic_std_log.append(np.std(port_gain_log))
                    for port_rfic in ports_rfic:
                        if normalise == True:
                            offset = np.median(port_gain_log)
                        else:
                            offset = 0.0
                        port_number = (port_rfic-1) + (lens*(len(meas_array_gain)/3))
                        axs[lens, beam-1].plot(rfic, meas_array_gain[int(port_number), col]-offset, 'o', color = col_map[col_count])
                        col_count = col_count + 1
                    if normalise == True:
                        offset = np.median(port_gain_log)
                    else:
                        offset = 0.0
                                 
                    axs[lens, beam-1].plot(rfic, np.median(port_gain_log)-offset, 'k^', markersize=15)
                    axs[lens, beam-1].plot([rfic, rfic], [np.median(port_gain_log)-np.std(port_gain_log)-offset, np.median(port_gain_log)+np.std(port_gain_log)-offset] , 'k-', markersize=15)
                    # axs[lens, beam-1].plot([rfic, rfic], [np.min(port_gain_log)-offset, np.max(port_gain_log)-offset] , 'k-', markersize=15)
                    axs[lens, beam-1].set_xlim([0,20])
                    axs[lens, beam-1].set_ylim([-10, 10])
                    axs[lens, beam-1].set_ylabel('dB')
                    axs[lens, beam-1].set_xlabel('rfic')
                    axs[lens, beam-1].set_title(f'Lens {lens+1}, beam {beam}: std_av = {round(np.median(rfic_std_log),1)} dB')
                    axs[lens, beam-1].set_xticks(np.linspace(1,len(rfic_offset_log), num=len(rfic_offset_log)))
                    axs[lens, beam-1].grid(linestyle=':')
                    
                    
                    
                    board = meas_params['barcodes'].split('_')[0]
                    for idx in range(len(meas_params['barcodes'].split('_'))):
                        if 'ias' in meas_params['barcodes'].split('_')[idx]:
                            start_val = idx
                    settings = meas_params['barcodes'].split('_')[start_val:]
                    
                    meas_file_overview_dict[meas_file][f'beam{beam}lens{lens}'] = [round(np.median(rfic_std_log),1), round(np.median(rfic_offset_log),1)]
                    meas_file_overview_dict[meas_file]['settings'] = settings
                    meas_file_overview_dict[meas_file]['board'] = board
                    meas_file_overview_dict[meas_file]['category'] = meas_file.split('\\')[-4][2:]
        
        fig.suptitle(f'board-{board}, settings: {settings}')
        plt.tight_layout()
        plt.savefig(f'board-{board}_settings{str(settings)}.png', dpi=400)
        
        
    fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(20,15))
    for meas_file in list(meas_file_overview_dict.keys()):
        gain = []
        std = []
        x_ticks = []
        for beam in [1,2]:
            for lens in [0,1,2]:
                gain.append(meas_file_overview_dict[meas_file][f'beam{beam}lens{lens}'][1])
                std.append(meas_file_overview_dict[meas_file][f'beam{beam}lens{lens}'][0])
                x_ticks.append(f'beam{beam}lens{lens+1}')
        label = meas_file_overview_dict[meas_file]['board'] + ': ' +  meas_file_overview_dict[meas_file]['category']#+ str(meas_file_overview_dict[meas_file]['settings'])
        axs[0].plot(x_ticks, gain, 'o-', label=label)
        axs[0].grid('on')
        axs[0].legend(loc='upper left')
        axs[0].set_ylim([10,30])
        axs[0].set_ylabel('average rfic gain [dB]')
        axs[1].plot(x_ticks, std, 'o-', label=label)
        axs[1].grid('on')
        axs[1].legend(loc='upper left')
        axs[1].set_ylim([1,4])
        axs[1].set_ylabel('average rfic channel spread [dB]')
    fig.suptitle(f'board-{board}')
    plt.savefig(f'overview_board-{board}.png', dpi=400)
            
            
            
            