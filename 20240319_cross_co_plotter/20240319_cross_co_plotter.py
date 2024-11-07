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


## run

# set-up
# file_path = r'C:\Users\jmitchell\Downloads\BB_Calibrated_Co_+_Cross\BB_Calibrated_Co_+_Cross\2024-03-19_15-25-01_MCR3_Rig1_cal_QR420-0230-00924_29.50_45C\iteration_2'
# file_path = r'C:\Users\jmitchell\Downloads\2024-03-20_10-30-57_MCR3_Rig1_cal_QR420-0230-00886_29.50_45C'
comparison_dict = {}
for file_path in [r'C:\Users\jmitchell\Downloads\2024-03-20_10-30-57_MCR3_Rig1_cal_QR420-0230-00886_29.50_45C\2024-03-20_10-30-57_MCR3_Rig1_cal_QR420-0230-00886_29.50_45C\iteration_2']:
    beam = 1
    f_set = '29.50'
    it = 2
    
    # co pol array
    find_measFiles(file_path, 'OP_2', beam, f_set, it=it)
    load__measFiles(measFiles[0])
    col = np.argmin((meas_frequencies-float(f_set))**2)
    co_gain = meas_array_gain[:,col]
    co_phase = meas_array_phase[:,col]
    
    # cross pol array
    find_measFiles(file_path, 'XP_2', beam, f_set, it=it)
    load__measFiles(measFiles[0])
    cross_gain = meas_array_gain[:,col]
    cross_phase = meas_array_phase[:,col]
    
    # plot
    plt.plot(co_gain)
    plt.plot(cross_gain)
    
    # gain in lin
    co_gain_lin = 10**(co_gain/20.0)
    cross_gain_lin = 10**(cross_gain/20.0)
    
    # complex co and cross
    def magPhase_complex(lin_mag, phase_rad):
        return lin_mag * exp(1j*phase_rad)
    co_complex = magPhase_complex(co_gain_lin, co_phase*np.pi/180.0)
    cross_complex = magPhase_complex(cross_gain_lin, cross_phase*np.pi/180.0)
    
    # output array
    df = pd.DataFrame(columns=['ports', 'pol', 'lens_no', 'co_gain_dB', 'co_phase_deg', 'cross_gain_dB', 'cross_phase_deg', 'co_complex_re', 'co_complex_im', 'cross_complex_re', 'cross_complex_im'])
    ports = list(np.linspace(1,len(co_complex)+1,num=len(co_complex)+1)[0:-1].astype(int))#.reshape(len(co_gain),1)
    df['ports'] = ports
    df['co_gain_dB'] = co_gain
    df['co_phase_deg'] = co_phase
    df['cross_gain_dB'] = cross_gain
    df['cross_phase_deg'] = cross_phase
    df['co_complex_re'] = np.real(co_complex)
    df['co_complex_im'] = np.imag(co_complex)
    df['cross_complex_re'] = np.real(cross_complex)
    df['cross_complex_im'] = np.imag(cross_complex)
    f_set_fname = f_set.replace('.', 'g')
    map_tlm_df = pd.read_csv(r'C:\Users\jmitchell\Documents\GitHub\jm_post_processing\20240227_tlm_map_plotter\20221019_TLMCalInputs\Mrk1_S2000_TLM_TX_ArrayGeometry_V20062022_CalInfo.csv', header=1)
    lens_list = (list(map_tlm_df['Lens no.'])+list(map_tlm_df['Lens no.']))
    lens_list.sort()
    df['lens_no'] = lens_list
    pol = []
    for i in range(len(map_tlm_df)):
        pol.append('Odd')
        pol.append('Even')
    df['pol'] = pol
    
    
    
    
    pkpk_log_odd = []
    pkpk_log_even = []
    gain_delta_log_odd = []
    gain_delta_log_even = []
    co_cross_pol_shift_log_odd = []
    co_cross_pol_shift_log_even = []
    odd_even_co_delta_log = []
    for port in list(np.linspace(0,len(co_complex),num=len(co_complex)+1)[::2][0:-1].astype(int)):
        plt.figure()
        for port_add in [0,1]:
            Eco_gain = []
            Eco_phase = []
            Ex_gain = []
            Ex_phase = []
            phase_range = 360
            pol_array = np.linspace(1,phase_range,num=phase_range)
            for count in range(phase_range):
            
                phi_deg=0.0
                phi_pol = count
                comb_ang_rad = (phi_deg + phi_pol)*np.pi/180.0
                
                # calculation
                Eco_C = np.cos(comb_ang_rad)*co_complex[port+port_add] - np.sin(comb_ang_rad)*cross_complex[port+port_add]
                Ex_C = np.sin(comb_ang_rad)*co_complex[port+port_add] + np.cos(comb_ang_rad)*cross_complex[port+port_add]
              
                # back to gain and phase
                Eco_gain.append(20*np.log10(abs(Eco_C)))
                Eco_phase.append((180.0/np.pi)*(angle(Eco_C)))
                Ex_gain.append(20*np.log10(abs(Ex_C)))
                Ex_phase.append((180.0/np.pi)*(angle(Ex_C)))
                
            if port_add == 0:
                pol = 'Odd'
                linestyle = '-'
                pkpk_odd = max(Eco_gain)-min(Eco_gain)
                max_val_odd = max(Eco_gain)
                pkpk_log_odd.append(pkpk_odd)
                gain_delta_log_odd.append(max(Eco_gain)-Eco_gain[0])
                co_cross_pol_shift_log_odd.append(pol_array[np.argmin(Eco_gain[0:int(phase_range/1)])]-pol_array[np.argmin(Ex_gain[0:int(phase_range/1)])])
                co_null_odd = pol_array[np.argmin(Eco_gain[0:int(phase_range/1)])]
            if port_add == 1:
                pol = 'Even'
                linestyle = '--'
                pkpk_even = max(Eco_gain)-min(Eco_gain)
                max_val_even = max(Eco_gain)
                pkpk_log_even.append(pkpk_even)
                gain_delta_log_even.append(max(Eco_gain)-Eco_gain[0])
                co_cross_pol_shift_log_even.append(pol_array[np.argmin(Eco_gain[0:int(phase_range/1)])]-pol_array[np.argmin(Ex_gain[0:int(phase_range/1)])])
                co_null_even = pol_array[np.argmin(Eco_gain[0:int(phase_range/1)])]
                
            # plots
            plt.plot(pol_array, Eco_gain, 'k'+linestyle, label=f'{pol} Co')          
            plt.plot(pol_array, Ex_gain, 'r'+linestyle, label=f'{pol} X')
        
        # difference between odd and even
        odd_even_co_delta_log.append(co_null_odd-co_null_even)
        
        plt.ylim([-20,10])
        plt.xlim([0,360]); plt.xticks([0,45,90,135,180,225,270,315,360])
        plt.xlabel('polarisation [deg]')
        plt.ylabel('gain [dB]')
        plt.title(f'Ports {port+1}, {port+1+1} \n ODD: max={round(max_val_odd,2)}, pkpk={round(pkpk_odd,2)} \n EVEN: max={round(max_val_even,2)}, pkpk={round(pkpk_even,2)}')
        plt.legend(loc='upper right')
        plt.grid()
        plt.tight_layout()
        plt.savefig(f'C:\Scratch\Ports {port+1}, {port+1+1}.png',dpi=400)
    
    # arrays
    port_list = list(np.linspace(1,len(co_complex)+1,num=len(co_complex)+1)[0:-1].astype(int))
    odd_ports = port_list[::2]
    even_ports = port_list[1::2]
    
    # overview figure pkpk
    plt.figure()
    plt.plot(odd_ports, pkpk_log_odd, label=f'odd')
    plt.plot(even_ports, pkpk_log_even, label=f'even')
    pkpk_log_both = list(co_gain*0.0)
    pkpk_log_both[::2] = pkpk_log_odd
    pkpk_log_both[1::2] = pkpk_log_even
    df['pkpk'] = pkpk_log_both
    plt.xlabel('port')
    plt.ylabel('pkpk [dB]')
    plt.legend()
    plt.savefig(f'C:\Scratch\overview figure pkpk.png',dpi=400)
    
    # overview figure gain delta
    plt.figure()
    plt.plot(odd_ports, gain_delta_log_odd, label=f'odd')
    plt.plot(even_ports, gain_delta_log_even, label=f'even')
    gain_delta_log_both = list(co_gain*0.0)
    gain_delta_log_both[::2] = gain_delta_log_odd
    gain_delta_log_both[1::2] = gain_delta_log_even
    df['gain_delta'] = gain_delta_log_both
    plt.xlabel('port')
    plt.ylabel('gain shift [dB]')
    plt.legend()
    plt.savefig(f'C:\Scratch\overview figure gain delta.png',dpi=400)
    
    # overview figure co-cross shift
    # plt.figure()
    # plt.plot(odd_ports, co_cross_pol_shift_log_odd, label=f'odd')
    # plt.plot(even_ports, co_cross_pol_shift_log_even, label=f'even')
    # plt.xlabel('port')
    # plt.ylabel('co cross pol delta [deg]')
    # plt.legend()
    
    # overview figure odd_even_diff
    for i in range(len(odd_even_co_delta_log)):
        if odd_even_co_delta_log[i] > 120.0:
            odd_even_co_delta_log[i] = odd_even_co_delta_log[i]-180.0
        if odd_even_co_delta_log[i] < -120.0:
            odd_even_co_delta_log[i] = odd_even_co_delta_log[i]+180.0
    
    plt.figure()
    plt.plot(odd_ports, odd_even_co_delta_log)
    odd_even_co_delta_log_both = list(co_gain*0.0)
    odd_even_co_delta_log_both[::2] = odd_even_co_delta_log
    df['odd_even_co_delta'] = odd_even_co_delta_log_both
    plt.xlabel('odd port')
    plt.ylabel('odd even co diff [deg]')
    plt.legend()
    plt.savefig(f'C:\Scratch\overview figure odd even diff.png',dpi=400)
    

    barcode=meas_params['barcodes']
    comparison_dict[f'{barcode}'] = {}
    comparison_dict[f'{barcode}']['pkpk_log_odd'] = pkpk_log_odd
    comparison_dict[f'{barcode}']['pkpk_log_even'] = pkpk_log_even
    comparison_dict[f'{barcode}']['gain_delta_log_odd'] = gain_delta_log_odd
    comparison_dict[f'{barcode}']['gain_delta_log_even'] = gain_delta_log_even
    comparison_dict[f'{barcode}']['odd_even_co_delta_log'] = odd_even_co_delta_log
    
    df.to_excel(f'C:\Scratch\co_cross_{f_set_fname}_beam{beam}_tlm{barcode}.xlsx', index=True)
    
    fig, axs = plt.subplots(nrows=1, ncols=3, figsize=(40, 9))
    plot_tlm_map(np.array(pkpk_log_both), f'{f_set} GHz: pkpk', 0, 50, 0.01, f'{f_set}', 0, 5, False, align=False, col_map = 'jet')
    plot_tlm_map(np.array(gain_delta_log_both), f'{f_set} GHz: gain_delta', 0, 2, 0.01, f'{f_set}', 1, 0.5, False, align=False, col_map = 'jet')
    plot_tlm_map(np.array(odd_even_co_delta_log_both), f'{f_set} GHz: odd_even_co_delta', -20, 20, 0.01, f'{f_set}', 2, 5, True, align=False, col_map = 'jet')
    plt.savefig(f'C:\Scratch\FOMs.png')
    
boards = list(comparison_dict.keys())
logs = list(comparison_dict[boards[0]].keys())
for log in logs:
    plt.figure()
    for board in boards:
        array = comparison_dict[board][log]
        plt.plot(array, label=board)
        plt.title(log)
    plt.legend()
    plt.savefig(f'C:\Scratch\comparison_{log}.png')
    



