# -*- coding: utf-8 -*-
"""
Created on Mon Dec 18 16:40:42 2023

@author: jmitchell
"""
#imports
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
        if fileString in files[i] and 'eam' + str(beam) in files[i] and f'{freq_set}_GHz_4' in files[i] and f'teration_{it}' in files[i]:
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


def plot_tlm_map(array_in, title, cmin, cmax, cstp, f_set, plot_no, tick_step, delta_pol, align=False, col_map = 'jet'):
    global Z, Y, temp, Z_trim, map_tlm_df
    
    # get x and y positions (this still uses the map_tlm rather than the dataframe)
    x = []
    y=[]
    rot = []
    for i in range(len(map_tlm)):
        x.append(map_tlm[i,4])
        y.append(map_tlm[i,5])
        rot.append(map_tlm[i,8])
    x = np.array(x)
    y = np.array(y)
    
    # lens specific coordinate rotation (this still uses the map_tlm rather than the dataframe)
    if align == True:
        x_shift = map_tlm[:,4] - map_tlm[:,2]
        y_shift = map_tlm[:,5] - map_tlm[:,3]
        angle = x_shift*0.0
        for i in range(len(map_tlm)):
            if map_tlm[i,0] == 1:
                angle[i] = 0.0
            if map_tlm[i,0] == 2:
                angle[i] = -102.5
            if map_tlm[i,0] == 3:
                angle[i] = -205
        x_rot = x_shift*cos(angle*np.pi/180.0)-y_shift*sin(angle*np.pi/180.0)
        y_rot = y_shift*cos(angle*np.pi/180.0)+x_shift*sin(angle*np.pi/180.0)
        x_new = x_rot + map_tlm[:,2]
        y_new = y_rot + map_tlm[:,3]
        x = x_new.copy()
        y = y_new.copy()
    
    # select the column of data
    col = np.argmin((meas_frequencies-f_set)**2)
    Z = array_in[:,col]
    
    # odd ports
    Z_trim = Z[::2]
    Z_trim_pol1 = Z_trim.copy()
    
    # marker for odd ports
    m = MarkerStyle('D', fillstyle='left')
    m._transform.rotate_deg(float(rot[i]+45))
    
    # map tlm as a df (and roated if needed)
    map_tlm_df = pd.read_csv(r'C:\Users\jmitchell\Documents\GitHub\jm_post_processing\20240227_tlm_map_plotter\20221019_TLMCalInputs\Mrk1_S2000_TLM_TX_ArrayGeometry_V20062022_CalInfo.csv', header=1)
        
    if align == True:
        map_tlm_df[' Feed x [mm] shift'] =   map_tlm_df[' Feed x [mm]'] -  map_tlm_df[' Lens x [mm]']
        map_tlm_df[' Feed y [mm] shift'] =   map_tlm_df[' Feed y [mm]'] -  map_tlm_df[' Lens y [mm]']
        angle = np.array(map_tlm_df[' Feed x [mm] shift'])*0.0
        for i in range(len(map_tlm_df[' Feed x [mm] shift'])):
            if map_tlm_df['Lens no.'][i] == 1:
                angle[i] = 0.0
            if map_tlm_df['Lens no.'][i] == 2:
                angle[i] = -102.5
            if map_tlm_df['Lens no.'][i] == 3:
                angle[i] = -205
        map_tlm_df['angle'] = angle
        map_tlm_df['x_rot'] = map_tlm_df[' Feed x [mm] shift']*cos(map_tlm_df['angle']*np.pi/180.0)-map_tlm_df[' Feed y [mm] shift']*sin(map_tlm_df['angle']*np.pi/180.0)
        map_tlm_df['y_rot'] = map_tlm_df[' Feed y [mm] shift']*cos(map_tlm_df['angle']*np.pi/180.0)+map_tlm_df[' Feed x [mm] shift']*sin(map_tlm_df['angle']*np.pi/180.0)
        map_tlm_df['x_new'] = map_tlm_df['x_rot'] + map_tlm_df[' Lens x [mm]']
        map_tlm_df['y_new'] = map_tlm_df['y_rot'] + map_tlm_df[' Lens y [mm]']
    
    # plot rfics
    map_rfic = pd.read_csv(r'C:\Users\jmitchell\Documents\GitHub\jm_post_processing\20240227_tlm_map_plotter\20221019_TLMCalInputs\MK1_TX_TLM_RFIC_Patch_Feed_Mapping.csv')
    rfics = list(set(list(map_rfic['RFIC Number'])))
    for rfic in rfics:
        map_rfic_cut = map_rfic[map_rfic['RFIC Number'] == rfic]
        patches = map_rfic_cut['Patch Number']
        for lens in [0,1,2]:
            x_rfic = []; y_rfic = []
            for patch in patches:
                if align == True:
                    x_rfic.append(map_tlm_df['x_new'][patch-1+lens*float(len(map_tlm_df))/3])
                    y_rfic.append(map_tlm_df['y_new'][patch-1+lens*float(len(map_tlm_df))/3])
                    axs[plot_no].text(map_tlm_df['x_new'][patch-1+lens*float(len(map_tlm_df))/3], 
                                      map_tlm_df['y_new'][patch-1+lens*float(len(map_tlm_df))/3], 
                                      patch, fontsize=3)
                else:
                    x_rfic.append(map_tlm_df[' Feed x [mm]'][patch-1+lens*float(len(map_tlm_df))/3])
                    y_rfic.append(map_tlm_df[' Feed y [mm]'][patch-1+lens*float(len(map_tlm_df))/3])
                    axs[plot_no].text(map_tlm_df[' Feed x [mm]'][patch-1+lens*float(len(map_tlm_df))/3], 
                                      map_tlm_df[' Feed y [mm]'][patch-1+lens*float(len(map_tlm_df))/3], 
                                      patch, fontsize=3)
            axs[plot_no].plot(x_rfic, y_rfic, 'm-', linewidth=1.0, alpha=0.7)
    
    # scatter plot for odd pol
    v = np.linspace(cmin, cmax, int((cmax-cmin)/cstp), endpoint=True)
    cmap_chosen = cm.get_cmap(col_map, int((cmax-cmin)/cstp))
    cntr = axs[plot_no].scatter(x, y, c=Z_trim, marker=m, s=200, edgecolors='black', linewidths=0.5, cmap = cmap_chosen, vmin=min(v), vmax=max(v), alpha=1.0)
    
    # even pol
    Z_trim = Z[1::2]
    Z_trim_pol2 = Z_trim.copy()
    
    # marker for even ports
    m = MarkerStyle('D', fillstyle='right')
    m._transform.rotate_deg(float(rot[i]+45))
    
    # scatter plot for even pol
    cntr = axs[plot_no].scatter(x, y, c=Z_trim, marker=m, s=200, edgecolors='black', linewidths=0.5, cmap = cmap_chosen, vmin=min(v), vmax=max(v), alpha=1.0)
    
    # scatter plot (on-top) for delta pol
    if delta_pol == True:
        m = MarkerStyle('s')
        m._transform.rotate_deg(float(rot[i]))
        cntr = axs[plot_no].scatter(x, y, c=(Z_trim_pol1-Z_trim_pol2), marker=m, s=200, edgecolors='black', linewidths=0.5, vmin=min(v), vmax=max(v), cmap = cmap_chosen, alpha=1.0)
    cbar = plt.colorbar(cntr) 
    cbar.set_ticks(np.arange(min(v), max(v)+tick_step, tick_step))
    axs[plot_no].set_xlabel('X [mm]'); axs[plot_no].set_ylabel('Y [mm]')
    axs[plot_no].set_title(title)

# set-up
file_path = r'C:\Scratch\20240312\bare_board'
map_tlm = np.genfromtxt(
    r'C:\Users\jmitchell\Documents\GitHub\jm_post_processing\20240227_tlm_map_plotter\20221019_TLMCalInputs\Mrk1_S2000_TLM_TX_ArrayGeometry_V20062022_CalInfo.csv', 
    skip_header=2, dtype=float, delimiter=',')

freq_list = ['27.50', '28.00', '28.50', '29.00', '29.50', '30.00', '30.50', '31.00']
# freq_list = ['29.00']
align = True
beam_list = [1, 2]
it = 2

# run
for gain_phase in ['gain', 'phase']:
    
    for delta_pol in [False, True]:
        
        if delta_pol == True:
            if gain_phase == 'gain':
                vmax_std = 6.0
                v_OP = 8.0
                v_RFA = v_OP*1.0
                v_OP_step = 0.01
                v_RFA_step = v_OP_step*1.0
                v_spread_step = 0.01
                tick_step = 1
            if gain_phase == 'phase':
                vmax_std = 90
                v_OP = 360
                v_RFA = v_OP*1.0#3.0
                v_OP_step = 0.01
                v_RFA_step = v_OP_step*1.0
                v_spread_step = 0.01
                tick_step = 45.0
                
        if delta_pol == False:
            if gain_phase == 'gain':
                vmax_std = 6.0
                v_OP = 40.0
                v_RFA = v_OP*1.0
                v_OP_step = 0.01
                v_RFA_step = v_OP_step*1.0
                v_spread_step = 0.01
                tick_step = 2
            if gain_phase == 'phase':
                vmax_std = 90
                v_OP = 360
                v_RFA = v_OP*1.0#3.0
                v_OP_step = 0.01
                v_RFA_step = v_OP_step*1.0
                v_spread_step = 0.01
                tick_step = 45.0
        
        for f_type in ['OP_2', 'RFA']:
            
            # initialise out_array
            count = 0
            out_array = np.zeros([len(map_tlm)*2,len(freq_list)*2*len(beam_list)])
            
            for beam in beam_list:
                
                for freq_set in freq_list:
                    # find measurement files and load one of them to make an empty matrix
                    find_measFiles(file_path, f_type, beam, freq_set, it)
                    load__measFiles(measFiles[0])
                    meas_array_tot = meas_array_gain*0.0
                    meas_array_list = []
                    
                    # cycle through meas files to make average and stdev arrays
                    for measFile in measFiles:
                        load__measFiles(measFile)
                        if gain_phase == 'gain':
                            meas_array_list.append(meas_array_gain)
                        if gain_phase == 'phase':
                            meas_array_list.append(meas_array_phase)
                    meas_array_av = np.median(meas_array_list, axis=0)
                    meas_array_std = np.std(meas_array_list, axis=0)

                    # initialise figure
                    fig, axs = plt.subplots(nrows=1, ncols=3, figsize=(40, 9))
                    
                    # make plots for OP or RFA
                    if 'OP' in f_type:
                        plot_tlm_map(meas_array_av, f'({f_type}) {gain_phase} (average), N = {len(measFiles)} \n Freq = {freq_set} GHz, Beam {beam}, Delta Pol={delta_pol}, Lens Align={align}',
                                     -v_OP, v_OP, v_OP_step, float(meas_params['f_c']),0,tick_step=tick_step,delta_pol=delta_pol, align=align)
                    elif 'RFA' in f_type:
                        plot_tlm_map(meas_array_av, f'({f_type}) {gain_phase} (average), N = {len(measFiles)} \n Freq = {freq_set} GHz, Beam {beam}, Delta Pol={delta_pol}, Lens Align={align}',
                                     -v_RFA, v_RFA, v_RFA_step, float(meas_params['f_c']),0, tick_step=tick_step,delta_pol=delta_pol, align=align)
                    
                    # add to out_array
                    out_array[:,count] = Z
                    
                    # replace the decimal point in the frequency for filenames
                    freq_str = freq_set.replace('.', 'g')            
                    
                    # plot the stdev
                    plot_tlm_map(meas_array_std, f'({f_type}) {gain_phase} (stdev), N = {len(measFiles)} \n Freq = {freq_set} GHz, Beam {beam}, Delta Pol={delta_pol}, Lens Align={align}',
                                 0.0, vmax_std, v_spread_step, float(meas_params['f_c']),1, tick_step=tick_step,delta_pol=delta_pol, align=align)
                    
                    # plot the cartesian
                    # for measFile in measFiles:
                    load__measFiles(measFile)
                    col = np.argmin((meas_frequencies-float(freq_set))**2)
                    axs[2].plot(np.linspace(1,len(meas_array),num = len(meas_array)), meas_array_av[:,col])
                    axs[2].set_xlabel('port')
                    axs[2].set_ylabel(f'{gain_phase}')
                    axs[2].set_xlim([0, 500])
                    axs[2].set_xticks(np.linspace(0, 500, num=int(500/50)+1))
                    axs[2].set_title(f'({f_type}) {gain_phase} (average), N = {len(measFiles)} \n Freq = {freq_set} GHz, Beam {beam}, Lens Align={align}')
                    axs[2].grid('on')
                        
                    # add the stdev to the outarray
                    out_array[:,count+1] = Z
                    
                    # add to count
                    count = count+2
                    
                    # chck the directory
                    isExist = os.path.exists(f'{file_path}\\analysis')
                    if not isExist:
                        os.makedirs(f'{file_path}\\analysis')
                    
                    # save the figure
                    plt.savefig(f'{file_path}\\analysis\\{f_type}_{freq_str}_beam{beam}_delta{delta_pol}_{gain_phase}.png', dpi=200)
                    
            # make the output excel
            freq_list_av = [s + '_av' for s in freq_list]
            freq_list_std = [s + '_std' for s in freq_list]
            header_list = []
            for beam in beam_list:
                for i in range(len(freq_list)):
                    header_list.append(freq_list_av[i]+f'_beam{beam}'); header_list.append(freq_list_std[i]+f'_beam{beam}')
            df = pd.DataFrame(out_array, columns = header_list)
            lens_list = (list(map_tlm_df['Lens no.'])+list(map_tlm_df['Lens no.']))
            lens_list.sort()
            df['Lens no.'] = lens_list
            col = df.pop("Lens no.")
            df.insert(0, col.name, col)
            pol = []
            for i in range(len(map_tlm)):
                pol.append('Odd')
                pol.append('Even')
            df['pol'] = pol.copy()
            col = df.pop("pol")
            df.insert(0, col.name, col)
            df.index += 1 
            df.to_excel(f'{file_path}\\analysis\\{f_type} {gain_phase}, N = {len(measFiles)}.xlsx', index=True)