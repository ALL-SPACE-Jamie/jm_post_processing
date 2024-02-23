import pandas as pd
import numpy as np
import matplotlib.patches as patches
import matplotlib.pyplot as plt;

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

# file path
dirScript = os.getcwd()

# parmas

temperature = '45'  ##
tlmType = 'Tx'
measType = 'Calibration'  # 'Calibration'  # 'Calibration' or 'Evaluation'
# filePath = r'C:\Users\JamieMitchell\OneDrive - ALL.SPACE\S-Type\Rx_TLM\ES2c-Laser_Cut\Test\MCR2\20230717 - 21\sw_test'
filePath = r'C:\Users\RyanFairclough\Downloads\IFBW_Cal_Reduction'
SaveFileName = '\Post_Processed_Data'
BoardFont = '6'
counter = 0
colours = ['red','blue','green','black','yellow','cyan', 'orange']
external_folder_name = "Figures\\StressTest\\MCR1_Rig1"
measFileShift = 0
droppedThresh = -10

if measType == 'Evaluation' and tlmType == 'Tx':
    f_set_list = [29.5]
    droppedThreshList = [droppedThresh]
elif measType == 'Calibration' and tlmType == 'Tx':
    f_set_list = [27.5, 28.0, 28.5, 29.0, 29.5, 30.0, 30.5, 31.0]
    droppedThreshList = [-15, -15, -10, -9, -15, -15, -15, -20]
elif measType == 'Evaluation' and tlmType == 'Rx':
    f_set_list = [19.2]
    droppedThreshList = [droppedThresh]
elif measType == 'Calibration' and tlmType == 'Rx':
    f_set_list = [17.7, 18.2, 18.7, 19.2, 19.7, 20.2, 20.7, 21.2]
    droppedThreshList = [10, 10, 15, 15, 15, 12, 12, -5]
if tlmType == 'Tx':
    mask = os.path.join(dirScript,r'2023_06_07_Sweep_Discrete_7pts_calibration_data_ES2_TX_TLM_Lens1_cal_equ_FR_Norm_renormalization_of_ports.csv')
if tlmType == 'Rx':
    mask = os.path.join(dirScript,r'2023_03_17_discrete_17700_21200_8_calibration_data_175-0081_sanmina_rel1c_2023_03_07_L1L14_48feed_calibration_13mm_dual_pol_probe.csv')


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
        if fileString in files[i] and 'eam' + str(beam) in files[i] and 'Archive' not in files[i]:
            measFiles.append(files[i])
    # print(measFiles)

def import_mask(f_set, mask, offset):
    global mask_gain, mask_phase
    meas_info = []
    meas_array = np.genfromtxt(mask, delimiter=',', skip_header=1)[:,2:]
    meas_array_frequencies = np.genfromtxt(mask, delimiter=',', skip_header=1)[0:int(len(meas_array)/2),1]
    index = np.argmin((meas_array_frequencies-float(f_set))**2)
    meas_arrayT = meas_array[index,:][::2]
    meas_arrayB = meas_array[int(len(meas_array)/2)+index,:][::2]
    meas_array_gain = np.zeros(len(meas_arrayT))
    for i in range(int(len(meas_arrayT)/2)):
        meas_array_gain[2*i] = meas_arrayT[2*i]
        meas_array_gain[2*i+1] = meas_arrayB[2*i+1]
    meas_arrayT = meas_array[index,:][1:][::2]
    meas_arrayB = meas_array[int(len(meas_array)/2)+index,:][1:][::2]
    meas_array_phase = np.zeros(len(meas_arrayT))
    for i in range(int(len(meas_arrayT)/2)):
        meas_array_phase[2*i] = meas_arrayT[2*i]
        meas_array_phase[2*i+1] = meas_arrayB[2*i+1]
    mask_gain = meas_array_gain*1.0 + offset
    mask_phase = meas_array_phase*1.0
    mask_gain = np.hstack([mask_gain, mask_gain, mask_gain])
    mask_phase = np.hstack([mask_phase, mask_phase, mask_phase])


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
        meas_array_gain = meas_array[:, ::2]
        meas_frequencies = np.array(meas_info[index_start - 1])[::2].astype(float)

    # meas_params
    for i in range(len(meas_info) - 1):
        if len(meas_info[i]) > 1:
            paramName = meas_info[i][0]

            if paramName[0:2] == '# ':
                paramName = paramName[2:]
            meas_params[paramName] = meas_info[i][1]
    print(meas_params)


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

        stat_TLM_median = np.median(y)
        stat_TLM_median_log.append(stat_TLM_median)
        stat_l1_dropped = ((y[0:int(len(y) / 3)]) < droppedThresh).sum()
        stat_l1_dropped_list = ((y[0:int(len(y) / 3)]) < droppedThresh)
        stat_l2_dropped_list = ((y[int(len(y) / 3):2 * int(len(y) / 3)]) < droppedThresh)
        stat_l3_dropped_list = ((y[2 * int(len(y) / 3):3 * int(len(y) / 3)]) < droppedThresh)
        log = []
        for p in range(len(stat_l1_dropped_list)):
            if stat_l1_dropped_list[p] == True:
                log.append(p+1)
        if len(log) > 12:
            log = [str(len(log)) + ' ports dropped']
        stat_l2_dropped = ((y[int(len(y) / 3):2 * int(len(y) / 3)]) < -droppedThresh).sum()
        stat_l3_dropped = ((y[2 * int(len(y) / 3):3 * int(len(y) / 3)]) < -droppedThresh).sum()

        # plots
        dataSetLabel = meas_params['date time'] + '\n' + meas_params['lens type (rx/tx)'] + meas_params['barcodes'] + ', SW: ' + meas_params['acu_version'] + '\n ITCC: ' + meas_params['itcc_runner_version']
        # plot 1
        minY = -30
        maxY = 50
        axs.vlines(int(len(y) / 3), minY, maxY, 'k', alpha=0.2)
        axs.vlines(2 * int(len(y) / 3), minY, maxY, 'k', alpha=0.2)
        axs.text(0.8 * int(len(y) / 6), minY + 5, 'Lens 1', backgroundcolor='r', fontsize=20)
        axs.text(2.8 * int(len(y) / 6), minY + 5, 'Lens 2', backgroundcolor='g', fontsize=20)
        axs.text(4.8 * int(len(y) / 6), minY + 5, 'Lens 3', backgroundcolor='b', fontsize=20)
        axs.plot(np.linspace(1, len(y) + 1, num=len(y)), y, 'k', alpha=0.2)
        axs.set_xlabel('port')
        axs.set_ylabel('S$_{21}$ [dB]')
        axs.set_xlim([1, len(y) + 1])
        axs.set_ylim([minY, maxY])
        axs.grid('on')
        axs.text(droppedThresh, 2, log)
        axs.axhline(y=droppedThresh, color="red", linestyle='--')
        x = np.arange(len(y))
        indices = [i for i, num in enumerate(y) if num < droppedThresh]
        for index in indices:
            axs.add_patch(plt.Circle((x[index], y[index], droppedThresh), radius=2, edgecolor='red', facecolor='none'))
        # plot 2

        # out
        loaded = True
    else:
        loaded = False


# Loop through beams
for p in range(2):
    beam = p + 1
    for l in range(len(f_set_list)):
        f_set = f_set_list[l]

        # find all measurement files
        find_measFiles(filePath, 'OP', beam)

        fig, axs = plt.subplots(1, 1, figsize=(20, 10))
        stat_TLM_median_log = []
        y_gain_log = []
        tlm_log = []

        for k in range(len(measFiles) - measFileShift):

            # load measurement file
            if '_4' in measFiles[k]:  # Check for specific conditions to load files
                load_measFiles(measFiles[k])
                print('-------------------------------------')
                print(meas_params['date time'][1:])
                print(meas_params['barcodes'])
                print('Temperature = ' + meas_params['Temp. [°C]'])
                print('-------------------------------------')

                # plot
                if '.' in meas_params['acu_version']:
                    plot__gainVport(f_set, measType)
                    # colate data
                    if loaded == True:
                        stat_TLM_median_log.append(stat_TLM_median)
                        y_gain_log.append(y_gain)
                        tlm_log.append(meas_params['barcodes'])

        # Generate a unique color for each plot
        plot_color = colours[l % len(colours)]

        # Plot mask
        import_mask(f_set, mask, 0.0)
        mask_lim = 10.0
        mask_offset = np.median(np.array(stat_TLM_median_log)) - np.median(np.array(mask_gain))
        axs.plot(np.linspace(1, len(mask_gain), num=len(mask_gain)), mask_gain + mask_offset, color=plot_color, alpha=0.5)
        axs.fill_between(np.linspace(1, len(mask_gain), num=len(mask_gain)), mask_gain + mask_offset - mask_lim,
                         mask_gain + mask_offset + mask_lim, color=plot_color, alpha=0.2)

        # Check mask deviation
        for jj in range(len(y_gain_log)):
            delta = y_gain_log[jj] - (mask_gain + mask_offset)
            if max(abs(delta)) > mask_lim:
                print(tlm_log[jj])
                for i in range(len(delta)):
                    if abs(delta[i]) > mask_lim:
                        axs.plot(i + 1, y_gain_log[jj][i], 'ro', markersize=2)

        # Plot histogram
        ymax1 = 25.0

        # Format plot
        axs.set_title(measType + ': ' + str(f_set) + ' GHz, Beam ' + str(beam) + ', ' + str(temperature) + ' degC')
        axs.set_xlabel('Port')
        axs.set_ylabel('S$_{21}$ [dB]')
        axs.set_xlim([1, len(y) + 1])
        axs.set_ylim([-30, 50])
        axs.axhline(y=droppedThresh, color="red", linestyle='--')
        axs.grid('on')
        plt.tight_layout()

        # Save plot
        fileName = measType + '_f-set' + str(f_set) + '_b' + str(beam) + '.png'
        newPath = os.path.join(filePath, SaveFileName)
        if not os.path.exists(newPath):
            os.makedirs(newPath)
        plt.savefig(os.path.join(newPath, fileName), dpi=200)

# ... (copy selected files to an external folder)

print("Done")
