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


file_path = r'C:\Scratch\Raw_Data'
map_tlm = np.genfromtxt(r'C:\Users\jmitchell\Documents\GitHub\jm_post_processing\20240227_tlm_map_plotter\20221019_TLMCalInputs\Mrk1_S2000_TLM_TX_ArrayGeometry_V20062022_CalInfo.csv', skip_header=2, dtype=float, delimiter=',')

def find_measFiles(path, fileString, beam, freq_set):
    global measFiles, files
    files = []
    for root, directories, file in os.walk(path):
        for file in file:
            if (file.endswith(".csv")) == True:
                files.append(os.path.join(root, file))
    measFiles = []
    for i in range(len(files)):
        if fileString in files[i] and 'eam' + str(beam) in files[i] and f'{freq_set}_GHz_4' in files[i]:
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


def plot_phaseDrift(deltaNew, title, cmin, cmax, cstp, f_set, Pol):
    global Z, Y, temp
    x = []
    y=[]
    rot = []
    for i in range(len(map_tlm)):
        x.append(map_tlm[i,4])
        # x.append(map_tlm[i,4])
        y.append(map_tlm[i,5])
        # y.append(map_tlm[i,5])
        rot.append(map_tlm[i,8])
        # rot.append(map_tlm[i,8])
    x = np.array(x)
    y = np.array(y)

    plt.figure(figsize=(6,4.5))
    
    print(f_set)
    col = np.argmin((meas_frequencies-f_set)**2)
    Z = deltaNew[:,col]#-np.mean(deltaNew)
    if Pol == 'Odd':
        Z = Z[::2]
    else:
        Z = Z[1::2]
    Y=3e8/(f_set*1e9)
    # Z = 1000.0*Z/360.0*Y
    

    m = MarkerStyle("s")
    m._transform.rotate_deg(float(rot[i]))
    cseg = int((cmax-cmin)/cstp)
    
    
    rfics = list(set(list(map_rfic['RFIC Number'])))
    for rfic in rfics:
        map_rfic_cut = map_rfic[map_rfic['RFIC Number'] == rfic]
        patches = map_rfic_cut['Patch Number']
        for lens in [0,1,2]:
            x_rfic = []; y_rfic = []
            for patch in patches:
                x_rfic.append(map_tlm_df[' Feed x [mm]'][patch-1+lens*float(len(map_tlm_df))/3])
                y_rfic.append(map_tlm_df[' Feed y [mm]'][patch-1+lens*float(len(map_tlm_df))/3])
                plt.text(map_tlm_df[' Feed x [mm]'][patch-1+lens*float(len(map_tlm_df))/3]-0.5, map_tlm_df[' Feed y [mm]'][patch-1+lens*float(len(map_tlm_df))/3]-0.5, patch, fontsize=3)
            plt.plot(x_rfic, y_rfic, 'm-', linewidth=1.0, alpha=0.7)
    
    
    plt.scatter(x, y, c=Z, marker=m, s=50, edgecolors='black', cmap = cm.get_cmap('jet', cseg), alpha=1.0)
    plt.colorbar()  

    plt.clim(cmin, cmax)
    plt.xlabel('X [mm]'); plt.ylabel('Y [mm]')
    plt.title(title)
    plt.tight_layout()

beam = 2
Pol = 'Odd'
freq_list = ['27.50', '28.00', '28.50', '29.00', '29.50', '30.00', '30.50', '31.00']


for beam in [1,2]:
    for Pol in ['Odd', 'Even']:
        count = 0
        out_array_1 = np.zeros([len(map_tlm),8])
        out_array_2 = np.zeros([len(map_tlm),8])
        for freq_set in freq_list:
            
            
            find_measFiles(file_path, 'OP_2', beam, freq_set)
            load__measFiles(measFiles[0])
            meas_array_gain_tot = meas_array_gain*0.0
            meas_array_gain_list = []
            for measFile in measFiles:
                load__measFiles(measFile)
                meas_array_gain_list.append(meas_array_gain)
            meas_array_gain_av = np.average(meas_array_gain_list, axis=0)
            
            meas_array_gain_std = np.std(meas_array_gain_list, axis=0)
            
            
            
            map_tlm_df = pd.read_csv(r'C:\Users\jmitchell\Documents\GitHub\jm_post_processing\20240227_tlm_map_plotter\20221019_TLMCalInputs\Mrk1_S2000_TLM_TX_ArrayGeometry_V20062022_CalInfo.csv', header=1)
            map_rfic = pd.read_csv(r'C:\Users\jmitchell\Documents\GitHub\jm_post_processing\20240227_tlm_map_plotter\20221019_TLMCalInputs\MK1_TX_TLM_RFIC_Patch_Feed_Mapping.csv')
            
            plot_phaseDrift(meas_array_gain_av, f'Gain (average) [dB], N = {len(measFiles)} \n Freq = {freq_set} GHz, Beam {beam}, {Pol}', 10.0, 40.0, 1.0, float(meas_params['f_c']), Pol)
            out_array_1[:,count] = Z

            freq_str = freq_set.replace('.', 'g')            
            plt.savefig(f'Av_{freq_str}_beam{beam}_{Pol}.png', dpi=400)
            
            
            
            plot_phaseDrift(meas_array_gain_std, f'Gain (stdev) [dB], N = {len(measFiles)} \n Freq = {freq_set} GHz, Beam {beam}, {Pol}', 0.0, 5.0, 0.1, float(meas_params['f_c']), Pol)
            out_array_2[:,count] = Z
            plt.savefig(f'Stdev_{freq_str}_beam{beam}_{Pol}.png', dpi=400)
            
            count = count+1
            
        df = pd.DataFrame(np.concatenate([np.array(freq_list).reshape(1,8), out_array_1], axis=0))
        new_header = df.iloc[0]; df = df[1:]; df.columns = new_header
        df.to_excel(f'Gain (average) [dB], N = {len(measFiles)}, Beam {beam}, {Pol}.xlsx', index=True)
        
        df = pd.DataFrame(np.concatenate([np.array(freq_list).reshape(1,8), out_array_2], axis=0))
        new_header = df.iloc[0]; df = df[1:]; df.columns = new_header
        df.to_excel(f'Gain (stdev) [dB], N = {len(measFiles)}, Beam {beam}, {Pol}.xlsx', index=True)
        

















