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
from scipy.signal import savgol_filter
import os
import glob
import copy
import csv
import json
import time
from pylab import *
import seaborn as sns
from matplotlib.markers import MarkerStyle
import json
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
    
    # import map_tlm
    map_tlm = np.genfromtxt(
        r'C:\Users\jmitchell\Documents\GitHub\jm_post_processing\20240227_tlm_map_plotter\20221019_TLMCalInputs\Mrk1_S2000_TLM_TX_ArrayGeometry_V20062022_CalInfo.csv', 
        skip_header=2, dtype=float, delimiter=',')
    
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
    Z = array_in
    
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


# file_path = r'C:\Scratch\20240324\Batch_19\Raw_Data'
file_path = r'C:\Users\jmitchell\Downloads\Batch\Batch\Batch'
f_set_list = ['27.50', '29.00', '31.00']
save_fig = True
it=1
# beam=1
# f_set = f_set_list[1]
find_measFiles(file_path, 'OP_2', 1, '27.50', it=it)
load__measFiles(measFiles[0])
av_dev_log = []
max_dev_log = []
resonance_dict = {}
df_av = pd.DataFrame(columns=['f_meas'])
df_av[f'f_meas'] = meas_frequencies
df_std = pd.DataFrame(columns=['f_meas'])
df_std[f'f_meas'] = meas_frequencies
df_smooth_check = pd.DataFrame(columns=['f_meas'])
df_smooth_check[f'f_meas'] = meas_frequencies
for f_set in f_set_list:
    resonance_dict[f_set] = {}
    for beam in [1,2]:
        res_log = []
        find_measFiles(file_path, 'OP_2', beam, f_set, it=it)
        for port in range(len(meas_array_gain)):
        # for port in [0,1,2,3]:
            plt.figure()
            port_array = np.zeros([len(measFiles), len(meas_frequencies)])
            meas_file_count = 0
            min_max = 0
            for measFile in measFiles:
                load__measFiles(measFile)
                port_array[meas_file_count,:] = meas_array_gain[port, :]
                plt.plot(meas_frequencies, meas_array_gain[port, :], 'k', alpha=0.2)
                if max(meas_array_gain[port, :]) - min(meas_array_gain[port, :]) > min_max:
                    min_max = max(meas_array_gain[port, :]) - min(meas_array_gain[port, :])
                meas_file_count = meas_file_count + 1
            average = np.average(port_array, axis=0)
            average_smoothed = savgol_filter(average, 20, 3)
            av_dev_log.append(max(average) - min(average))
            max_dev_log.append(min_max)
            stdev = np.std(port_array, axis=0)
            plt.plot(meas_frequencies, average, 'b--', linewidth=2)
            # plt.plot(meas_frequencies, average_smoothed, 'm--', linewidth=2)
            smooth_check = average_smoothed-average
            # plt.plot(meas_frequencies, smooth_check, 'g--', linewidth=2)
            
            if max(smooth_check) > 5:
                print(port+1)
                res_loc = np.argmax(smooth_check)
                plt.axvline(x=meas_frequencies[res_loc],color='r')
                res_log.append(port+1)
            plt.fill_between(meas_frequencies, y1=average-stdev, y2=average+stdev, color='b', alpha=0.2)
            plt.axvline(x=float(f_set), color='k', linestyle='--')
            plt.ylim([-20,50])
            plt.xlabel('freq [GHz]')
            plt.ylabel('gain (arb.) [dB]')
            plt.title(f'{f_set} GHz, port {port+1}, beam {beam}')
            plt.grid()
            fname = f'{f_set}GHz_port{port+1}_beam{beam}'
            if save_fig == True:
                plt.savefig(f'C:\Scratch\{fname}.png',dpi=400)
            if max(smooth_check) > 5:
                if save_fig == True:
                    plt.savefig(f'C:\\Scratch\\resonance_detected_{fname}.png',dpi=400)
            df_av[f'{f_set}GHz_b{beam}_p{port+1}_av'] = average
            df_std[f'{f_set}GHz_b{beam}_p{port+1}_std'] = stdev
            df_smooth_check[f'{f_set}GHz_b{beam}_p{port+1}_smooth_check'] = smooth_check
        resonance_dict[f_set][f'beam{beam}'] = res_log
        
df_av.to_excel(f'C:\Scratch\port_v_freq_average.xlsx', index=True)
df_std.to_excel(f'C:\Scratch\port_v_freq_std.xlsx', index=True)
df_smooth_check.to_excel(f'C:\Scratch\port_v_freq_smooth_check.xlsx', index=True)

with open(f'C:\\Scratch\\data.json', 'w') as fp:
    json.dump(resonance_dict, fp)


for f_set in f_set_list:
    plt.figure()
    for beam in [1,2]:
        for_plot = []
        resonance_ports = resonance_dict[f_set][f'beam{beam}']
        for port in range(len(meas_array_gain)):
            if (port+1) in resonance_ports:
                for_plot.append(1)
            else:
                for_plot.append(0)
        plt.plot(np.linspace(1,len(meas_array_gain),num=len(meas_array_gain)), for_plot, 'o-', alpha=0.,label=f'{f_set}GHz, beam{beam}')
    plt.xlabel('port')
    plt.ylabel('resonance')
    plt.legend()
    plt.savefig(f'C:\\Scratch\\overview_{f_set}GHz_resonance_ports.png',dpi=400)
    
fig, axs = plt.subplots(nrows=1, ncols=3, figsize=(40, 9))
fig_count = 0
for f_set in f_set_list:
    plt.figure()
    for beam in [2]:
        for_plot = []
        resonance_ports = resonance_dict[f_set][f'beam{beam}']
        for port in range(len(meas_array_gain)):
            if (port+1) in resonance_ports:
                for_plot.append(1)
            else:
                for_plot.append(0)
        plot_tlm_map(np.array(for_plot), f'{f_set} GHz', 0, 1, 0.5, f_set, fig_count, 1.0, False, align=True,col_map='binary')
        fig_count = fig_count+1
fig.savefig(f'C:\\Scratch\\overview_beam{beam}_null_map.png',dpi=400)

for f_set in f_set_list:
    for beam in [1,2]:

        df_av_filtered = df_av.filter(regex=f'b{beam}')
        df_av_filtered = df_av_filtered.filter(regex=f'{f_set}')
        plt.figure()
        v = np.linspace(0, 40, 41, endpoint=True)
        plt.contourf(np.array(ports), np.array(meas_frequencies), np.array(df_av_filtered), v, cmap='jet')
        plt.xlabel('port')
        plt.ylabel('freq [GHz]')
        plt.xticks([0,152,304,456])
        plt.title(f'Average gain [dB] (iteration {it}) \n {f_set} GHz, beam {beam}')
        plt.colorbar()
        plt.savefig(f'C:\\Scratch\\overview_{f_set}GHz_beam{beam}_average_heatmap.png',dpi=400)
        
        df_smooth_check_filtered = df_smooth_check.filter(regex=f'b{beam}')
        df_smooth_check_filtered = df_smooth_check_filtered.filter(regex=f'{f_set}')
        plt.figure()
        v = np.linspace(0, 5, 3, endpoint=True)
        plt.contourf(np.array(ports), np.array(meas_frequencies), abs(np.array(df_smooth_check_filtered)), v, cmap='binary')
        plt.xlabel('port')
        plt.ylabel('freq [GHz]')
        plt.xticks([0,152,304,456])
        plt.title(f'Null checker (iteration {it}) \n {f_set} GHz, beam {beam}')
        cbar = plt.colorbar()
        cbar.set_ticks([])
        plt.savefig(f'C:\\Scratch\\overview_{f_set}GHz_beam{beam}_null_finder.png',dpi=400)


