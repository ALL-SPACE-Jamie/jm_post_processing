import pandas as pd
import numpy as np
import matplotlib.patches as patches
import matplotlib.pyplot as plt
from decimal import Decimal
from scipy.stats import norm
import os
import glob
import copy
import csv
import json
import time
import math
import statistics
import shutil


plt.rcParams['font.size'] = 12
plt.close('all')

# File path
dirScript = os.getcwd()

# Params
temperature = '45'
tlmType = 'Tx'
measType = 'Calibration'  # 'Calibration' or 'Evaluation'
filePath = r'C:\Users\RyanFairclough\Downloads\new wafer_vA4_Tx\337'
SaveFileName = '\Post_Processed_Data'
Lens = 3
BoardFont = '6'
counter = 0
mask_lim_variable = []
external_folder_name = "Figures\\StressTest\\MCR1_Rig1"
measFileShift = 0
droppedThresh = 8
Exempt_Folder = 'combiner'

# Frequencies to iterate through
if tlmType == 'Tx':
    mask_lim_variable = [5]
if tlmType == 'Rx':
    mask_lim_variable = [5]
if measType == 'Evaluation' and tlmType == 'Tx':
    f_set_list = [29.5]
elif measType == 'Calibration' and tlmType == 'Tx':
    f_set_list = [27.5, 28.0, 28.5, 29.0, 29.5, 30.0, 30.5, 31.0]
elif measType == 'Evaluation' and tlmType == 'Rx':
    f_set_list = [19.2]
elif measType == 'Calibration' and tlmType == 'Rx':
    f_set_list = [17.70, 18.20, 18.70, 19.20, 19.70, 20.20, 20.70, 21.20]


# Definitions
def find_measFiles(path, fileString, beam):
    global measFiles, files
    files = []
    for root, directories, file in os.walk(path):
        for file in file:
            if (file.endswith(".csv")):
                files.append(os.path.join(root, file))
    measFiles = []
    for i in range(len(files)):
        if fileString in files[i] and 'eam' + str(beam) in files[i] and Exempt_Folder not in files[i]:
            measFiles.append(files[i])


def load_measFiles(filePath):
    global meas_info, meas_array, meas_frequencies, meas_params, meas_array_gain
    meas_params = {}
    meas_info = []
    meas_freq = []
    # Meas info, array and measurement frequencies
    with open(filePath, 'r') as file:
        filecontent = csv.reader(file, delimiter=',')
        time.sleep(0.10)
        for row in filecontent:
            meas_info.append(row)
        index_start = [index for index in range(len(meas_info)) if 'barcodes' in meas_info[index]][0] + 2
        meas_info = meas_info[0:index_start]
        meas_array = np.genfromtxt(filePath, delimiter=',', skip_header=index_start)
        meas_array_gain = meas_array[:, ::2]
        meas_array_phase = meas_array[:, 1:][:, ::2]
        meas_frequencies = np.array(meas_info[index_start - 1])[::2].astype(float)

    for i in range(len(meas_info) - 1):
        if len(meas_info[i]) > 1:
            paramName = meas_info[i][0]

            if paramName[0:2] == '# ':
                paramName = paramName[2:]
            meas_params[paramName] = meas_info[i][1]


def plot__gainVport(f_set, measType):
    global y, stat_TLM_median, loaded, y_gain, meas_frequencies, meas_frequencies_list, meas_array_gain, map_tlm_df, all_y_values,all_h_values, all_v_values

    if tlmType == 'Rx':
        map_rfic = pd.read_csv(r'C:\Users\RyanFairclough\PycharmProjects\Post-Processing\20231218_TLMPortMapPlot\20240227_tlm_map_plotter\20221019_TLMCalInputs\MK1_RX_TLM_RFIC_Patch_Feed_mapping_RF.csv')
    elif tlmType == 'Tx':
        map_rfic = pd.read_csv(r'C:\Users\RyanFairclough\PycharmProjects\Post-Processing\20231218_TLMPortMapPlot\20240227_tlm_map_plotter\20221019_TLMCalInputs\MK1_TX_TLM_RFIC_Patch_Feed_Mapping.csv')

    rfics = map_rfic['RFIC Number']
    h_feed = map_rfic['H-Feed (Odd)']
    v_feed = map_rfic['V-Feed (Even)']

    v_feed_list = v_feed.values.tolist()
    h_feed_list = h_feed.values.tolist()
    rfic_list = rfics.values.tolist()

    col = np.argmin((meas_frequencies - f_set) ** 2)


    if float(meas_params['f_c']) == f_set and len(meas_array) > 2:
        print('Plotting')

        # Array
        all_y_values = []
        all_h_values = []
        all_v_values = []

        start_col = int(np.where(meas_frequencies == meas_frequencies)[0][0] * 2)
        # Loop to measure every consecutive column with a skip of 1
        while start_col < meas_array.shape[1]:
            if Lens == 1:
                y = meas_array[0:152, start_col]
                Z = meas_array[0:152, start_col]
            elif Lens == 2:
                y = meas_array[152:304, start_col]
                Z = meas_array[152:304, start_col]
            elif Lens == 3:
                y = meas_array[304:456, start_col]
                Z = meas_array[304:456, start_col]
            y_H = Z[::2]
            y_V = Z[1::2]
            all_y_values.append(y)
            all_h_values.append(y_H)
            all_v_values.append(y_V)
            #print(y_H)
            # Increment the column index by 2 for the next iteration
            start_col += 2

        v_feed_dict = dict(zip(y_V, v_feed_list))
        h_feed_dict = dict(zip(y_H, h_feed_list))

        #print("Z_trim_h to H-Feed Mapping:", h_feed_dict)
        #print("Z_trim_v to V-Feed Mapping:", v_feed_dict)

        rfic_feed_mapping = [
            {
                'RFIC Number': rfic_list[i],
                'y_H': y_H[i] if i < len(y_H) else None,
                'H-Feed': h_feed_dict.get(y_H[i], None) if i < len(y_H) else None,
                'y_V': y_V[i] if i < len(y_V) else None,
                'V-Feed': v_feed_dict.get(y_V[i], None) if i < len(y_V) else None
            }
            for i in range(len(rfic_list))
        ]

        #print("RFIC to Z_trim and Feed Mapping:")
        for mapping in rfic_feed_mapping:
            print(mapping)


        num_columns = meas_array.shape[1]
        print('Num Col:', num_columns)

        y_gain = y * 1.0
        meas_frequencies_list = meas_frequencies.tolist()
        #print(meas_frequencies_list)


        # Stats
        stat_TLM_median = np.median(y)
        stat_TLM_median_log.append(stat_TLM_median)



        # Plots
        #dataSetLabel = meas_params['date time'] + '\n' + meas_params['lens type (rx/tx)'] + meas_params['barcodes'] + ', SW: ' + meas_params['acu_version'] + '\n ITCC: ' + meas_params['itcc_runner_version']
        dataSetLabel = meas_params['lens type (rx/tx)'] + meas_params['barcodes'] + ', SW: ' + meas_params['acu_version'] + f'Lens: {Lens}'
        list=[]
        len_y = len(y)

        for i in range(len(y)):
            list.append(i)
        print(all_v_values)
        # -----------------------------------------NEED TO CONVERT RFIC / FREQUENCY IN DF-------------------------------------------------------------
        # Plotting the heatmap

        fig, axs = plt.subplots(2)
        heatmap = axs[0].imshow(all_h_values, cmap='RdYlGn', aspect='auto',extent=[0, len(rfic_list), meas_frequencies_list[-1],meas_frequencies_list[0]])
        heatmap2 = axs[1].imshow(all_y_values, cmap='RdYlGn', aspect='auto',extent=[0, len(rfic_list), meas_frequencies_list[-1], meas_frequencies_list[0]])
        #heatmap = ax.imshow(all_y_values, cmap='RdYlGn', aspect='auto',extent=[0, len(y), meas_frequencies_list[-1], meas_frequencies_list[0]])
        # Adding a colorbar
        cbar = plt.colorbar(heatmap, ax=axs[0])
        cbar = plt.colorbar(heatmap2, ax=axs[1])

        # Setting labels and limits
        axs[0].set_xlabel('Ports')
        axs[0].set_ylabel('Frequency')
        axs[0].set_title('H Ports')
        xticks = np.arange(0, len(rfic_list) + 5, 5)
        axs[0].set_xticks(xticks)
        yticks = np.arange(27.5, 31.5 + 0.5, 0.5)
        Descend = np.sort(yticks)[::-1]
        axs[0].set_yticks(Descend)
        axs[0].set_xlim([0, len(rfic_list)])
        axs[0].set_ylim([meas_frequencies_list[0], meas_frequencies_list[-1]])

        axs[1].set_xlabel('Ports')
        axs[1].set_ylabel('Frequency')
        axs[1].set_title('V Ports')
        xticks = np.arange(0, len(rfic_list) + 5, 5)
        axs[1].set_xticks(xticks)
        yticks = np.arange(27.5, 31.5 + 0.5, 0.5)
        Descend = np.sort(yticks)[::-1]
        axs[1].set_yticks(Descend)
        axs[1].set_xlim([0, len(rfic_list)])
        axs[1].set_ylim([meas_frequencies_list[0], meas_frequencies_list[-1]])

        axs[0].set_title(dataSetLabel)

        num_arrays = len(all_v_values)
        array_length = len(all_v_values[0])

        # Initialize a list to keep track of consistent drops
        consistent_drops = [True] * array_length

        # Iterate over each array
        for array in all_v_values:
            for idx, value in enumerate(array):
                if value >= -25:
                    consistent_drops[idx] = False

        # Check for consistent drops
        for idx, dropped in enumerate(consistent_drops):
            if dropped:
                print(f"Dropped port at index {idx+1}")
                nth_value = idx
                for i in range(len(rfic_list)):
                    if i == nth_value:
                        plt.text(0, 25, f'Port dropped at: {idx + 1} - Faulty RFIC: {rfic_list[nth_value]}', fontsize= 10)

        for array in all_h_values:
            for idx1, value in enumerate(array):
                if value >= -25:
                    consistent_drops[idx1] = False

        for idx1, dropped in enumerate(consistent_drops):
            if dropped:
                print(f"Dropped port at index {idx1+1}")
                plt.text(0, 25, f'Port dropped at: {idx1 + 1}', fontsize= 10)


        # Out
        loaded = True
    else:
        loaded = False


# Run
for p in range(2):
    beam = p + 1
    for l in range(len(f_set_list)):
        f_set = f_set_list[l]

        # Find all meas files
        find_measFiles(filePath, 'OP', beam)

        fig, axs = plt.subplots(figsize=(12, 8))
        stat_TLM_median_log = []
        y_gain_log = []
        tlm_log = []
        for k in range(len(measFiles) - measFileShift):

            # Load meas file
            if '_4' in measFiles[k]:  # if str(temperature) + 'C' in measFiles[k]:
                load_measFiles(measFiles[k])
                print('-------------------------------------')
                print(meas_params['date time'][1:])
                print(meas_params['barcodes'])
                print('Temperature = ' + meas_params['Temp. [°C]'])
                print('-------------------------------------')

                # Plot
                if '.' in meas_params['acu_version']:
                    plot__gainVport(f_set, measType)
                    # Colate
                    if loaded:
                        stat_TLM_median_log.append(stat_TLM_median)
                        y_gain_log.append(y_gain)
                        tlm_log.append(meas_params['barcodes'])

        # Format
        plt.tight_layout()

        # Save
        fileName = measType + '_f-set' + str(f_set) + '_b' + str(beam) + '.png'
        newPath = filePath + SaveFileName
        if not os.path.exists(newPath):
            os.makedirs(newPath)
        plt.savefig(newPath + '/' + fileName, dpi=200)
        plt.close()

external_path = os.path.join(filePath, external_folder_name)
os.makedirs(external_path, exist_ok=True)  # The path of the external folder

for dirpath, dirnames, filenames in os.walk(filePath):
    for file in filenames:
        if 'f-set' in file.lower():
            try:
                file_path = os.path.join(dirpath, file)
                shutil.copy(file_path, external_path)
                print(f"Copied_file_path_to_external_path")
            except shutil.SameFileError as e:
                print(f"Skipped copying file{file}:{e}")
print("Done.")
