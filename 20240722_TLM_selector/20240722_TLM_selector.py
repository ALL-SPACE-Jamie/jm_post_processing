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
def find_measFiles(path, fileString, beam, freq_set):
    global measFiles, files
    files = []
    for root, directories, file in os.walk(path):
        for file in file:
            if (file.endswith(".csv")) == True:
                files.append(os.path.join(root, file))
    measFiles = []
    for i in range(len(files)):
        if fileString in files[i] and 'eam' + str(beam) in files[i] and f'{freq_set}_GHz_4' in files[i] and f'teration_2' not in files[i]:
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
file_path = r'C:\Users\jmitchell\Downloads\P3Tx____'

# params
freq_set = '29.50'
beam = 1
freq_list = ['29.50', '28.00', '28.50', '29.00', '27.50', '30.00', '30.50', '31.00']
# freq_list = ['27.50']
# freq_list = ['17.70', '18.20', '18.70', '19.20', '19.70', '20.20', '20.70', '21.20']

# run

df = pd.DataFrame(columns=['board', 'gain_median', 'gain_spread', 'min_port', 'dropped_port', 'frequency', 'beam', 'gain_median_rank', 'gain_spread_rank', 'full_rank'])




for beam in [1, 2]:
    for freq_set in freq_list:        
        find_measFiles(file_path, 'RFA', beam, freq_set)
        for meas_file in measFiles:
            load__measFiles(meas_file)
            col = np.argmin((meas_frequencies-float(freq_set))**2)
            gain = meas_array_gain[:, col]
            gain_median = np.median(gain)
            gain_spread = np.std(gain)
            board = meas_params['barcodes']
            dropped_flag = False
            min_port = min(gain)
            if min_port < (gain_median - gain_spread*5):
                dropped_flag = True
            new_entry = {'board': board, 'gain_median': gain_median, 'gain_spread': gain_spread, 'min_port': min_port, 'dropped_port': dropped_flag,
                          'frequency': float(freq_set), 'beam': beam}
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)


df_ranked = pd.DataFrame(columns=['board', 'gain_median', 'gain_spread', 'min_port', 'dropped_port', 'frequency', 'beam', 'gain_median_rank', 'gain_spread_rank', 'full_rank'])
for beam in [1, 2]:
    for freq_set in freq_list:
        # load 143
        find_measFiles(r'C:\Users\jmitchell\Downloads\MCR1_Rig1_TLM_00143', 'RFA', beam, freq_set)
        load__measFiles(measFiles[0])
        col = np.argmin((meas_frequencies-float(freq_set))**2)
        gain = meas_array_gain[:, col]
        gain_median_143 = np.median(gain)
        
        df_freq = df[df['frequency'] == float(freq_set)]
        df_freq = df_freq[df_freq['beam'] == beam]
        gain_medians = df_freq['gain_median']
        gain_spreads = df_freq['gain_spread']
        
        ###################################
        gain_medians_relative = abs(df_freq['gain_median'] - np.median(df_freq['gain_median']))
        # gain_medians_relative = abs(df_freq['gain_median'] - gain_median_143)
        
        # rank gain medians
        numbers_array = np.array(gain_medians_relative)
        # rank = numbers_array.argsort().argsort() + 1
        rank = (-numbers_array).argsort().argsort() + 1
        for idx in range(len(numbers_array)):
            if list(gain_medians)[idx] < 0.1:
                rank[idx] = -10000000.0
                print('dead')
        df_freq['gain_median_rank'] = rank
        
        # rank gain spreads
        numbers_array = np.array(gain_spreads)
        rank = (-numbers_array).argsort().argsort() + 1
        df_freq['gain_spread_rank'] = rank
        
        # full rank
        df_freq['full_rank'] = df_freq['gain_median_rank'] + df_freq['gain_spread_rank']
        
        df_ranked = pd.concat([df_ranked, pd.DataFrame(df_freq)], ignore_index=True)
        
boards = list(set(df_ranked['board']))
scores = []
for board in boards:
    df_board = df_ranked[df_ranked['board'] == board]
    scores.append(np.sum(df_board['full_rank']))
    
df_scores = pd.DataFrame(columns=['board', 'scores'])
df_scores['board'] = boards
df_scores['scores'] = scores
df_scores = df_scores.sort_values(by='scores', ascending=False)

boards_ranked = list(df_scores['board'])
plt.close('all')
for freq_set in freq_list:
    fig, axs = plt.subplots(nrows=2, ncols=1, figsize=(15, 10))
    for board in boards_ranked:
        df_board = df_ranked[df_ranked['board'] == board]
        df_board = df_board[df_board['frequency'] == float(freq_set)]
        axs[0].plot(board, list(df_board['gain_median'])[0], 'ko')
        axs[0].plot(board, list(df_board['gain_median'])[1], 'r^')
        axs[1].plot(board, list(df_board['gain_spread'])[0], 'ko')
        axs[1].plot(board, list(df_board['gain_spread'])[1], 'r^')
    axs[0].plot(board, list(df_board['gain_median'])[0], 'ko', label='beam1')
    axs[0].plot(board, list(df_board['gain_median'])[1], 'r^', label='beam2')
    axs[1].plot(board, list(df_board['gain_spread'])[0], 'ko', label='beam1')
    axs[1].plot(board, list(df_board['gain_spread'])[1], 'r^', label='beam2')
    axs[0].set_ylabel('median gain [dB]')
    axs[1].set_ylabel('spread [dB]')
    axs[0].grid('on')
    axs[1].grid('on')
    axs[0].legend(loc='lower right')
    axs[1].legend(loc='lower right')
    fig.suptitle(f'{freq_set} GHz')
        
    for ax in axs:
        for label in ax.get_xticklabels():
            label.set_rotation(90)
    
    freq_set_forsave = freq_set.replace('.','g')
    plt.savefig(f'{freq_set_forsave}GHz.png', dpi=400)
            
plt.figure()
plt.plot(df_scores['board'], df_scores['scores'],'o-')
plt.ylim([0,1300])
plt.xticks(rotation=90, fontsize=7)
plt.xlabel('board')
plt.ylabel('score')
plt.grid()





















