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
import seaborn as sns
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
                    
def gain_to_rfic_metrics(gain_col):
    gain_col = gain_col - np.median(gain_col)
    rfics = list(set(map_rfic['RFIC Number']))
    rfic_offset_log = []
    rfic_std_log = []
    rfic_minmax_log = []
    for lens in [0,1,2]:
        ports = np.linspace(1,len(gain), num=len(gain))
        for rfic in rfics:
            df_rfic = map_rfic[map_rfic['RFIC Number']==rfic]
            ports_rfic = np.array(df_rfic['Patch Number'])
            ports_rfic = list(np.concatenate((ports_rfic, ports_rfic+1), axis=0))
            ports_rfic.sort()
            port_gain_log = []
            for port_rfic in ports_rfic:
                port_number = (port_rfic-1) + (lens*(len(gain_col)/3))
                port_gain_log.append(gain_col[int(port_number)])
            rfic_offset_log.append(np.median(port_gain_log))
            rfic_std_log.append(np.std(port_gain_log))
            rfic_minmax_log.append(np.max(port_gain_log)-np.min(port_gain_log))
            
    return np.array(rfic_offset_log), np.array(rfic_std_log), np.array(rfic_minmax_log)






## code

# files
file_path = r'C:\Users\jmitchell\Downloads\P3Tx_all\P3Tx_all\rest'
map_tlm_df = pd.read_csv(r'C:\GitHub\jm_post_processing\20240227_tlm_map_plotter\20221019_TLMCalInputs\Mrk1_S2000_TLM_TX_ArrayGeometry_V20062022_CalInfo.csv', header=1)
map_rfic = pd.read_csv(r'C:\GitHub\jm_post_processing\20240227_tlm_map_plotter\20221019_TLMCalInputs\MK1_TX_TLM_RFIC_Patch_Feed_Mapping.csv')
df_tlmic = pd.read_excel(r'C:\Users\jmitchell\Downloads\es2i_wafer_map_master_GF.xlsx', sheet_name='es2i_wafer_map_master_GF', header=1)

# params
freq_set = '29.50'
beam = 1
delta_board = False
freq_list = ['29.50', '28.00', '28.50', '29.00', '27.50', '30.00', '30.50', '31.00']
# freq_list = ['29.50']
# freq_list = ['17.70', '18.20', '18.70', '19.20', '19.70', '20.20', '20.70', '21.20']

# run

df = pd.DataFrame()

for beam in [1,2]:
    for freq_set in freq_list:        
        find_measFiles(file_path, 'OP_2', beam, freq_set)
        for meas_file in measFiles:
            load__measFiles(meas_file)
            col = np.argmin((meas_frequencies-float(freq_set))**2)
            gain = meas_array_gain[:, col]
            gain_median = np.median(gain)
            gain_spread = np.std(gain)
            gain_minmax = np.max(gain)-np.min(gain)
            lens_medians = []
            for lens in [1,2,3]:
                lens_medians.append(float(np.median(gain[int((lens-1)*len(gain)/3):int((lens)*len(gain)/3)])))
            lens_delta_max = max(lens_medians)-min(lens_medians)
            rfic_offset_log, rfic_std_log, rfic_minmax_log = gain_to_rfic_metrics(gain)
            rfic_offset_max = rfic_offset_log[np.argmax(abs(rfic_offset_log))]
            rfic_spread_max = rfic_std_log[np.argmax(abs(rfic_std_log))]
            rfic_minmax_max = rfic_minmax_log[np.argmax(abs(rfic_minmax_log))]
            
            board = meas_params['barcodes']
            uid = meas_params['ER Id']
            wafer_id_chunk = uid[0:5]
            wafer_id_binary = bin(int(wafer_id_chunk, 16))
            wafer_id_num = int(wafer_id_binary[2:],2)
            df_tlmic_specific = df_tlmic[df_tlmic['uid[31:12]']==wafer_id_num]
            wafer_id = df_tlmic_specific['wafer_id']
            lot = list(df_tlmic_specific['ES2i Lot ID'])[0]#[-10:]
            dropped_flag = False
            min_port = min(gain)
            if min_port < (gain_median - gain_spread*5):
                dropped_flag = True
            new_entry = {'board': board, 'gain_median [dB]': gain_median, 'gain_spread [dB]': gain_spread,
                         'min_port [dB]': min_port, 'dropped_port': dropped_flag,
                         'frequency [GHz]': float(freq_set), 'beam': beam,
                         'gain_minmax [dB]': gain_minmax, 'lens1_median [dB]': lens_medians[0],
                         'lens2_median [dB]': lens_medians[1], 'lens3_median [dB]': lens_medians[2], 'lens_delta_max': lens_delta_max,
                         'rfic_offset_max [dB]': rfic_offset_max, 'rfic_spread_max [dB]': rfic_spread_max, 'rfic_minmax_max [dB]': rfic_minmax_max,
                         'lens_delta_max [dB]': lens_delta_max, 'uid': uid, 'wafer_id_num': wafer_id_num,
                         'lot': lot
                         }
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)



limits = {}
limits['27.50'] = {}
limits['27.50']['gain_median [dB]'] = 6.0



for freq_set in freq_list:
    fig, axs = plt.subplots(nrows=4, ncols=4, figsize=(40,25))
    df_freq = df[df['frequency [GHz]'] == float(freq_set)]
    for beam in [1,2]:
        df_plot = df_freq[df_freq['beam']==beam]
        
        sns.histplot(data=df_plot, x='gain_median [dB]', kde=True, ax=axs[0+(2*(beam-1)),0])
        axs[0+(2*(beam-1)),0].set_title(f'Median TLM gain [dB] (beam{beam})')
        axs[0+(2*(beam-1)),0].set_xlim([-6,12])
        
        sns.histplot(data=df_plot, x='gain_spread [dB]', kde=True, ax=axs[0+(2*(beam-1)),1])
        axs[0+(2*(beam-1)),1].set_title(f'TLM spread [dB] (beam{beam})')
        axs[0+(2*(beam-1)),1].set_xlim([2,4])
        
        sns.histplot(data=df_plot, x='lens1_median [dB]', kde=True, ax=axs[0+(2*(beam-1)),2], label='lens1')
        sns.histplot(data=df_plot, x='lens2_median [dB]', kde=True, ax=axs[0+(2*(beam-1)),2], label='lens1')
        sns.histplot(data=df_plot, x='lens3_median [dB]', kde=True, ax=axs[0+(2*(beam-1)),2], label='lens1')
        axs[0+(2*(beam-1)),2].set_title(f'Lens gain [dB] (beam{beam})')
        axs[0+(2*(beam-1)),2].set_xlim([-6,12])
        axs[0+(2*(beam-1)),2].set_xlabel('lens_median [dB]')
        axs[0+(2*(beam-1)),2].legend()
        
        sns.histplot(data=df_plot, x='lens_delta_max [dB]', kde=True, ax=axs[0+(2*(beam-1)),3])
        axs[0+(2*(beam-1)),3].set_title(f'Largest lens delta [dB] (beam{beam})')
        axs[0+(2*(beam-1)),3].set_xlim([0,6])
        
        
        sns.histplot(data=df_plot, x='rfic_offset_max [dB]', kde=True, binwidth=1, ax=axs[1+(2*(beam-1)),0])
        axs[1+(2*(beam-1)),0].set_title(f'Largest deviation of RFIC \n from 57 RFICs [dB] (beam{beam})')
        axs[1+(2*(beam-1)),0].set_xlim([-12,12])
        
        
        sns.histplot(data=df_plot, x='rfic_spread_max [dB]', kde=True, ax=axs[1+(2*(beam-1)),1])
        axs[1+(2*(beam-1)),1].set_title(f'Spread of 8 channels on RFIC [dB] (beam{beam})')
        axs[1+(2*(beam-1)),1].set_xlim([-6,12])
        
        sns.histplot(data=df_plot, x='rfic_minmax_max [dB]', kde=True, ax=axs[1+(2*(beam-1)),2])
        axs[1+(2*(beam-1)),2].set_title(f'Maximum deviation of channels on an RFIC [dB] (beam{beam})')
        axs[1+(2*(beam-1)),2].set_xlim([0,24])
        
        sns.histplot(data=df_plot, x='gain_median [dB]', kde=True, ax=axs[1+(2*(beam-1)),3], hue='lot')
        axs[1+(2*(beam-1)),3].set_title(f'Gain Median with Wafer Lots [dB]')
        axs[1+(2*(beam-1)),3].set_xlim([-6,12])
        axs[1+(2*(beam-1)),3].set_ylim([0,8])
        
    N = len(df_plot)
    plt.suptitle(f'{freq_set} GHz, N={N}')
    plt.tight_layout()
    
    freq_save = freq_set.replace('.', 'g')
    plt.savefig(f'{freq_save}.png', dpi=400)



























        
        
        
        


plot = False
if plot == True:
    
    df_ranked = pd.DataFrame()
    for beam in [1, 2]:
        for freq_set in freq_list:
            # load reference board
            find_measFiles(r'C:\Users\jmitchell\Downloads\MCR1_Rig1_TLM_00143', 'OP_2', beam, freq_set)
            load__measFiles(measFiles[0])
            col = np.argmin((meas_frequencies-float(freq_set))**2)
            gain = meas_array_gain[:, col]
            gain_median_143 = np.median(gain)
            
            # calculate FOMs
            df_freq = df[df['frequency [GHz]'] == float(freq_set)]
            df_freq = df_freq[df_freq['beam'] == beam]
            gain_medians = df_freq['gain_median [dB]']
            gain_spreads = df_freq['gain_spread [dB]']
            
            # gain medians relative
            gain_medians_relative = abs(df_freq['gain_median [dB]'] - np.median(df_freq['gain_median [dB]']))
            if delta_board == True:
                gain_medians_relative = abs(df_freq['gain_median [dB]'] - gain_median_143)
            df_freq['gain_median_relative [dB]'] = gain_medians_relative
            
            # rank gain medians
            numbers_array = np.array(gain_medians_relative)
            rank = (-numbers_array).argsort().argsort() + 1
            if delta_board == True:
                rank = numbers_array.argsort().argsort() + 1
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
    




















