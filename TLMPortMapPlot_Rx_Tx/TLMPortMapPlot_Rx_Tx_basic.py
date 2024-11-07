# -*- coding: utf-8 -*-
"""
Created on Mon Dec 18 16:40:42 2023

@author: jmitchell
"""
# imports
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

TLM_Type = 'Rx' #'Rx'
Add_stdev = 'OFF'

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


def plot_tlm_map(array_in, title, cmin, cmax, cstp, f_set, plot_no, tick_step,delta_pol, align=False, col_map='jet'):
    global Z, Y, temp, Z_trim,Z_trim_h, rfic_list, map_tlm_df, rfic_feed_mapping

    # map tlm as a df (and roated if needed)
    if TLM_Type == 'Rx':
        map_tlm_df = pd.read_csv(r'C:\Users\RyanFairclough\PycharmProjects\Post-Processing\20231218_TLMPortMapPlot\20240227_tlm_map_plotter\20221019_TLMCalInputs\Mrk1_S2000_TLM_RX_ArrayGeometry_V20062022_CalInfo_Orig.csv',header=1)
    elif TLM_Type == 'Tx':
        map_tlm_df = pd.read_csv(r'C:\Users\RyanFairclough\PycharmProjects\Post-Processing\20231218_TLMPortMapPlot\20240227_tlm_map_plotter\20221019_TLMCalInputs\Mrk1_S2000_TLM_TX_ArrayGeometry_V20062022_CalInfo.csv',header=1)

    if align == True:
        map_tlm_df[' Feed x [mm] shift'] = map_tlm_df[' Feed x [mm]'] - map_tlm_df[' Lens x [mm]']
        map_tlm_df[' Feed y [mm] shift'] = map_tlm_df[' Feed y [mm]'] - map_tlm_df[' Lens y [mm]']
        map_tlm_df[' Dual-Pol Probe rotation [deg]']
        angle = np.array(map_tlm_df[' Feed x [mm] shift']) * 0.0
        if TLM_Type == 'Rx':
            for i in range(len(map_tlm_df[' Feed x [mm] shift'])):
                if map_tlm_df['Lens no.'][i] == 1:
                    angle[i] = 0.0
                    if map_tlm_df['Lens no.'][i] == 2:
                        angle[i] = -77.25
                        if map_tlm_df['Lens no.'][i] == 3:
                            angle[i] = -154.5
        if TLM_Type == 'Tx':
            for i in range(len(map_tlm_df[' Feed x [mm] shift'])):
                if map_tlm_df['Lens no.'][i] == 1:
                    angle[i] = 0.0
                    if map_tlm_df['Lens no.'][i] == 2:
                        angle[i] = -102.5
                        if map_tlm_df['Lens no.'][i] == 3:
                            angle[i] = -205
        map_tlm_df['angle'] = angle
        map_tlm_df['x_rot'] = map_tlm_df[' Feed x [mm] shift'] * cos(map_tlm_df['angle'] * np.pi / 180.0) - map_tlm_df[
            ' Feed y [mm] shift'] * sin(map_tlm_df['angle'] * np.pi / 180.0)
        map_tlm_df['y_rot'] = map_tlm_df[' Feed y [mm] shift'] * cos(map_tlm_df['angle'] * np.pi / 180.0) + map_tlm_df[
            ' Feed x [mm] shift'] * sin(map_tlm_df['angle'] * np.pi / 180.0)
        map_tlm_df['x_new'] = map_tlm_df['x_rot'] + map_tlm_df[' Lens x [mm]']
        map_tlm_df['y_new'] = map_tlm_df['y_rot'] + map_tlm_df[' Lens y [mm]']
        #print(map_tlm_df)

    # plot rfics
    if TLM_Type == 'Rx':
        map_rfic = pd.read_csv(r'C:\Users\RyanFairclough\PycharmProjects\Post-Processing\20231218_TLMPortMapPlot\20240227_tlm_map_plotter\20221019_TLMCalInputs\MK1_RX_TLM_RFIC_Patch_Feed_mapping_RF.csv')
    elif TLM_Type == 'Tx':
        map_rfic = pd.read_csv(r'C:\Users\RyanFairclough\PycharmProjects\Post-Processing\20231218_TLMPortMapPlot\20240227_tlm_map_plotter\20221019_TLMCalInputs\MK1_TX_TLM_RFIC_Patch_Feed_Mapping.csv')
    rfics = list(set(list(map_rfic['RFIC Number'])))
    #(rfics)
    for rfic in rfics:
        map_rfic_cut = map_rfic[map_rfic['RFIC Number'] == rfic]
        print(map_rfic_cut.columns)
        patches = map_rfic_cut['Patch_Number ']

        for lens in [0, 1, 2]:
            x_rfic = [];
            y_rfic = []
            for patch in patches:
                if align == True:
                    x_rfic.append(map_tlm_df['x_new'][patch - 1 + lens * float(len(map_tlm_df)) / 3])
                    y_rfic.append(map_tlm_df['y_new'][patch - 1 + lens * float(len(map_tlm_df)) / 3])
                    axs[plot_no].text(map_tlm_df['x_new'][patch - 1 + lens * float(len(map_tlm_df)) / 3],
                                      map_tlm_df['y_new'][patch - 1 + lens * float(len(map_tlm_df)) / 3],
                                      patch, fontsize=3)
                else:
                    x_rfic.append(map_tlm_df[' Feed x [mm]'][patch - 1 + lens * float(len(map_tlm_df)) / 3])
                    y_rfic.append(map_tlm_df[' Feed y [mm]'][patch - 1 + lens * float(len(map_tlm_df)) / 3])
                    axs[plot_no].text(map_tlm_df[' Feed x [mm]'][patch - 1 + lens * float(len(map_tlm_df)) / 3],
                                      map_tlm_df[' Feed y [mm]'][patch - 1 + lens * float(len(map_tlm_df)) / 3],
                                      patch, fontsize=3)
            axs[plot_no].plot(x_rfic, y_rfic, 'm-', linewidth=1.0, alpha=0.7)


    # select the column of data
    col = np.argmin((meas_frequencies - f_set) ** 2)
    Z = array_in[:, col]
    stat_TLM_Median = np.median(Z)
    #print(stat_TLM_Median)
    #np.median(Z)
    # odd ports
    Z_trim_h = Z[::2]
    print(Z_trim_h)
    Z_trim_pol1 = Z_trim_h.copy()

    rfic = map_rfic['RFIC Number']
    h_feed = map_rfic['H-Feed (Odd)']
    v_feed = map_rfic['V-Feed (Even)']

    v_feed_list = v_feed.values.tolist()
    h_feed_list = h_feed.values.tolist()
    rfic_list = rfic.values.tolist() * 3
    # print(h_feed_list)
    # print(v_feed_list)
    # print(rfic_list)

    # marker for odd ports
    m = MarkerStyle('D', fillstyle='left')
    m._transform.rotate_deg(map_tlm_df[' Dual-Pol Probe rotation [deg]'][i] + 45)

    # scatter plot for odd pol
    v = np.linspace(cmin, cmax, int((cmax - cmin) / cstp), endpoint=True)
    cmap_chosen = cm.get_cmap(col_map, int((cmax - cmin) / cstp))
    #print(Z_trim)
    cntr = axs[plot_no].scatter(map_tlm_df[' Feed x [mm]'],map_tlm_df[' Feed y [mm]'], c=Z_trim_h, marker=m, s=200, edgecolors='black', linewidths=0.5, cmap=cmap_chosen,vmin=min(v), vmax=max(v), alpha=1.0)

    # even pol
    Z_trim = Z[1::2]
    Z_trim_pol2 = Z_trim.copy()

    # marker for even ports
    m = MarkerStyle('D', fillstyle='right')
    m._transform.rotate_deg(map_tlm_df[' Dual-Pol Probe rotation [deg]'][i] + 45)


    v_feed_dict = dict(zip(Z_trim, v_feed_list))
    h_feed_dict = dict(zip(Z_trim_h, h_feed_list))

    print("Z_trim_h to H-Feed Mapping:", h_feed_dict)
    print("Z_trim_v to V-Feed Mapping:", v_feed_dict)

    rfic_feed_mapping = [
        {
            'RFIC Number': rfic_list[i],
            'Z_trim_h': Z_trim_h[i] if i < len(Z_trim_h) else None,
            'H-Feed': h_feed_dict.get(Z_trim_h[i], None) if i < len(Z_trim_h) else None,
            'Z_trim_v': Z_trim[i] if i < len(Z_trim) else None,
            'V-Feed': v_feed_dict.get(Z_trim[i], None) if i < len(Z_trim) else None
        }
        for i in range(len(rfic_list))
    ]

    print("RFIC to Z_trim and Feed Mapping:")
    for mapping in rfic_feed_mapping:
        print(mapping)

    # scatter plot for even pol
    cntr = axs[plot_no].scatter(map_tlm_df[' Feed x [mm]'],map_tlm_df[' Feed y [mm]'] , c=Z_trim, marker=m, s=200, edgecolors='black', linewidths=0.5, cmap=cmap_chosen,vmin=min(v), vmax=max(v), alpha=1.0)

    # scatter plot (on-top) for delta pol
    if delta_pol == True:
        m = MarkerStyle('s')
        m._transform.rotate_deg(map_tlm_df[' Dual-Pol Probe rotation [deg]'][i])
        cntr = axs[plot_no].scatter(map_tlm_df[' Feed x [mm]'],map_tlm_df[' Feed y [mm]'] , c=(Z_trim_pol1 - Z_trim_pol2), marker=m, s=200, edgecolors='black',linewidths=0.5, vmin=min(v), vmax=max(v), cmap=cmap_chosen, alpha=1.0)

    cbar = plt.colorbar(cntr)
    cbar.set_ticks(np.arange(min(v), max(v) + tick_step, tick_step))
    axs[plot_no].set_xlabel('X [mm]');
    axs[plot_no].set_ylabel('Y [mm]')
    axs[plot_no].set_title(title)


# set-up
file_path = r'C:\Users\RyanFairclough\Downloads\compare_after_cable_cal'
if TLM_Type == 'Rx':
    map_tlm_df = pd.read_csv(r'C:\Users\RyanFairclough\PycharmProjects\Post-Processing\20231218_TLMPortMapPlot\20240227_tlm_map_plotter\20221019_TLMCalInputs\Mrk1_S2000_TLM_RX_ArrayGeometry_V20062022_CalInfo_Orig.csv',header=1)
    freq_list = ['19.20']
elif TLM_Type == 'Tx':
    map_tlm_df = pd.read_csv(r'C:\Users\RyanFairclough\PycharmProjects\Post-Processing\20231218_TLMPortMapPlot\20240227_tlm_map_plotter\20221019_TLMCalInputs\Mrk1_S2000_TLM_TX_ArrayGeometry_V20062022_CalInfo.csv',header=1)
    freq_list = ['27.50', '28.00', '28.50', '29.00', '29.50', '30.00', '30.50', '31.00']
align = True
beam_list = [1]
it = 1

# run
for gain_phase in ['gain', 'phase']:

    for delta_pol in [False, True]:

        if delta_pol == True:
            if gain_phase == 'gain':
                vmax_std = 6.0
                v_OP = 8.0
                v_RFA = v_OP * 1.0
                v_OP_step = 0.01
                v_RFA_step = v_OP_step * 1.0
                v_spread_step = 0.01
                tick_step = 1
            if gain_phase == 'phase':
                vmax_std = 90
                v_OP = 360
                v_RFA = v_OP * 1.0  # 3.0
                v_OP_step = 0.01
                v_RFA_step = v_OP_step * 1.0
                v_spread_step = 0.01
                tick_step = 45.0

        if delta_pol == False:
            if gain_phase == 'gain':
                vmax_std = 6.0
                v_OP = 20.0
                v_RFA = v_OP * 1.0
                v_OP_step = 0.01
                v_RFA_step = v_OP_step * 1.0
                v_spread_step = 0.01
                tick_step = 2
            if gain_phase == 'phase':
                vmax_std = 90
                v_OP = 360
                v_RFA = v_OP * 1.0  # 3.0
                v_OP_step = 0.01
                v_RFA_step = v_OP_step * 1.0
                v_spread_step = 0.01
                tick_step = 45.0

        for f_type in ['OP_2', 'RFA']:

            # initialise out_array
            count = 0
            out_array = np.zeros([len(map_tlm_df) * 2, len(freq_list) * 2 * len(beam_list)])


            for beam in beam_list:

                for freq_set in freq_list:
                    # find measurement files and load one of them to make an empty matrix
                    find_measFiles(file_path, f_type, beam, freq_set, it)
                    print(f_type)
                    load__measFiles(measFiles[0])
                    meas_array_tot = meas_array_gain * 0.0
                    meas_array_list = []

                    # cycle through meas files to make average and stdev arrays
                    for measFile in measFiles:
                        load__measFiles(measFile)
                        if gain_phase == 'gain':
                            meas_array_list.append(meas_array_gain)
                        if gain_phase == 'phase':
                            meas_array_list.append(meas_array_phase)
                    meas_array_av = np.median(meas_array_list, axis=0)
                    if Add_stdev == 'ON':
                        meas_array_std = np.std(meas_array_list, axis=0)
                    else:
                        print('STDEV OFF')
                    # initialise figure
                    fig, axs = plt.subplots(nrows=1, ncols=3, figsize=(40, 9))

                    # make plots for OP or RFA
                    if 'OP' in f_type:
                        plot_tlm_map(meas_array_av,
                                     f'({f_type}) {gain_phase} (average), N = {len(measFiles)} \n Freq = {freq_set} GHz, Beam {beam}, Delta Pol={delta_pol}, Lens Align={align}',
                                     0, v_OP, v_OP_step, float(meas_params['f_c']), 0, tick_step=tick_step,
                                     delta_pol=delta_pol, align=align)
                    elif 'RFA' in f_type:
                        plot_tlm_map(meas_array_av,
                                     f'({f_type}) {gain_phase} (average), N = {len(measFiles)} \n Freq = {freq_set} GHz, Beam {beam}, Delta Pol={delta_pol}, Lens Align={align}',
                                     -v_RFA, v_RFA, v_RFA_step, float(meas_params['f_c']), 0, tick_step=tick_step,
                                     delta_pol=delta_pol, align=align)

                    # add to out_array
                    out_array[:, count] = Z

                    # replace the decimal point in the frequency for filenames
                    freq_str = freq_set.replace('.', 'g')

                    # plot the stdev
                    if Add_stdev == 'ON':
                        plot_tlm_map(meas_array_std,f'({f_type}) {gain_phase} (stdev), N = {len(measFiles)} \n Freq = {freq_set} GHz, Beam {beam}, Delta Pol={delta_pol}, Lens Align={align}',
                                 0.0, vmax_std, v_spread_step, float(meas_params['f_c']), 1, tick_step=tick_step,
                                 delta_pol=delta_pol, align=align)
                    else:
                        print("STDEV OFF")

                   # if TLM_Type == 'Rx':
                       # map_rfic = pd.read_csv(
                          #  r'C:\Users\RyanFairclough\PycharmProjects\Post-Processing\20231218_TLMPortMapPlot\20240227_tlm_map_plotter\20221019_TLMCalInputs\MK1_RX_TLM_RFIC_Patch_Feed_mapping_RF.csv')
                    #elif TLM_Type == 'Tx':
                       # map_rfic = pd.read_csv(
                           # r'C:\Users\RyanFairclough\PycharmProjects\Post-Processing\20231218_TLMPortMapPlot\20240227_tlm_map_plotter\20221019_TLMCalInputs\MK1_TX_TLM_RFIC_Patch_Feed_Mapping.csv')

                    # plot the cartesian
                    # for measFile in measFiles:

                    rfics = [item['RFIC Number'] for item in rfic_feed_mapping]
                    Z_trim_h = [item['Z_trim_h'] for item in rfic_feed_mapping]
                    Z_trim_v = [item['Z_trim_v'] for item in rfic_feed_mapping]
                    print('@@@@@@',Z_trim_h)
                    print(len(Z_trim_h))


                    load__measFiles(measFile)
                    col = np.argmin((meas_frequencies - float(freq_set)) ** 2)

                    stat_median = np.median(meas_array_av)
                    colors = ['red', 'green', 'blue']


                    Z_trim_h_colored = []
                    Z_trim_v_colored = []

                    for i in range(len(Z_trim_h)):
                        color_index = (i // 76) % 3  # This will cycle through 0, 1, 2
                        Z_trim_h_colored.append((Z_trim_h[i], colors[color_index]))
                        Z_trim_v_colored.append((Z_trim_v[i], colors[color_index]))


                    for i in range(len(rfics)):
                        axs[2].scatter(rfics[i], Z_trim_h_colored[i][0], color=Z_trim_h_colored[i][1],label='Z_trim_h (H-Feed)' if i == 0 else "", linestyle='solid')
                        axs[1].scatter(rfics[i], Z_trim_v_colored[i][0], color=Z_trim_v_colored[i][1],label='Z_trim_v (V-Feed)' if i == 0 else "", linestyle='solid')

                    from matplotlib.lines import Line2D

                    legend_elements = [Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=10,
                                              label='Lens 1 (H-Feed)'),
                                       Line2D([0], [0], marker='o', color='w', markerfacecolor='green', markersize=10,
                                              label='Lens 2 (H-Feed)'),
                                       Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markersize=10,
                                              label='Lens 3 (H-Feed)')]

                    legend_elements1 = [Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=10,
                               label='Lens 1 (V-Feed)'),
                                        Line2D([0], [0], marker='o', color='w', markerfacecolor='green', markersize=10,
                                               label='Lens 2 (V-Feed)'),
                                        Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markersize=10,
                                            label='Lens 3 (V-Feed)')]

                    axs[1].legend(handles=legend_elements1, loc='lower left')
                    axs[2].legend(handles=legend_elements, loc='lower left')

                    axs[2].plot(rfic_list, Z_trim_h)
                    axs[1].set_xlabel('RFIC')
                    axs[1].set_ylabel(f'{gain_phase}')
                    axs[1].set_xlim([0, 20])
                    axs[1].set_xticks(np.linspace(0, 20, num=int(20 / 1) + 1))
                    axs[1].set_title(f'({f_type}) {gain_phase} (average) - V-Feed Plot, N = {len(measFiles)} \n Freq = {freq_set} GHz, Beam {beam}, Lens Align={align}')
                    axs[1].grid('on')
                    axs[1].legend(handles=legend_elements1, loc='lower left')


                    axs[2].set_xlabel('RFIC')
                    axs[2].set_ylabel(f'{gain_phase}')
                    axs[2].set_xlim([0, 20])
                    axs[2].set_xticks(np.linspace(0, 20, num=int(20 / 1) + 1))
                    axs[2].set_title(f'({f_type}) {gain_phase} (average) - H-Feed Plot, N = {len(measFiles)} \n Freq = {freq_set} GHz, Beam {beam}, Lens Align={align}')
                    axs[2].grid('on')
                    axs[2].legend(handles=legend_elements, loc='lower left')
                    # add the stdev to the outarray
                    out_array[:, count + 1] = Z

                    # add to count
                    count = count + 2

                    # chck the directory
                    isExist = os.path.exists(f'{file_path}\\analysis_rfic')
                    if not isExist:
                        os.makedirs(f'{file_path}\\analysis_rfic')

                    # save the figure
                    plt.savefig(
                        f'{file_path}\\analysis_rfic\\{f_type}_{freq_str}_beam{beam}_delta{delta_pol}_{gain_phase}.png',
                        dpi=200)

            # make the output excel
            freq_list_av = [s + '_av' for s in freq_list]
            freq_list_std = [s + '_std' for s in freq_list]
            header_list = []
            for beam in beam_list:
                for i in range(len(freq_list)):
                    header_list.append(freq_list_av[i] + f'_beam{beam}');
                    header_list.append(freq_list_std[i] + f'_beam{beam}')
            df = pd.DataFrame(out_array, columns=header_list)
            lens_list = (list(map_tlm_df['Lens no.']) + list(map_tlm_df['Lens no.']))
            lens_list.sort()
            df['Lens no.'] = lens_list
            col = df.pop("Lens no.")
            df.insert(0, col.name, col)
            pol = []
            for i in range(len(map_tlm_df)):
                pol.append('Odd')
                pol.append('Even')
            df['pol'] = pol.copy()
            col = df.pop("pol")
            df.insert(0, col.name, col)
            df.index += 1
            df.to_excel(f'{file_path}\\analysis\\{f_type} {gain_phase}, N = {len(measFiles)}.xlsx', index=True)