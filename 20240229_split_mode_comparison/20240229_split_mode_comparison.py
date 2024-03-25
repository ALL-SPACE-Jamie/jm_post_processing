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


file_path = r'C:\Users\jmitchell\Downloads\2It\forComp'
map_tlm = np.genfromtxt(r'C:\Users\jmitchell\Documents\GitHub\jm_post_processing\20240227_tlm_map_plotter\20221019_TLMCalInputs\Mrk1_S2000_TLM_TX_ArrayGeometry_V20062022_CalInfo.csv', skip_header=2, dtype=float, delimiter=',')

def find_measFiles(path, fileString, beam, freq_set, board):
    global measFiles, files
    files = []
    for root, directories, file in os.walk(path):
        for file in file:
            if (file.endswith(".csv")) == True:
                files.append(os.path.join(root, file))
    measFiles = []
    for i in range(len(files)):
        if fileString in files[i] and 'eam' + str(beam) in files[i] and f'{freq_set}_GHz_4' in files[i] and f'329-00{board}' in files[i] and 'teration_1' in files[i]:
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

                


# set-up      

board = 718



for beam in [1,2]:
    for f_set in ['27.50', '28.00', '28.50', '29.00', '29.50', '30.00', '30.50', '31.00']:
        fig, axs = plt.subplots(nrows=2, ncols=2, figsize=(20, 10))
        f_set_float = float(f_set)
        
        # load the reference and save
        find_measFiles(r'C:\Users\jmitchell\Downloads\2It\ref', 'OP_2', beam, f_set, board)
        load__measFiles(measFiles[0])
        f_loc = np.argmin((meas_frequencies-f_set_float)**2)
        reference = meas_array_gain[:,f_loc]
        reference_phase = meas_array_phase[:,f_loc]
        ref_label = measFiles[0].split('\\')[-1].split('_')[-10:-8]+[meas_params['barcodes']]
        axs[0,0].plot(reference, 'k--', label=['REF: '] + measFiles[0].split('\\')[-1].split('_')[-10:-8]+[meas_params['barcodes']]+[meas_params['barcodes']])
        
        # plots
        find_measFiles(file_path, 'OP_2', beam, f_set, board)
        for meas_file in measFiles:
            load__measFiles(meas_file)
            axs[0,0].plot(meas_array_gain[:,f_loc], label=meas_file.split('\\')[-1].split('_')[-10:-8]+[meas_params['barcodes']]+[meas_params['barcodes']])
            axs[1,0].plot(reference-meas_array_gain[:,f_loc], label=meas_file.split('\\')[-1].split('_')[-10:-8]+[meas_params['barcodes']])
            axs[0,1].plot(meas_array_phase[:,f_loc], label=meas_file.split('\\')[-1].split('_')[-10:-8]+[meas_params['barcodes']])
            delta_phase = reference_phase-meas_array_phase[:,f_loc]
            for j in range(len(delta_phase)):
                if delta_phase[j]>270:
                    delta_phase[j] = delta_phase[j]-360
                if delta_phase[j]<-270:
                    delta_phase[j] = delta_phase[j]+360
            axs[1,1].plot(delta_phase, label=meas_file.split('\\')[-1].split('_')[-10:-8]+[meas_params['barcodes']])
        
        # plot format
        for i in range(2):
            axs[i,0].legend()
            axs[i,0].set_xlabel('port')
            axs[i,0].set_ylabel('gain [dB]')
            axs[i,0].grid('on')
            axs[i,1].legend()
            axs[i,1].set_xlabel('port')
            axs[i,1].set_ylabel('phase [deg]')
            axs[i,1].grid('on')
        axs[0,0].set_ylim([-10,40])
        axs[1,0].set_ylim([-10,10])
        axs[0,1].set_ylim([-360,360*2])
        axs[1,1].set_ylim([-10,10])
        axs[0,0].set_title('raw')
        axs[1,0].set_title(f'delta from: {ref_label}')
        axs[0,1].set_title('raw')
        axs[1,1].set_title(f'delta from: {ref_label}')
        fig.suptitle(f'board{board}, {f_set} GHz, beam {beam}')
        plt.tight_layout()
        f_str = f_set.replace('.', 'g')      
        plt.savefig(f'board{board}_beam{beam}_f{f_str}.png')
        
            
            
        
