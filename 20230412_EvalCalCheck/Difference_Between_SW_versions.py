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
tlmType = 'Rx'
filePath = r'C:\Users\RyanFairclough\ALL.SPACE\Engineering - Systems\S2000 0.8m\DVT\F-Type\Rx_TLM_F-Type\TLM_Evaluation_Measurements\Batch2'
SaveFileName = '\Post_Processed_Data'
BoardFont = '6'
counter = 0
measType = 'Evaluation'  # 'Calibration' or 'Evaluation'
external_folder_name = "Figures\\StressTest\\MCR1_Rig1"
measFileShift = 0
droppedThresh = -5

# frequencies to iterate through
# frequencies to iterate through
if measType == 'Evaluation' and tlmType == 'Tx':
    f_set_list = [29.5]
    droppedThreshList = [droppedThresh]
elif measType == 'Calibration' and tlmType == 'Tx':
    f_set_list = [27.5, 28.0, 28.5, 29.0, 29.5, 30.0, 30.5, 31.0]
    droppedThreshList = [-15, -15, -11, -9, -15, -6, -15, -20]
elif measType == 'Evaluation' and tlmType == 'Rx':
    f_set_list = [19.2]
    droppedThreshList = [droppedThresh]
elif measType == 'Calibration' and tlmType == 'Rx':
    f_set_list = [19.20]#[17.70, 18.20, 18.70, 19.20, 19.70, 20.20, 20.70, 21.20]
    droppedThreshList = [12, 10, 15, 15, 15, 12, 12, 5]

def find_measFiles(path, fileString, beam):
    global measFiles, files
    files = []
    for root, directories, file in os.walk(path):
        for file in file:
            if (file.endswith(".csv")) == True:
                files.append(os.path.join(root, file))
    measFiles = []
    for i in range(len(files)):
        if fileString in files[i] and 'eam' + str(beam) in files[i] and 'combiner' not in files[i]:
            measFiles.append(files[i])

def load_measFiles(filePath):
    global meas_info, meas_array, meas_frequencies, meas_params
    meas_params = {}
    meas_info = []
    # meas_info, array and measurement frequencies
    with open(filePath, 'r') as file:
        filecontent = csv.reader(file, delimiter=',')
        time.sleep(0.10)
        for row in filecontent:
            meas_info.append(row)
        index_start = [index for index in range(len(meas_info)) if 'barcodes' in meas_info[index]][0] + 2
        meas_info = meas_info[0:index_start]

        meas_array = np.genfromtxt(filePath, delimiter=',', skip_header=index_start)
        meas_frequencies = np.array(meas_info[index_start - 1])[::2].astype(float)


    for i in range(len(meas_info) - 1):
        if len(meas_info[i]) > 1:
            paramName = meas_info[i][0]

            if paramName[0:2] == '# ':
                paramName = paramName[2:]
            meas_params[paramName] = meas_info[i][1]


def plot__gainVport(f_set, measType):
    global y, stat_TLM_median, loaded, y_gain
    fig.suptitle(measType + ': ' + str(f_set) + ' GHz, Beam ' + str(beam) + ', ' + str(temperature) + ' degC',
                 fontsize=25)
    if float(meas_params['f_c']) == f_set and len(meas_array) > 2:
        print('Plotting')
        # array
        col = int(np.where(meas_frequencies == f_set)[0][0] * 2)
        y = meas_array[:, col]
        y_gain = y * 1.0


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


        # plots
        dataSetLabel = meas_params['date time'] + '\n' + meas_params['lens type (rx/tx)'] + meas_params['barcodes'] + ', SW: ' + meas_params['acu_version'] + '\n ITCC: ' + meas_params['itcc_runner_version']
        # plot 1
        minY = -30
        maxY = 60
        axs[0, 0].vlines(int(len(y) / 3), minY, maxY, 'k', alpha=0.2)
        axs[0, 0].vlines(2 * int(len(y) / 3), minY, maxY, 'k', alpha=0.2)
        axs[0, 0].text(0.8 * int(len(y) / 6), minY + 5, 'Lens 1', backgroundcolor='r', fontsize=20)
        axs[0, 0].text(2.8 * int(len(y) / 6), minY + 5, 'Lens 2', backgroundcolor='g', fontsize=20)
        axs[0, 0].text(4.8 * int(len(y) / 6), minY + 5, 'Lens 3', backgroundcolor='b', fontsize=20)
        #colormap = plt.get_cmap('viridis')
        #colors = np.linspace(0, 1, len(y))
        #axs[0, 0].scatter(np.linspace(1, len(y), num=len(y)), y, c=colors, cmap=colormap, alpha=0.2)
        axs[0, 0].plot(np.linspace(1, len(y), num=len(y)), y, 'k', alpha=0.2)
        axs[0, 0].set_xlabel('port')
        axs[0, 0].set_ylabel('S$_{21}$ [dB]')
        axs[0, 0].set_xticks([0.5 * int(len(y) / 3), 1 * int(len(y) / 3), 1.5 * int(len(y) / 3),  2 * int(len(y) / 3), 2.5 * int(len(y) / 3), 3 * int(len(y) / 3)])
        axs[0, 0].set_xlim([1, len(y) + 1])
        axs[0, 0].set_ylim([minY, maxY])
        axs[0, 0].grid('on')
        axs[0, 0].axhline(y=droppedThresh, color="red", linestyle='--')
        # plot 2

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



        # plot histogram
        ymax1 = 25.0
        mean = np.mean(np.array(stat_TLM_median_log))


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