import pandas as pd
import numpy as np
import matplotlib.patches as patches
import matplotlib.pyplot as plt;

plt.rcParams['font.size'] = 12;
plt.close('all')
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

# file path
dirScript = os.getcwd()

# parmas
temperature = '45'
tlmType = 'Tx'
measType = 'Calibration'  # 'Calibration' or 'Evaluation'
filePath = r'C:\Users\RyanFairclough\Downloads\Points_1001'
SaveFileName = '\Post_Processed_Data'#_RFA'
BoardFont = '6'
counter = 0
mask_lim_variable = []
external_folder_name = "Figures\\StressTest\\MCR1_Rig1"
measFileShift = 0
droppedThresh = 8
Exempt_Folder = 'combiner'

# frequencies to iterate through
if tlmType == 'Tx':
    mask_lim_variable = [5]
if tlmType == 'Rx':
    mask_lim_variable = [5]
if measType == 'Evaluation' and tlmType == 'Tx':
    f_set_list = [29.5]
elif measType == 'Calibration' and tlmType == 'Tx':
    f_set_list = [27.5]
elif measType == 'Evaluation' and tlmType == 'Rx':
    f_set_list = [19.2]
elif measType == 'Calibration' and tlmType == 'Rx':
    f_set_list = [17.70, 18.20, 18.70, 19.20, 19.70, 20.20, 20.70, 21.20]


# definitions
def find_measFiles(path, fileString, beam):
    global measFiles, files
    files = []
    for root, directories, file in os.walk(path):
        for file in file:
            if (file.endswith(".csv")) == True:
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
    # meas_info, array and measurement frequencies
    with open(filePath, 'r') as file:
        filecontent = csv.reader(file, delimiter=',')
        time.sleep(0.10)
        for row in filecontent:
            meas_info.append(row)
        index_start = [index for index in range(len(meas_info)) if 'barcodes' in meas_info[index]][0] + 2
        meas_info = meas_info[0:index_start]
        meas_array = np.genfromtxt(filePath, delimiter=',', skip_header=index_start)
        meas_array_gain = meas_array[:,::2]
        meas_array_phase = meas_array[:,1:][:,::2]
        meas_frequencies = np.array(meas_info[index_start - 1])[::2].astype(float)
        #print('MEAS:',meas_array_gain)

    for i in range(len(meas_info) - 1):
        if len(meas_info[i]) > 1:
            paramName = meas_info[i][0]

            if paramName[0:2] == '# ':
                paramName = paramName[2:]
            meas_params[paramName] = meas_info[i][1]


def plot__gainVport(f_set, measType):
    global y, stat_TLM_median, loaded, y_gain, meas_frequencies, meas_frequencies_list, meas_array_gain
    fig.suptitle(measType + ': ' + str(f_set) + ' GHz, Beam ' + str(beam) + ', ' + str(temperature) + ' degC',
                 fontsize=25)
    if float(meas_params['f_c']) == f_set and len(meas_array) > 2:
        print('Plotting')
        # array
        #col = int(np.where(meas_frequencies == f_set)[0][0] * 2)

        indices = np.where(meas_frequencies == f_set)[0]
        unique_indices = np.unique(indices)
        cols_to_extract = unique_indices * 2

        y = meas_array[:, cols_to_extract]
        #y = meas_array[:, col]
        y_gain = y * 1.0
        meas_frequencies_list = meas_frequencies.tolist()
        print(meas_frequencies_list)
        print('xxx:',f_set)
        print(y)

        # stats
        stat_TLM_median = np.median(y)
        stat_TLM_median_log.append(stat_TLM_median)
        stat_l1_median = np.median(y[0:int(len(y) / 3)])
        stat_l2_median = np.median(y[int(len(y) / 3):2 * int(len(y) / 3)])
        stat_l3_median = np.median(y[2 * int(len(y) / 3):3 * int(len(y) / 3)])
        stat_l1_dropped = ((y[0:int(len(y) / 3)]) < droppedThresh).sum()
        stat_l1_dropped_list = ((y[0:int(len(y) / 3)]) < droppedThresh)
        stat_l2_dropped_list = ((y[int(len(y) / 3):2 * int(len(y) / 3)]) < droppedThresh)
        stat_l3_dropped_list = ((y[2 * int(len(y) / 3):3 * int(len(y) / 3)]) < droppedThresh)
        log = []
        for p in range(len(stat_l1_dropped_list)):
            if stat_l1_dropped_list[p] == True:
                log.append(p + 1)
        for p in range(len(stat_l2_dropped_list)):
            if stat_l2_dropped_list[p] == True:
                log.append(1 * int(len(y) / 3) + p + 1)
        for p in range(len(stat_l3_dropped_list)):
            if stat_l3_dropped_list[p] == True:
                log.append(2 * int(len(y) / 3) + p + 1)
        if len(log) > 12:
            log = [str(len(log)) + ' ports dropped']
        stat_l2_dropped = ((y[int(len(y) / 3):2 * int(len(y) / 3)]) < droppedThresh).sum()
        stat_l3_dropped = ((y[2 * int(len(y) / 3):3 * int(len(y) / 3)]) < droppedThresh).sum()
        stat_TLM_std = np.std(y, dtype=np.float64)  ##

        stat_l1_std = np.std(y[0:int(len(y) / 3)])
        stat_l2_std = np.std(y[int(len(y) / 3):2 * int(len(y) / 3)])
        stat_l3_std = np.std(y[2 * int(len(y) / 3):3 * int(len(y) / 3)])

        # plots
        dataSetLabel = meas_params['date time'] + '\n' + meas_params['lens type (rx/tx)'] + meas_params['barcodes'] + ', SW: ' + meas_params['acu_version'] + '\n ITCC: ' + meas_params['itcc_runner_version']
        # plot 1
        minY = -30
        maxY = 60

        y1 = y


        X, Y = np.meshgrid(meas_frequencies_list, np.linspace(minY, maxY, 100))

        #heatmap = plt.imshow([y1], cmap='viridis', aspect='auto', extent=[meas_frequencies_list[0], meas_frequencies_list[-1], minY, maxY])
        heatmap = axs[0, 0].imshow([y1], cmap='viridis', aspect='auto',extent=[meas_frequencies_list[0], meas_frequencies_list[-1], minY, maxY])

        cbar = plt.colorbar(heatmap, ax=axs[0, 0])
        axs[0, 0].set_xlabel('Frequencies')
        axs[0, 0].set_ylabel('S$_{21}$ [dB]')
        axs[0, 0].set_xlim([meas_frequencies_list[0], meas_frequencies_list[-1]])
        axs[0, 0].set_ylim([minY, maxY])
        axs[0, 0].grid(True)


        # plot 2
        axs[0, 1].plot(dataSetLabel, stat_l1_median, 'rs')
        axs[0, 1].plot(dataSetLabel, stat_l2_median, 'g^')
        axs[0, 1].plot(dataSetLabel, stat_l3_median, 'bP')
        axs[0, 1].plot(dataSetLabel, stat_TLM_median, 'kX', markersize=10)
        axs[0, 1].set_xlabel('board')
        axs[0, 1].set_ylabel('Median [dB]')
        axs[0, 1].tick_params(axis='x', labelrotation=90, labelsize=BoardFont)
        axs[0, 1].set_ylim([minY, maxY])
        axs[0, 1].grid('on')

        # out
        loaded = True
    else:
        loaded = False


# run
for p in range(2):
    beam = p + 1
    for l in range(len(f_set_list)):
        f_set = f_set_list[l]


        # find all meas files
        find_measFiles(filePath, 'OP', beam)

        fig, axs = plt.subplots(3, 2, figsize=(25, 15))
        stat_TLM_median_log = []
        y_gain_log = []
        tlm_log = []
        for k in range(len(measFiles) - measFileShift):

            # load meas file
            if '_4' in measFiles[k]:  # if str(temperature) + 'C' in measFiles[k]:
                load_measFiles(measFiles[k])
                print('-------------------------------------')
                print(meas_params['date time'][1:])
                print(meas_params['barcodes'])
                print('Temperature = ' + meas_params['Temp. [°C]'])
                print('-------------------------------------')

                # plot
                if '.' in meas_params['acu_version']:
                    plot__gainVport(f_set, measType)
                    # colate
                    if loaded == True:
                        stat_TLM_median_log.append(stat_TLM_median)
                        y_gain_log.append(y_gain)
                        tlm_log.append(meas_params['barcodes'])

        # format
        plt.tight_layout()

        # save
        fileName = measType + '_f-set' + str(f_set) + '_b' + str(beam) + '.png'
        newPath = filePath + SaveFileName
        if not os.path.exists(newPath):
            os.makedirs(newPath)
        plt.savefig(newPath + '/' + fileName, dpi=200)

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