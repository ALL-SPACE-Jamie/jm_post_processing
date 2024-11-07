# -*- coding: utf-8 -*-
"""
Created on Fri Jul 19 14:55:51 2024

@author: jmitchell
"""

import scipy.io
import numpy as np
import matplotlib.pyplot as plt
import os

def find__measFiles(filePath, fileString, fileString2, fileString3, fileString4):
    files = []
    for root, directories, file in os.walk(filePath):
        for file in file:
            if (file.endswith(".mat")) == True:
                files.append(os.path.join(root, file))
    measFiles = []
    sizeLog = []
    for i in range(len(files)):
        if fileString in files[i] and fileString2 in files[i] and fileString3 in files[i] and fileString4 in files[i]:
            if os.path.getsize(files[i]) > 1000:
                measFiles.append(files[i])
    return measFiles

def load_mat(file_path):
    # Load the .mat file
    mat = scipy.io.loadmat(file_path)
    
    headings = ['fname', 'theta', 'f_t', 'pol_t', 'vals_t', 'f_r', 'pol_r', 'vals_r', 'vals_r2']
    indexes = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    
    master_dict = {}
    
    for idx in range(len(headings)):
        master_dict[headings[idx]] = mat['TF'][0][0][indexes[idx]][0]
        
    return master_dict

def col_select(file):
    col = 'k'
    if '50deg' in file:
        col = 'b'
    if '65deg' in file:
        col = 'orange'
    if '85deg' in file:
        col = 'red'
        
    return col

def plot_cuts(freq, fom, meas_entry, ylims):
    fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(15, 7))
    
    interp = 'OFF'
    files = find__measFiles(r"C:\scratch\20240719\OneDrive_1_19-07-2024", 'GTEIRP', freq, interp, 'TF')
    files_orig = find__measFiles(r"C:\scratch\20240719\OneDrive_1_19-07-2024", 'GTEIRP', freq, 'Original', 'TF')
    files = files + files_orig
    for file in files:
        master_dict = load_mat(file)
        temperature = file.split('\\')[5]
        col = col_select(file)
        axs[0].plot(np.array(master_dict['theta'].reshape(1,len(master_dict['theta'])))[0], np.array(master_dict[meas_entry])[0], color=col, marker='x', label=temperature + '\n' + master_dict['fname'])
    axs[0].legend(loc='lower left')
    axs[0].set_ylim(ylims)
    axs[0].set_xlabel('theta [deg]')
    axs[0].set_ylabel(f'{fom}')
    axs[0].set_title(f'{freq} Interp OFF')
    axs[0].grid()
    
    interp = 'ON'
    files = find__measFiles(r"C:\scratch\20240719\OneDrive_1_19-07-2024", 'GTEIRP', freq, interp, 'TF')
    files_orig = find__measFiles(r"C:\scratch\20240719\OneDrive_1_19-07-2024", 'GTEIRP', freq, 'Original', 'TF')
    files = files + files_orig
    for file in files:
        master_dict = load_mat(file)
        temperature = file.split('\\')[5]
        col = col_select(file)
        axs[1].plot(np.array(master_dict['theta'].reshape(1,len(master_dict['theta'])))[0], np.array(master_dict[meas_entry])[0], color=col, marker='x', label=temperature + '\n' + master_dict['fname'])
    axs[1].legend(loc='lower left')
    axs[1].set_ylim(ylims)
    axs[1].set_xlabel('theta [deg]')
    axs[1].set_ylabel(f'{fom}')
    axs[1].set_title(f'{freq} Interp ON')
    axs[1].grid()
    
    plt.savefig(f'{freq}_{fom}.png', dpi=400)

for freq_select in ['18g3', '19g5', '20g7']:
    plot_cuts(freq_select, 'GT', 'vals_r', [0,12])

for freq_select in ['28g1', '29g35', '30g55']:
    plot_cuts(freq_select, 'ERIP', 'vals_t', [30,50])

