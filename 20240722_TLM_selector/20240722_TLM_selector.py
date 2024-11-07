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
import shutil

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
    for lens in [0, 1, 2]:
        ports = np.linspace(1, len(gain), num=len(gain))
        for rfic in rfics:
            df_rfic = map_rfic[map_rfic['RFIC Number'] == rfic]
            ports_rfic = np.array(df_rfic['Patch Number'])
            ports_rfic = list(np.concatenate((ports_rfic, ports_rfic + 1), axis=0))
            ports_rfic.sort()
            port_gain_log = []
            for port_rfic in ports_rfic:
                port_number = (port_rfic - 1) + (lens * (len(gain_col) / 3))
                port_gain_log.append(gain_col[int(port_number)])
            rfic_offset_log.append(np.median(port_gain_log))
            rfic_std_log.append(np.std(port_gain_log))
            rfic_minmax_log.append(np.max(port_gain_log) - np.min(port_gain_log))

    return np.array(rfic_offset_log), np.array(rfic_std_log), np.array(rfic_minmax_log), rfics


def pass_rate(df):
    boards = list(set(df['board']))
    board_pass = []
    for board in boards:
        df_board = df[df['board'] == board]
        if False in list(df_board['pass']):
            board_pass.append(False)
        else:
            board_pass.append(True)

    pass_rate = 100.0 * float(board_pass.count(True)) / (float(len(board_pass)));
    print(round(pass_rate, 2))

    return boards, board_pass, pass_rate


## code

# files
# file_path = r'C:\scratch\20240903\TLM Results\P3\P3_TLMs_New_TX\P3_TLMs_New\Raw_Data\p3_bb'
# file_path = r'C:\scratch\20240903\TLM Results\P4\P4_TLMs TX updated\P4_TLMs TX\P4_TLMs\BB\Raw_Data'
# file_path = r'C:\scratch\20240903\TLM Results\P5\P5_TLMs tx\P5_TLMs\BB'
# file_path = r'C:\scratch\20240903\TLM Results\P6\P6_TX_TLMs\P6_TLMs'
file_path = r'C:\Users\RyanFairclough\Downloads\P18_TLMs'
#file_path = r'C:\Users\jmitchell\Downloads\Pass TX TLMS 11-09-24\Pass TX TLMS 11-09-24\All TLMS'
#file_path = r'C:\scratch\20240903\TLM Results\All_TLMs\Pass and Fail'
map_tlm_df = pd.read_csv(
    r'C:\Users\RyanFairclough\Downloads\TLM_Selector\Mrk1_S2000_TLM_TX_ArrayGeometry_V20062022_CalInfo.csv',
    header=1)
map_rfic = pd.read_csv(
    r'C:\Users\RyanFairclough\Downloads\TLM_Selector\MK1_TX_TLM_RFIC_Patch_Feed_Mapping.csv')
df_tlmic = pd.read_excel(r'C:\Users\RyanFairclough\Downloads\TLM_Selector\es2i_wafer_map_master_GF.xlsx',
                         sheet_name='es2i_wafer_map_master_GF', header=1)

# params
freq_set = '29.50'

delta_board = False
freq_list = ['27.50', '28.00', '28.50', '29.00', '29.50', '30.00', '30.50', '31.00']
#freq_list = ['29.50']
# freq_list = ['17.70', '18.20', '18.70', '19.20', '19.70', '20.20', '20.70', '21.20']

# run

df = pd.DataFrame()

# List to keep track of unique 16-character Date_Time entries
date_time_changes = []

for beam in [1,2]:
    for freq_set in freq_list:
        find_measFiles(file_path, 'OP_2', beam, freq_set)
        for meas_file in measFiles:
            load__measFiles(meas_file)
            col = np.argmin((meas_frequencies - float(freq_set)) ** 2)
            gain = meas_array_gain[:, col]
            gain_median = np.median(gain)
            gain_spread = np.std(gain)
            gain_minmax = np.max(gain) - np.min(gain)
            lens_medians = []

            for lens in [1, 2, 3]:
                lens_medians.append(float(np.median(gain[int((lens - 1) * len(gain) / 3):int(lens * len(gain) / 3)])))

            lens_delta_max = max(lens_medians) - min(lens_medians)
            rfic_offset_log, rfic_std_log, rfic_minmax_log, rficsrfica = gain_to_rfic_metrics(gain)
            rfic_offset_max = rfic_offset_log[np.argmax(abs(rfic_offset_log))]
            #if len(rfic_std_log) ==
            #print(rfic_std_log)
            rfic_spread_max = rfic_std_log[np.argmax(abs(rfic_std_log))]
            rfic_minmax_max = rfic_minmax_log[np.argmax(abs(rfic_minmax_log))]
            rfic_minmax_idx = np.argmax(abs(rfic_minmax_log)) + 1

            board = meas_params['barcodes']
            Date_Time = meas_params['date time']


            #try:
                #Date_Time_str = pd.to_datetime(Date_Time).strftime("%Y-%m-%d %H:%M")
            #except Exception as e:
                #print(f"Error parsing Date_Time: {e}")
                #continue


            #print("Formatted Date_Time:", Date_Time_str)


            #if Date_Time_str not in date_time_changes:
                #date_time_changes.append(Date_Time_str)
                #print(f"Added new Date_Time entry to list: {Date_Time_str}")

            uid = meas_params['ER Id']
            wafer_id_chunk = uid[0:5]
            wafer_id_binary = bin(int(wafer_id_chunk, 16))
            wafer_id_num = int(wafer_id_binary[2:], 2)
            df_tlmic_specific = df_tlmic[df_tlmic['uid[31:12]'] == wafer_id_num]
            wafer_id = df_tlmic_specific['wafer_id']
            lot = list(df_tlmic_specific['ES2i Lot ID'])[0]
            dropped_flag = False
            min_port = min(gain)
            if min_port < (gain_median - gain_spread * 5):
                dropped_flag = True

            new_entry = {
                'board': board, 'gain_median [dB]': gain_median, 'gain_spread [dB]': gain_spread,
                'min_port [dB]': min_port, 'dropped_port': dropped_flag,
                'frequency [GHz]': float(freq_set), 'beam': beam,
                'gain_minmax [dB]': gain_minmax, 'lens1_median [dB]': lens_medians[0],
                'lens2_median [dB]': lens_medians[1], 'lens3_median [dB]': lens_medians[2],
                'lens_delta_max': lens_delta_max,
                'rfic_offset_max [dB]': rfic_offset_max, 'rfic_spread_max [dB]': rfic_spread_max,
                'rfic_minmax_max [dB]': rfic_minmax_max,
                'lens_delta_max [dB]': lens_delta_max, 'uid': uid, 'wafer_id_num': wafer_id_num,
                'lot': lot, 'rfic_minmax_maxidx': rfic_minmax_idx,
                'Date_Time': Date_Time
            }


            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)

# Final print of the unique date_time_changes list
print("Unique Date_Time entries (formatted to 16 chars):", date_time_changes)
#0.5 shift
# limits = {} # increase median
# limits['median_gain'] = {}
# limits['median_gain']['27.50'] = [1.37, 2.53]
# limits['median_gain']['28.00'] = [5.82, 1.94]
# limits['median_gain']['28.50'] = [6.06, 2.07]
# limits['median_gain']['29.00'] = [5.13, 2.32]
# limits['median_gain']['29.50'] = [6.11, 2.1]
# limits['median_gain']['30.00'] = [6.46, 2.13]
# limits['median_gain']['30.50'] = [6.58, 2.4]
# limits['median_gain']['31.00'] = [5.51, 2]
# limits['tlm_spread'] = 4
# limits['lens_delta'] = 5.50
# limits['rfic_offset'] = 8.50
# limits['rfic_spread'] = 10.50
# limits['rfic_minmax'] = 24.50
# spread_factor = 2.5
# limits = {}
# limits['median_gain'] = {}
# limits['median_gain']['27.50'] = [1.37, 2.03]
# limits['median_gain']['28.00'] = [5.82, 1.44]
# limits['median_gain']['28.50'] = [6.06, 1.57]
# limits['median_gain']['29.00'] = [5.13, 1.82]
# limits['median_gain']['29.50'] = [6.11, 1.60]
# limits['median_gain']['30.00'] = [6.46, 1.63]
# limits['median_gain']['30.50'] = [6.58, 1.93]
# limits['median_gain']['31.00'] = [5.51, 1.55]
# limits['tlm_spread'] = 3.50
# limits['lens_delta'] = 5.00
# limits['rfic_offset'] = 8.00
# limits['rfic_spread'] = 10.00
# limits['rfic_minmax'] = 24.00
# spread_factor = 2.0
##0.3shift
limits = {}
limits['median_gain'] = {}
limits['median_gain']['27.50'] = [1.37, 2.33]
limits['median_gain']['28.00'] = [5.82, 1.74]
limits['median_gain']['28.50'] = [6.06, 1.87]
limits['median_gain']['29.00'] = [5.13, 2.12]
limits['median_gain']['29.50'] = [6.11, 1.90]
limits['median_gain']['30.00'] = [6.46, 1.93]
limits['median_gain']['30.50'] = [6.58, 2.23]
limits['median_gain']['31.00'] = [5.51, 1.85]
limits['tlm_spread'] = 3.80
limits['lens_delta'] = 5.30
limits['rfic_offset'] = 8.30
limits['rfic_spread'] = 10.30
limits['rfic_minmax'] = 24.30
spread_factor = 2.3

# pass fail
df['pass'] = True
pass_rate_log = []

for idx in range(len(df)):
    freq_set = df.iloc[idx]['frequency [GHz]'];
    freq_set = str(freq_set) + '0'
    lower_lim = limits['median_gain'][freq_set][0] - spread_factor * limits['median_gain'][freq_set][1]
    upper_lim = limits['median_gain'][freq_set][0] + spread_factor * limits['median_gain'][freq_set][1]
    if not lower_lim < df.iloc[idx]['gain_median [dB]'] < upper_lim:
        df.at[idx, 'pass'] = False
passed = len(df[df['pass'] == True])
pass_rate_log.append(round(float(passed) / float(len(df)) * 100, 2))
print(pass_rate_log)
#df['pass'] = True
for idx in range(len(df)):
    freq_set = df.iloc[idx]['frequency [GHz]'];
    freq_set = str(freq_set) + '0'
    if df.iloc[idx]['min_port [dB]'] < limits['median_gain'][freq_set][0] - 20.0:
        df.at[idx, 'pass'] = False
passed = len(df[df['pass'] == True])
pass_rate_log.append(round(float(passed) / float(len(df)) * 100, 2))
print(pass_rate_log)
#df['pass'] = True
for idx in range(len(df)):
    if df.iloc[idx]['gain_spread [dB]'] > limits['tlm_spread']:
        df.at[idx, 'pass'] = False
passed = len(df[df['pass'] == True])
pass_rate_log.append(round(float(passed) / float(len(df)) * 100, 2))
print(pass_rate_log)
#df['pass'] = True
for idx in range(len(df)):
    if df.iloc[idx]['lens_delta_max [dB]'] > limits['lens_delta']:
        df.at[idx, 'pass'] = False
passed = len(df[df['pass'] == True])
pass_rate_log.append(round(float(passed) / float(len(df)) * 100, 2))
print(pass_rate_log)
#df['pass'] = True
for idx in range(len(df)):
    if abs(df.iloc[idx]['rfic_offset_max [dB]']) > limits['rfic_offset']:
        df.at[idx, 'pass'] = False
passed = len(df[df['pass'] == True])
pass_rate_log.append(round(float(passed) / float(len(df)) * 100, 2))
print(pass_rate_log)
#df['pass'] = True
for idx in range(len(df)):
    if abs(df.iloc[idx]['rfic_spread_max [dB]']) > limits['rfic_spread']:
        df.at[idx, 'pass'] = False
passed = len(df[df['pass'] == True])
pass_rate_log.append(round(float(passed) / float(len(df)) * 100, 2))
print(pass_rate_log)
#df['pass'] = True
for idx in range(len(df)):
    if abs(df.iloc[idx]['rfic_minmax_max [dB]']) > limits['rfic_minmax']:
        df.at[idx, 'pass'] = False
passed = len(df[df['pass'] == True])
pass_rate_log.append(round(float(passed) / float(len(df)) * 100, 2))
print(pass_rate_log)
#df['pass'] = True
diffs = []
for idx in range(len(df)):
    entry = df.iloc[idx]
    board = df.iloc[idx]['board']
    f = df.iloc[idx]['frequency [GHz]']
    beam = df.iloc[idx]['beam']
    if beam == 1:
        other_beam = 2
    else:
        other_beam = 1
    df_other_beam = df[df['board'] == board]
    df_other_beam = df_other_beam[df_other_beam['frequency [GHz]'] == f]
    df_other_beam = df_other_beam[df_other_beam['beam'] == other_beam]
    diffs.append(abs(entry['gain_median [dB]'] - list(dict(df_other_beam)['gain_median [dB]'])[0]))
    if abs(entry['gain_median [dB]'] - list(dict(df_other_beam)['gain_median [dB]'])[0]) > 3.3:
        df.at[idx, 'pass'] = False

df['board_status'] = df['pass'].apply(lambda x: "True" if x else "False")

for board in df['board'].unique():
    # Select the subset of rows with this specific board number
    board_rows = df[df['board'] == board]

    # Check if all rows with this board number have `pass` == True
    if not board_rows['pass'].all():
        # If any row fails, set the `board_status` to "Fail" for this board number
        df.loc[df['board'] == board, 'board_status'] = "False"

boards, board_pass, pass_rate = pass_rate(df)
print(pass_rate)
print(board_pass)
print(boards)

print('board_pass:',len(board_pass))
print('Boards:',len(boards))
#print(boards)
True_boards = []  # List to store boards that passed
dropped = []

unique_dropped_boards = set()  # Set to hold unique boards with dropped ports

# Loop through each board to find the dropped ones without duplicates
for idx, row in df.iterrows():
    if row['dropped_port']:
        unique_dropped_boards.add(row['board'])  # Add board to set (no duplicates)

# Print the unique boards where dropped_flag is True
if unique_dropped_boards:
    print("Unique boards with dropped ports:", unique_dropped_boards)
else:
    print("No dropped ports found.")
def repeat_values(board_pass, repeat_count):
    repeated_list = []
    for value in board_pass:
        repeated_list.extend([value] * repeat_count)
    return repeated_list

# Repeat each value 8 times
repeated_values = repeat_values(board_pass, 8)


print(repeated_values)

for i in range(len(boards)):
    if board_pass[i]:
        True_boards.append(boards[i])
# for j in range(len(boards)):
#     if df['dropped_port'][j]:
#         dropped.append(boards[j])
# print('Dropped:',dropped)
print(True_boards)
print(len(True_boards))



 #plots
for freq_set in freq_list:
    fig, axs = plt.subplots(nrows=4, ncols=4, figsize=(40, 25))
    df_freq = df[df['frequency [GHz]'] == float(freq_set)]
    for beam in [1, 2]:
        df_plot = df_freq[df_freq['beam'] == beam]

        # median tlm gain
        sns.histplot(data=df_plot, x='gain_median [dB]', kde=True, ax=axs[0 + (2 * (beam - 1)), 0])
        axs[0 + (2 * (beam - 1)), 0].set_title(f'Median TLM gain [dB] (beam{beam})')
        axs[0 + (2 * (beam - 1)), 0].set_xlim([-6, 12])

        gain_median_terminal = np.median(df_plot['gain_median [dB]'])
        gain_spread_terminal = np.std(df_plot['gain_median [dB]'])
        axs[0 + (2 * (beam - 1)), 0].axvline(x=gain_median_terminal, color='k', linestyle='--', linewidth=2.0)
        axs[0 + (2 * (beam - 1)), 0].axvline(
            x=limits['median_gain'][freq_set][0] - spread_factor * limits['median_gain'][freq_set][1], color='r')
        axs[0 + (2 * (beam - 1)), 0].axvline(
            x=limits['median_gain'][freq_set][0] + spread_factor * limits['median_gain'][freq_set][1], color='r')
        axs[0 + (2 * (beam - 1)), 0].axvspan(
            limits['median_gain'][freq_set][0] - 10 * limits['median_gain'][freq_set][1],
            limits['median_gain'][freq_set][0] - spread_factor * limits['median_gain'][freq_set][1], alpha=0.25,
            color='red')
        axs[0 + (2 * (beam - 1)), 0].axvspan(
            limits['median_gain'][freq_set][0] + spread_factor * limits['median_gain'][freq_set][1],
            limits['median_gain'][freq_set][0] + 10 * limits['median_gain'][freq_set][1], alpha=0.25, color='red')
        # axs[0+(2*(beam-1)),0].annotate('', xy=(limits['median_gain'][freq_set][0]-spread_factor*limits['median_gain'][freq_set][1], 3.0), xytext=(limits['median_gain'][freq_set][0]+spread_factor*limits['median_gain'][freq_set][1], 3.0), arrowprops=dict(arrowstyle='<->', color='red', lw=2))
        # axs[0+(2*(beam-1)),0].text(gain_median_terminal-4.0*gain_spread_terminal, 3.0, f' 4std = 4 * {np.round(gain_spread_terminal,2)}', ha='center', va='center', color='red')
        # print(f'{freq_set}')
        # print(round(gain_median_terminal,2))
        # print(round(gain_spread_terminal,2))

        # tlm spread
        sns.histplot(data=df_plot, x='gain_spread [dB]', kde=True, ax=axs[0 + (2 * (beam - 1)), 1])
        axs[0 + (2 * (beam - 1)), 1].set_title(f'TLM spread [dB] (beam{beam})')
        axs[0 + (2 * (beam - 1)), 1].set_xlim([2, 4])

        axs[0 + (2 * (beam - 1)), 1].axvline(x=limits['tlm_spread'], color='r')
        axs[0 + (2 * (beam - 1)), 1].axvspan(limits['tlm_spread'], 1e6, alpha=0.25, color='red')

        # lens gain
        sns.histplot(data=df_plot, x='lens1_median [dB]', kde=True, ax=axs[0 + (2 * (beam - 1)), 2], label='lens1')
        sns.histplot(data=df_plot, x='lens2_median [dB]', kde=True, ax=axs[0 + (2 * (beam - 1)), 2], label='lens2')
        sns.histplot(data=df_plot, x='lens3_median [dB]', kde=True, ax=axs[0 + (2 * (beam - 1)), 2], label='lens3')
        axs[0 + (2 * (beam - 1)), 2].set_title(f'Lens gain [dB] (beam{beam})')
        axs[0 + (2 * (beam - 1)), 2].set_xlim([-6, 12])
        axs[0 + (2 * (beam - 1)), 2].set_xlabel('lens_median [dB]')
        axs[0 + (2 * (beam - 1)), 2].legend()

        # lens delta
        sns.histplot(data=df_plot, x='lens_delta_max [dB]', kde=True, ax=axs[0 + (2 * (beam - 1)), 3])
        axs[0 + (2 * (beam - 1)), 3].set_title(f'Largest lens delta [dB] (beam{beam})')
        axs[0 + (2 * (beam - 1)), 3].set_xlim([0, 12])

        axs[0 + (2 * (beam - 1)), 3].axvline(x=limits['lens_delta'], color='r')
        axs[0 + (2 * (beam - 1)), 3].axvspan(limits['lens_delta'], 1e6, alpha=0.25, color='red')

        # largest RFIC delta
        sns.histplot(data=df_plot, x='rfic_offset_max [dB]', kde=True, binwidth=1, ax=axs[1 + (2 * (beam - 1)), 0])
        axs[1 + (2 * (beam - 1)), 0].set_title(f'Largest deviation of RFIC \n from 57 RFICs [dB] (beam{beam})')
        axs[1 + (2 * (beam - 1)), 0].set_xlim([-12, 12])

        axs[1 + (2 * (beam - 1)), 0].axvline(x=-limits['rfic_offset'], color='r')
        axs[1 + (2 * (beam - 1)), 0].axvspan(-1e6, -limits['rfic_offset'], alpha=0.25, color='red')
        axs[1 + (2 * (beam - 1)), 0].axvline(x=limits['rfic_offset'], color='r')
        axs[1 + (2 * (beam - 1)), 0].axvspan(limits['rfic_offset'], 1e6, alpha=0.25, color='red')

        # channel spread
        sns.histplot(data=df_plot, x='rfic_spread_max [dB]', kde=True, ax=axs[1 + (2 * (beam - 1)), 1])
        axs[1 + (2 * (beam - 1)), 1].set_title(f'Spread of 8 channels on RFIC [dB] (beam{beam})')
        axs[1 + (2 * (beam - 1)), 1].set_xlim([0, 18])
        # for_print = np.median(df_plot['rfic_spread_max [dB]'])
        # print(f'{freq_set}GHz, beam{beam}, {for_print}')

        axs[1 + (2 * (beam - 1)), 1].axvline(x=limits['rfic_spread'], color='r')
        axs[1 + (2 * (beam - 1)), 1].axvspan(limits['rfic_spread'], 1e6, alpha=0.25, color='red')

        # max deviation of channels on RFIC
        sns.histplot(data=df_plot, x='rfic_minmax_max [dB]', kde=True, ax=axs[1 + (2 * (beam - 1)), 2])
        axs[1 + (2 * (beam - 1)), 2].set_title(f'Maximum deviation of channels on an RFIC [dB] (beam{beam})')
        axs[1 + (2 * (beam - 1)), 2].set_xlim([0, 30])

        axs[1 + (2 * (beam - 1)), 2].axvline(x=limits['rfic_minmax'], color='r')
        axs[1 + (2 * (beam - 1)), 2].axvspan(limits['rfic_minmax'], 1e6, alpha=0.25, color='red')

        # wafers
        # sns.histplot(data=df_plot, x='gain_median [dB]', kde=True, ax=axs[1+(2*(beam-1)),3], hue='lot')
        # axs[1+(2*(beam-1)),3].set_title(f'Gain Median with Wafer Lots [dB]')
        # axs[1+(2*(beam-1)),3].set_xlim([-6,12])
        # axs[1+(2*(beam-1)),3].set_ylim([0,8])

        # RFICs with max deviation
        sns.histplot(df_plot['rfic_minmax_maxidx'], ax=axs[1 + (2 * (beam - 1)), 3])
        axs[1 + (2 * (beam - 1)), 3].set_title(f'RFIC with the largest channel deviation (beam{beam})')
        axs[1 + (2 * (beam - 1)), 3].set_xlim([0, 60])

    N = len(df_plot)
    plt.suptitle(f'{freq_set} GHz \n {file_path}, N={N}')
    plt.tight_layout()

    freq_save = freq_set.replace('.', 'g')
    plt.savefig(f'{freq_save}.png', dpi=400)

# From this point on it is the initial 'simplified' ranking system. Generally I do not use this.
rank_run = False
if rank_run == True:

    df_ranked = pd.DataFrame()
    for beam in [1, 2]:
        for freq_set in freq_list:
            # load reference board
            find_measFiles(r'C:\Users\jmitchell\Downloads\MCR1_Rig1_TLM_00143', 'OP_2', beam, freq_set)
            load__measFiles(measFiles[0])
            col = np.argmin((meas_frequencies - float(freq_set)) ** 2)
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
    for freq_set in freq_list:
        fig, axs = plt.subplots(nrows=2, ncols=1, figsize=(15, 10))
        for board in boards_ranked:
            df_board = df_ranked[df_ranked['board'] == board]
            df_board = df_board[df_board['frequency [GHz]'] == float(freq_set)]
            axs[0].plot(board, list(df_board['gain_median [dB]'])[0], 'ko')
            axs[0].plot(board, list(df_board['gain_median [dB]'])[1], 'r^')
            axs[1].plot(board, list(df_board['gain_spread [dB]'])[0], 'ko')
            axs[1].plot(board, list(df_board['gain_spread [dB]'])[1], 'r^')
        axs[0].plot(board, list(df_board['gain_median [dB]'])[0], 'ko', label='beam1')
        axs[0].plot(board, list(df_board['gain_median [dB]'])[1], 'r^', label='beam2')
        axs[1].plot(board, list(df_board['gain_spread [dB]'])[0], 'ko', label='beam1')
        axs[1].plot(board, list(df_board['gain_spread [dB]'])[1], 'r^', label='beam2')
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

        freq_set_forsave = freq_set.replace('.', 'g')
        plt.savefig(f'{freq_set_forsave}GHz.png', dpi=400)

#print(board_pass * 16)
#df['Overall_pass'] = board_pass * 16

#

#DataF = pd.DataFrame({'Boards': boards, 'board_pass': board_pass#})
#DataF.to_excel('Output_boards_Pass.xlsx', index=False)


sort = df.sort_values(by=['Date_Time'], ascending=True)

df_no_duplicates = df.drop_duplicates()

df['pf'] = df['board_status'].apply(lambda x: 1 if x is True or str(x).lower() == "true" else 0)
df['rolling_avg'] = df['pf'].rolling(window=5, min_periods=1).mean()*100

df.to_csv("output_test.csv", index=False)

num_boards = len(boards)

# Plot board_status
plt.plot(df['Date_Time'][:num_boards], df['board_status'][:num_boards])
plt.tick_params(axis='x', labelrotation=90, labelsize=8)
plt.gca().invert_yaxis()  # Only invert if necessary
plt.show()

# Plot rolling average of pf
plt.plot(df['Date_Time'][:num_boards], df['rolling_avg'][:num_boards])
plt.tick_params(axis='x', labelrotation=90, labelsize=8)
plt.show()


