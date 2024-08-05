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
import re
# file path
dirScript = os.getcwd()

# parmas
temperature = '45'
tlmType = 'Tx'
Type = '0267'
Drop_level = -20
measType = 'Calibration'
filePath = r'C:\Users\RyanFairclough\Downloads\flat_lens_reboot'
SaveFileName = '\Post_Processed_Data_OP_iteration_1_Best_18_OP'
port_Label = 'OFF'
BoardFont = '6'
counter = 0
Dropped_Port_indentifier ='ON'
mask_lim_variable = []
external_folder_name = "Figures\\StressTest\\MCR1_Rig1"
measFileShift = 0
droppedThresh = 0
Exempt_Folder = 'combiner'
Exempt_Folder2 = 'Archive'
file_type = 'OP'
Mask = 'ON'


# frequencies to iterate through
if tlmType == 'Tx':
    mask_lim_variable = [5]
if tlmType == 'Rx':
    mask_lim_variable = [5]
if measType == 'Evaluation' and tlmType == 'Tx':
    f_set_list = [29.5]
    droppedThreshList = [droppedThresh]
elif measType == 'Calibration' and tlmType == 'Tx':
    f_set_list = [27.5]#[27.5, 28.0, 28.5, 29.0,29.5, 30.0, 30.5, 31.0]
    droppedThreshList = [3, 10, 10, 7, 7, 7, 7, 0]
elif measType == 'Evaluation' and tlmType == 'Rx':
    f_set_list = [19.20]#[17.70, 18.20, 18.70, 19.20, 19.70, 20.20, 20.70, 21.20]
    droppedThreshList = [droppedThresh]
elif measType == 'Calibration' and tlmType == 'Rx':
    f_set_list = [17.70, 18.20, 18.70,19.20, 19.70, 20.2, 20.7, 21.2]
    droppedThreshList = [10, 15, 15, 15, 15, 15, 15, 10]
if measType == 'Calibration' and tlmType == 'Tx':
    mask = os.path.join(dirScript,r'2023_09_22_Sweep_FF_calibration_data_LensA_Sim_HFSS_ES2iXS_perf_eval_stackup_Cluster_freq_change_sorted.csv') #2023_09_22_Sweep_FF_calibration_data_LensA_Sim_HFSS_ES2iXS_cal_equ_stackup_Cluster_freq_change_sorted, 2023_09_22_Sweep_FF_calibration_data_LensA_Sim_HFSS_ES2iXS_cal_equ_stackup_Cluster_freq_change_sorted
elif measType == 'Calibration' and tlmType == 'Rx':
    mask = os.path.join(dirScript,r'2023_10_31_discrete_17700_21200_8_calibration_data_175-0212_sanmina_rel1c_2023_09_01_v0_LensA_RX_default_cal_equ_sorted.csv') #2023_10_31_discrete_17700_21200_8_calibration_data_175-0212_sanmina_rel1c_2023_09_01_v0_LensA_RX_default_cal_equ_sorted, 2023_10_20_discrete_17700_21200_8_calibration_data_175-0200_dual_probe_cal_equ_sorted.csv ,2023_03_17_discrete_17700_21200_8_calibration_data_175-0081_sanmina_rel1c_2023_03_07_L1L14_48feed_calibration_13mm_dual_pol_probe_2
elif measType == 'Evaluation' and tlmType == 'Tx':
    mask = os.path.join(dirScript, r'2023_09_22_Sweep_FF_calibration_data_LensA_Sim_HFSS_ES2iXS_perf_eval_stackup_Cluster_freq_change_sorted.csv')
elif measType == 'Evaluation' and tlmType == 'Rx':
    mask = os.path.join(dirScript, r'2023_10_31_discrete_17700_21200_8_calibration_data_175-0212_sanmina_rel1c_2023_perf_eval_sorted.csv') #2023_10_31_discrete_17700_21200_8_calibration_data_175-0212_sanmina_rel1c_2023_perf_eval_sorted, 2023_03_16_discrete_17700_21200_8_calibration_data_175-0081_sanmina_rel1c_2023_03_07_L1L14_48feed_v10_performance_evaluation_250mm_dual_pol_probe.csv
# definitions
files = glob.glob(os.path.join(filePath,'*'))
sorted_files = sorted(files,key=lambda x: x[-5:])
for file in sorted_files:
    print(file)


def find_measFiles(path, fileString, beam):
    global measFiles, files
    files = []
    for root, directories, filenames in os.walk(path):
        for filename in filenames:
            if filename.endswith(".csv"):
                files.append(os.path.join(root, filename))
    measFiles = []
    for file in files:
        if fileString in file and 'eam' + str(beam) in file and (Exempt_Folder not in file and Exempt_Folder2 not in file and 'iteration_2' not in file):
            measFiles.append(file)



def import_mask(f_set, mask, offset):
    global mask_gain, mask_phase, mask_gain_cross
    meas_info = []
    meas_array = np.genfromtxt(mask, delimiter=',', skip_header=1)[:,2:]
    meas_array_frequencies = np.genfromtxt(mask, delimiter=',', skip_header=1)[0:int(len(meas_array)/2),1]
    index = np.argmin((meas_array_frequencies-float(f_set))**2)
    meas_arrayT = meas_array[index,:][::2]
    meas_arrayB = meas_array[int(len(meas_array)/2)+index,:][::2]
    meas_array_gain = np.zeros(len(meas_arrayT))
    meas_array_gain_cross = np.zeros(len(meas_arrayT))
    for i in range(int(len(meas_arrayT)/2)):
        meas_array_gain[2*i] = meas_arrayT[2*i]
        meas_array_gain[2*i+1] = meas_arrayB[2*i+1]
        meas_array_gain_cross[2*i] = meas_arrayT[2*i+1]
        meas_array_gain_cross[2*i+1] = meas_arrayB[2*i]
    meas_arrayT = meas_array[index,:][1:][::2]
    meas_arrayB = meas_array[int(len(meas_array)/2)+index,:][1:][::2]
    meas_array_phase = np.zeros(len(meas_arrayT))
    for i in range(int(len(meas_arrayT)/2)):
        meas_array_phase[2*i] = meas_arrayT[2*i]
        meas_array_phase[2*i+1] = meas_arrayB[2*i+1]
    mask_gain = meas_array_gain*1.0 + offset
    mask_gain_cross = meas_array_gain_cross*1.0 + offset
    for i in range(len(mask_gain)):
        if mask_gain_cross[i] > mask_gain[i]:
            mask_gain[i] = mask_gain_cross[i]*1.0
    mask_phase = meas_array_phase*1.0
    mask_gain = np.hstack([mask_gain, mask_gain, mask_gain])
    mask_phase = np.hstack([mask_phase, mask_phase, mask_phase])

def load_measFiles(filePath):
    global meas_info, meas_array, meas_frequencies, meas_params, mask_gain
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

y_diff =[]
y_list =[]
def plot__gainVport(f_set, measType):
    global y, stat_TLM_median, loaded, y_gain, paramName, mask_gain, rfic
    fig.suptitle(measType + ': ' + str(f_set) + ' GHz, Beam ' + str(beam) + ', ' + str(temperature) + ' degC',
                 fontsize=25)
    all_gain = []
    prev_stat_TLM = None
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
        import_mask(f_set, mask, 0.0)
        if tlmType == 'Tx':
            mask_l1 = mask_gain[:152]
            mask_l2 = mask_gain[152:304]
            mask_l3 = mask_gain[304:456]
        else:
            mask_l1 = mask_gain[:96]
            mask_l2 = mask_gain[96:192]
            mask_l3 = mask_gain[192:288]
        mask_offset = np.median(np.array(stat_TLM_median_log)) - np.median(np.array(mask_gain))
        mask_G_lens1 = mask_l1 + mask_offset
        mask_G_lens2 = mask_l2 + mask_offset
        mask_G_lens3 = mask_l3 + mask_offset
        mask_gain_lim1 = [item -5 for item in mask_G_lens1]
        mask_gain_lim3 = [item -5 for item in mask_G_lens2]
        mask_gain_lim5 = [item -5 for item in mask_G_lens3]
        stat_l1_dropped = ((y[0:int(len(y) / 3)] < mask_gain_lim1)).sum()
        stat_l1_dropped_list = ((y[0:int(len(y) / 3)]) < droppedThresh)
        stat_l2_dropped_list = ((y[int(len(y) / 3):2 * int(len(y) / 3)]) < droppedThresh)
        stat_l3_dropped_list = ((y[2 * int(len(y) / 3):3 * int(len(y) / 3)]) < droppedThresh)
        #print('11111111:',y[0:int(len(y) / 3)])
        #print(mask_gain)

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
        stat_l2_dropped = ((y[int(len(y) / 3):2 * int(len(y) / 3)]) < mask_gain_lim3).sum()
        stat_l3_dropped = ((y[2 * int(len(y) / 3):3 * int(len(y) / 3)]) < mask_gain_lim5).sum()
        stat_TLM_std = np.std(y, dtype=np.float64)  ##

        stat_l1_std = np.std(y[0:int(len(y) / 3)])
        stat_l2_std = np.std(y[int(len(y) / 3):2 * int(len(y) / 3)])
        stat_l3_std = np.std(y[2 * int(len(y) / 3):3 * int(len(y) / 3)])

        # plots
        dataSetLabel = meas_params['date time'] + '\n' + meas_params['lens type (rx/tx)'] + meas_params['barcodes'] + ', SW: ' + meas_params['acu_version'] + '\n ITCC: ' + meas_params['itcc_runner_version']

        # plot 1
        if tlmType == 'Rx':
            minY = -10
            maxY = 50
            yticks = np.arange(-30, 50, 5)
        if tlmType == 'Tx':
            minY = -20
            maxY = 30
            yticks = np.arange(-30, 31, 5)
        plt.vlines(int(len(y) / 3), minY, maxY, 'k', alpha=0.2)
        plt.vlines(2 * int(len(y) / 3), minY, maxY, 'k', alpha=0.2)
        plt.text(0.8 * int(len(y) / 6), minY + 5, 'Lens 1', backgroundcolor='r', fontsize=20)
        plt.text(2.8 * int(len(y) / 6), minY + 5, 'Lens 2', backgroundcolor='g', fontsize=20)
        plt.text(4.8 * int(len(y) / 6), minY + 5, 'Lens 3', backgroundcolor='b', fontsize=20)

        print(meas_params['barcodes'])

        if '1QQ' in meas_params['barcodes']:
            plt.plot(np.linspace(1, len(y), num=len(y)), y, 'r', alpha=0.2)
            y_diff.append(y)
        else:
             plt.plot(np.linspace(1, len(y), num=len(y)), y, 'k', alpha=0.2)
             y_list.append(y)

        plt.xlabel('port')
        plt.ylabel('S$_{21}$ [dB]')
        plt.xticks([0.5 * int(len(y) / 3), 1 * int(len(y) / 3), 1.5 * int(len(y) / 3),  2 * int(len(y) / 3), 2.5 * int(len(y) / 3), 3 * int(len(y) / 3)])
        plt.yticks(yticks)
        plt.xlim([1, len(y) + 1])
        plt.ylim([minY, maxY])
        plt.grid('on')

        loaded = True
    else:
        loaded = False

#run
for p in range(2):
    beam = p + 1
    for l in range(len(f_set_list)):
        f_set = f_set_list[l]


        # find all meas files
        find_measFiles(filePath, 'OP', beam)
        fig, ax = plt.subplots(figsize=(12, 8))
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

        dif = np.array(y_diff) - np.array(y_list)
        print(dif)
        plt.plot(np.linspace(1, len(y), num=len(y)), dif, 'b', alpha=0.2)

        # save
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