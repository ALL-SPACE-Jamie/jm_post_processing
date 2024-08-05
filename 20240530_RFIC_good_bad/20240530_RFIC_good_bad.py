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
def find_measFiles(path, fileString, beam, freq_set, it):
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
                    
def rfic_passfail(pass_thresh, beam, freq_set, file_path, map_tlm_df, map_rfic):
    global df, df_flagged, tlm_log

    find_measFiles(file_path, 'OP_2', beam, freq_set, 1)
    
    out_array = np.zeros([0,9])
    gain_array = np.zeros([456,0])
    
    # generate ref
    for meas_file in measFiles:
        load__measFiles(meas_file)
        col = np.argmin((meas_frequencies-float(freq_set))**2)
        gain = meas_array_gain[:, col]
        gain_array = np.concatenate((gain_array, gain.reshape(456,1)-np.median(gain)), axis=1)
    all_gain_ref = np.median(gain_array, axis=1)
    all_gain_std = np.std(gain_array, axis=1)
    
    # loop through files and make an output array of rfic information
    for meas_file in measFiles:
        load__measFiles(meas_file)
        col = np.argmin((meas_frequencies-float(freq_set))**2)
        gain = meas_array_gain[:, col]
        gain_array = np.concatenate((gain_array, gain.reshape(456,1)-np.median(gain)), axis=1)
        deviation = gain - np.median(gain) - all_gain_ref
        tlm_SN = np.full((len(gain)), meas_params['barcodes'])
        lens = np.concatenate((np.full((int(len(gain)/3)), 1), np.full((int(len(gain)/3)), 2), np.full((int(len(gain)/3)), 3)), axis=0)
        ports = np.linspace(1,len(gain), num=len(gain))
        map_rfic = pd.read_csv(r'C:\GitHub\jm_post_processing\20240227_tlm_map_plotter\20221019_TLMCalInputs\MK1_TX_TLM_RFIC_Patch_Feed_Mapping.csv')
        map_rfic = np.concatenate((np.array(map_rfic), np.array(map_rfic), np.array(map_rfic)), axis=0)
        zipped_arr = np.empty((map_rfic.shape[0]+map_rfic.shape[0], map_rfic.shape[1]), dtype=map_rfic.dtype)
        zipped_arr[0::2] = map_rfic
        zipped_arr[1::2] = map_rfic
        out_array_file = np.concatenate((tlm_SN.reshape(456,1), lens.reshape(456,1), ports.reshape(456,1), gain.reshape(456,1), deviation.reshape(456,1), zipped_arr), axis=1)
        out_array = np.concatenate((out_array, out_array_file), axis=0)    
    
    headers = ['TLM S/N', 'lens', 'port', f'gain (beam{beam}) [dB]', f'deviation (beam{beam}) [dB]', 'RFIC', 'channel_H', 'channel_V', 'patch']
    df = pd.DataFrame(out_array, columns=headers)
    
    # flag rfics, output df and plot
    tlms = list(set(df['TLM S/N']))
    tlms.sort()
    lenses = [1, 2, 3]
    RFICs = np.linspace(1,19,num=19)
    
    tlm_log = []
    tlm_number_log = []
    lens_log = []
    rfic_log = []
    max_dev_log = []
    chanel_dev_fromIC_log = []
    av_dev_log = []
    fail_flag_log = []
    pass_flag_log = []
    max_channel_dev_log = []
    
    for tlm in tlms:
        df_tlm = df[df['TLM S/N'] == tlm]
        for lens in lenses:
            df_tlm_lens = df_tlm[df_tlm['lens'] == lens]
            for RFIC in RFICs:
                df_tlm_lens_rfic = df_tlm_lens[df_tlm_lens['RFIC'] == RFIC]
                devs = np.array(df_tlm_lens_rfic[f'deviation (beam{beam}) [dB]'])
                gains = np.array(df_tlm_lens_rfic[f'gain (beam{beam}) [dB]'])
                max_dev_abs = np.max(abs(devs))
                av_dev = np.median(devs)
                loc = np.argmax(abs(devs))
                max_dev = devs[loc]
                std_dev = np.std(devs)
                loc_furthest_channel = np.argmax((gains-np.median(gains))**2)
                max_channel_dev = gains[loc_furthest_channel]
                if av_dev < pass_thresh and max_dev < 2.0:
                    flag = 1
                else:
                    flag = 0
                tlm_log.append(tlm)
                tlm_number_log.append(int(tlm[-3:]))
                lens_log.append(lens)
                rfic_log.append(RFIC)
                max_dev_log.append(max_dev)
                av_dev_log.append(av_dev)
                max_channel_dev_log.append(max_channel_dev)
                fail_flag_log.append(flag)
                pass_flag_log.append((flag-1)*-1)
                
    df_flagged = pd.DataFrame({
        'TLM S/N': tlm_log,
        'TLM No': tlm_number_log,
        'lens': lens_log,
        'RFIC': rfic_log,
        f'Max deviation of the worst channel on an RFIC from typical RFIC behaviour (beam{beam}) [dB]': max_dev_log,
        f'Average deviation of RFIC from typical RFIC behaviour (beam{beam}) [dB]': av_dev_log,
        f'Max deviation of the worst channel on an RFIC from the average response of that RFIC (beam{beam}) [dB]': max_channel_dev_log,
        f'fail flag (beam{beam}, pass_thresh={pass_thresh}dB)': fail_flag_log,
        f'pass flag (beam{beam}, pass_thresh={pass_thresh}dB)': pass_flag_log
        })
    
    plt.plot(np.linspace(1,len(df_flagged), num=len(df_flagged)),
             np.cumsum(df_flagged[f'fail flag (beam{beam}, pass_thresh={pass_thresh}dB)']), 
             label=f'beam{beam}, pass_thresh={pass_thresh}dB')
    plt.xlabel('IC tested')
    plt.ylabel('cumultive fail')
    plt.legend(fontsize=12)
    plt.grid('on')       
    plt.savefig('fig.png', dpi=400)
    
    
def tlm_wafermap(tlm_log):
    global df_wafermap
    
    wafermap_array = np.zeros([0,4])
    
    tlms = list(set(tlm_log))
    
    sheet_names = (pd.ExcelFile('CIL local - Tx TLM comms and UIDzero check.xlsx')).sheet_names
    
    for tlm in tlms:
    
        try:
            
            for sheet in sheet_names:
                if f'{tlm}' in sheet:
                    sheet_name = sheet
        
            df_tlmic = pd.read_excel('CIL local - Tx TLM comms and UIDzero check.xlsx', sheet_name=sheet_name)
            
            df_tlmic_idx = list(df_tlmic[df_tlmic['Tx TLM:'] == 'Lens'].index)
            
            out_arrays = {}
            for lens in [1, 2, 3]: 
                if lens < 3:
                    df_tlmic_l = df_tlmic[df_tlmic_idx[lens-1]+1:df_tlmic_idx[lens-1]+2+19]
                else:
                    df_tlmic_l = df_tlmic[df_tlmic_idx[lens-1]+1:df_tlmic_idx[lens-1]+2+18]
                
                tlm_list = np.array([tlm]*len(df_tlmic_l)).reshape(len(df_tlmic_l),1)
                lens_list = np.array([lens]*len(df_tlmic_l)).reshape(len(df_tlmic_l),1)
                rfic_list = np.array(list(df_tlmic_l[f'{tlm}'])).reshape(len(df_tlmic_l),1)
                uid_list = np.array(list(df_tlmic_l['Unnamed: 8'])).reshape(len(df_tlmic_l),1)
                
                out_arrays[lens] = np.concatenate((tlm_list, lens_list, rfic_list, uid_list), axis=1)
            
            out_array_lenses = np.concatenate((out_arrays[1], out_arrays[2], out_arrays[3]), axis=0)
            
            wafermap_array = np.concatenate((wafermap_array, out_array_lenses), axis=0)
        
        except:
            
            print(f'{tlm} not found')
            
        df_wafermap = pd.DataFrame(wafermap_array, columns = ['TLM S/N', 'lens', 'rfic', 'uid'])

## code

# load
file_path = r'C:\Users\jmitchell\Downloads\P3Tx____'
map_tlm_df = pd.read_csv(r'C:\GitHub\jm_post_processing\20240227_tlm_map_plotter\20221019_TLMCalInputs\Mrk1_S2000_TLM_TX_ArrayGeometry_V20062022_CalInfo.csv', header=1)
map_rfic = pd.read_csv(r'C:\GitHub\jm_post_processing\20240227_tlm_map_plotter\20221019_TLMCalInputs\MK1_TX_TLM_RFIC_Patch_Feed_Mapping.csv')

# params
freq_set = '29.50'
pass_thresh = -5.0

# run
beam_log = {}
for beam in [1, 2]:
    plt.figure(figsize=(12,6))
    rfic_passfail(pass_thresh, beam, freq_set, file_path, map_tlm_df, map_rfic)       
    tlm_wafermap(tlm_log)
    beam_log[f'df_flagged (beam{beam})'] = df_flagged.copy()

# dev
for beam in [1,2]:
    uid_list = []
    for i in range(len(df_flagged)):
        row = df_flagged.iloc[i]
        df_wafermap_chosen = df_wafermap[df_wafermap['TLM S/N']==row['TLM S/N']]
        df_wafermap_chosen = df_wafermap_chosen[df_wafermap_chosen['lens']==str(row['lens'])]
        df_wafermap_chosen = df_wafermap_chosen[df_wafermap_chosen['rfic']==str(int(row['RFIC']))]
        if len(list(df_wafermap_chosen['uid'])) > 0:
            uid_list.append(list(df_wafermap_chosen['uid'])[0])
        else:
            uid_list.append('not found')
            
    beam_log[f'df_flagged (beam{beam})']['uid'] = uid_list
    
    x_co_log = []
    y_co_log = []
    wafer_log = []
    for hex_num in beam_log[f'df_flagged (beam{beam})']['uid']:
    # hex_num = 'c0063c5a'
        if hex_num == 'not found':
            x_co_log.append(1e9)
            y_co_log.append(1e9)
            wafer_log.append(0)
        else:
            wafer_id_chunk = hex_num[0:5]
            wafer_id_binary = bin(int(wafer_id_chunk, 16))
            wafer_id_num = int(wafer_id_binary[2:],2)
            pos_id_hex = hex_num[-3:]
            pos_id_binary = bin(int(pos_id_hex, 16))        
            x_co_binary = pos_id_binary[2:8]
            y_co_binary = pos_id_binary[-6:]
            x_co_num = int(x_co_binary,2)
            y_co_num = int(y_co_binary,2)
            x_co_log.append(x_co_num)
            y_co_log.append(y_co_num)
            wafer_log.append(wafer_id_num)
            
    beam_log[f'df_flagged (beam{beam})']['x_co'] = x_co_log
    beam_log[f'df_flagged (beam{beam})']['y_co'] = y_co_log
    beam_log[f'df_flagged (beam{beam})']['wafer'] = wafer_log
    
    # wafer position plot
    plt.figure()
    df_flagged_fail = beam_log[f'df_flagged (beam{beam})'][beam_log[f'df_flagged (beam{beam})'][f'fail flag (beam{beam}, pass_thresh={pass_thresh}dB)']==1]
    df_flagged_pass = beam_log[f'df_flagged (beam{beam})'][beam_log[f'df_flagged (beam{beam})'][f'fail flag (beam{beam}, pass_thresh={pass_thresh}dB)']==0]
    
    plt.plot(df_flagged_pass['x_co'], df_flagged_pass['y_co'], 'go')
    plt.plot(df_flagged_fail['x_co'], df_flagged_fail['y_co'], 'rX', markersize=10)
    plt.xlim([20,80])
    plt.ylim([-10,60])
    plt.xlabel('x'); plt.ylabel('y')
    plt.grid()

plt.close('all')
for beam in [1,2]:
    plt.figure()
    wafers = list(set(beam_log[f'df_flagged (beam{beam})']['wafer']))
    dead_log = []
    count_log= []
    for wafer in wafers:
        df_wafer = beam_log[f'df_flagged (beam{beam})'][beam_log[f'df_flagged (beam{beam})']['wafer']==wafer]
        dead_log.append(100.0*np.sum(df_wafer[f'fail flag (beam{beam}, pass_thresh={pass_thresh}dB)'])/len(df_wafer))
        # dead_log.append(np.sum(df_wafer[f'fail flag (beam{beam}, pass_thresh={pass_thresh}dB)']))
        count_log.append(len(df_wafer))
        plt.plot(df_wafer['x_co'], df_wafer['y_co'], 'o', markersize=10, label=wafer)
        plt.xlim([20,80])
        plt.ylim([-10,60])
    plt.legend()