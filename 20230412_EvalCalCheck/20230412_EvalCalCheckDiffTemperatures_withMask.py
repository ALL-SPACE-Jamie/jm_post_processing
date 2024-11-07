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
tlmType = 'Rx'
Type = '0267'
Drop_level = -10
Add_mean_sigma = '0N'
measType = 'Calibration'
filePath = r'C:\Users\RyanFairclough\Downloads\P18_Assembly'
SaveFileName = '\Post_Processed_Data_OP_iteration_Replace_op/'
port_Label = 'ON'
BoardFont = '6'
counter = 0
Dropped_Port_indentifier ='ON'
mask_lim_variable = []
external_folder_name = "Figures\\StressTest\\MCR1_Rig1"
measFileShift = 0
droppedThresh = 0
Exempt_Folder = 'combiner'
Exempt_Folder2 = 'Spare'
file_type = 'OP'
mask_status = 'ON'
Regression_comparison = 'OFF'

# frequencies to iterate through
if tlmType == 'Tx':
    mask_lim_variable = [7]
if tlmType == 'Rx':
    mask_lim_variable = [5]
if measType == 'Evaluation' and tlmType == 'Tx':
    f_set_list = [29.5]
    droppedThreshList = [droppedThresh]
elif measType == 'Calibration' and tlmType == 'Tx':
    f_set_list = [ 28.0, 28.5, 29.0,29.5, 30.0, 30.5, 31.0]
    droppedThreshList = [3, 10, 10, 7, 7, 7, 7, 0]
elif measType == 'Evaluation' and tlmType == 'Rx':
    f_set_list = [19.20]#[17.70, 18.20, 18.70, 19.20, 19.70, 20.20, 20.70, 21.20]
    droppedThreshList = [droppedThresh]
elif measType == 'Calibration' and tlmType == 'Rx':
    f_set_list = [17.70, 18.20, 18.70, 19.20, 19.70, 20.20, 20.70, 21.20]
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
        if fileString in file and 'eam' + str(beam) in file and (Exempt_Folder not in file and Exempt_Folder2 not in file and 'Fail' not in file):
            measFiles.append(file)

#def find_measFiles(path, fileString, beam):
    #global measFiles, files
    #files = []
    #for root, directories, file in os.walk(path):
        #for file in file:
            #if (file.endswith(".csv")) == True:
                #files.append(os.path.join(root, file))
    #measFiles = []
    #for i in range(len(files)):
        #if fileString in files[i] and 'eam' + str(beam) in files[i] and (Exempt_Folder not in files[i] and Exempt_Folder2 not in files[i]):
            #measFiles.append(files[i])


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

new_gasket = []
rtv = []
rtv_phase =[]
new_gasket_phase =[]
def plot__gainVport(f_set, measType):
    global y, stat_TLM_median, loaded, y_gain, paramName, mask_gain, rfic, rtv, new_gasket, rtv_phase,new_gasket_phase
    fig.suptitle(measType + ': ' + str(f_set) + ' GHz, Beam ' + str(beam) + ', ' + str(temperature) + ' degC',
                 fontsize=25)

    prev_stat_TLM = None
    if float(meas_params['f_c']) == f_set and len(meas_array) > 2:

        # array
        col = int(np.where(meas_frequencies == f_set)[0][0] * 2)
        y = meas_array[:, col]
        y_gain = y * 1.0



        # stats
        stat_TLM_median = np.median(y)
        stat_TLM_median_log.append(stat_TLM_median)
        barcode_num.append(meas_params['barcodes'])
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

        Gasket_y = []
        if 'Gasket' in meas_params['barcodes']:
            Gasket_y.append(np.array(y))
            Gasket_y_stacked = np.vstack(Gasket_y)
            Gasket_y_mean = np.mean(Gasket_y_stacked, axis=0)

            #axs[0, 0].plot(np.linspace(1, len(y), num=len(y)), y, 'b', alpha=0.2)
            #----change back to original y value if needed----- axs[0, 0].plot(np.linspace(1, len(y), num=len(y)), y, 'b', alpha=0.2)
            axs[0, 0].plot(np.linspace(1, len(y), num=len(y)), y, 'b', alpha=0.2)
            axs[0,0].text(120, 40, 'Algo2_V4', color = 'blue',fontsize = 5)
        if '00133' in meas_params['barcodes']:
            axs[0, 0].plot(np.linspace(1, len(y), num=len(y)), y, 'b', alpha=0.2)
            axs[0,0].text(80, 40, 'Algo2_V4', color = 'blue',fontsize = 5)
        elif '00099' in meas_params['barcodes']:
            axs[0, 0].plot(np.linspace(1, len(y), num=len(y)), y, 'y', alpha=0.2)
            axs[0, 0].text(40, 40, 'Algo1_V3', color='yellow', fontsize=5)
        elif 'rig1' in meas_params['barcodes']:
            axs[0, 0].plot(np.linspace(1, len(y), num=len(y)), y, 'r', alpha=0.2)
            axs[0, 0].text(0, 40, 'rtv', color='red', fontsize=5)
            rtv = np.append(rtv, y)
        elif '00004' in meas_params['barcodes']:
            axs[0, 0].plot(np.linspace(1, len(y), num=len(y)), y, 'r', alpha=0.2)
            axs[0, 0].text(0, 40, 'Algo2_V4_initial', color='red', fontsize=5)
        else:
            axs[0, 0].plot(np.linspace(1, len(y), num=len(y)), y, 'k', alpha=0.2)
            new_gasket = np.append(new_gasket, y)


        axs[0, 0].set_xlabel('port')
        axs[0, 0].set_ylabel('S$_{21}$ [dB]')
        axs[0, 0].set_xticks([0.5 * int(len(y) / 3), 1 * int(len(y) / 3), 1.5 * int(len(y) / 3),  2 * int(len(y) / 3), 2.5 * int(len(y) / 3), 3 * int(len(y) / 3)])
        axs[0, 0].set_xlim([1, len(y) + 1])
        axs[0, 0].set_ylim([minY, maxY])
        axs[0, 0].grid('on')

        #if file_type == 'OP':
            #axs[0, 0].axhline(y=droppedThresh, color="red", linestyle='--')
        #else:
            #print('xxxxx:',file_type)
        # plot 2
        axs[0, 1].plot(dataSetLabel, stat_l1_median, 'rs')
        axs[0, 1].plot(dataSetLabel, stat_l2_median, 'g^')
        axs[0, 1].plot(dataSetLabel, stat_l3_median, 'bP')
        if 'Gasket' in meas_params['barcodes']:
            axs[0, 1].plot(dataSetLabel, stat_TLM_median, 'bX', markersize=10)
        elif '00133' in meas_params['barcodes']:
            axs[0, 1].plot(dataSetLabel, stat_TLM_median, 'bX', markersize=10)
            axs[0, 1].text(dataSetLabel, stat_TLM_median + 10, 'Old_Lens', fontsize = 5)
        elif '00099' in meas_params['barcodes']:
            axs[0, 1].plot(dataSetLabel, stat_TLM_median, 'yX', markersize=10)
            axs[0, 1].text(dataSetLabel, stat_TLM_median + 10, 'Bare-Board', fontsize=5)
        elif '00003' in meas_params['barcodes']:
            axs[0, 1].plot(dataSetLabel, stat_TLM_median, 'rX', markersize=10)
            axs[0, 1].text(dataSetLabel, stat_TLM_median + 10, 'Algo2_V4_initial', fontsize=5)
        elif 'rig1' in meas_params['barcodes']:
            axs[0, 1].plot(dataSetLabel, stat_TLM_median, 'rX', markersize=10)
            axs[0, 1].text(dataSetLabel, stat_TLM_median + 10, 'rtv', fontsize=5)
        else:
            axs[0, 1].plot(dataSetLabel, stat_TLM_median, 'kX', markersize=10)
            axs[0, 1].text(dataSetLabel, stat_TLM_median + 10, 'New_Lens', fontsize=5)
        rounded = round(stat_TLM_median,1)
        axs[0, 1].text(dataSetLabel,stat_TLM_median + 5, rounded, fontsize=3 )

        #with open(r'C:\Users\RyanFairclough\Downloads\Failed_Evals\Gain_+_SerialNo.csv', mode='w') as file:
         #   writer = csv.writer(file)
           # writer.writerow(['Serial_Number', 'Median_Gain'])
          #  for value in barcode_num:
            #    writer.writerow([value])
            #for value in stat_TLM_median_log:
             #   writer.writerow(['', value])

        axs[0, 1].set_xlabel('board')
        axs[0, 1].set_ylabel('Median [dB]')
        axs[0, 1].tick_params(axis='x', labelrotation=90, labelsize=BoardFont)
        axs[0, 1].set_ylim([minY, maxY])
        axs[0, 1].grid('on')
        # plot 3
        axs[1, 1].plot(dataSetLabel, stat_l1_std, 'rs')
        axs[1, 1].plot(dataSetLabel, stat_l2_std, 'g^')
        axs[1, 1].plot(dataSetLabel, stat_l3_std, 'bP')
        axs[1, 1].plot(dataSetLabel, stat_TLM_std, 'kX', markersize=10)
        axs[1, 1].set_xlabel('board')
        axs[1, 1].set_ylabel('$\sigma$ [dB]')
        axs[1, 1].tick_params(axis='x', labelrotation=90, labelsize=BoardFont)
        axs[1, 1].set_ylim([0, 20])
        axs[1, 1].grid('on')
        # plot 4
        if stat_l1_dropped + stat_l2_dropped + stat_l3_dropped > 50:
            axs[2, 1].plot(dataSetLabel, 5.0, 'rX', markersize=30)
        axs[2, 1].plot(dataSetLabel, stat_l1_dropped, 'rs')
        axs[2, 1].plot(dataSetLabel, stat_l2_dropped, 'g^')
        axs[2, 1].plot(dataSetLabel, stat_l3_dropped, 'bP')
        axs[2, 1].set_xlabel('board')
        axs[2, 1].set_ylabel('Number of dropped ports (gain < ' + str(droppedThresh) + ' dB)')
        axs[2, 1].text(dataSetLabel, 2.0, log)  # bug
        axs[2, 1].tick_params(axis='x', labelrotation=90, labelsize=BoardFont)
        axs[2, 1].set_ylim([0, 10])
        axs[2, 1].grid('on')
        # plot 5
        y = meas_array[:, col + 1]
        minY = -90
        maxY = 360 + 45
        axs[1, 0].vlines(int(len(y) / 3), minY, maxY, 'k', alpha=0.2)
        axs[1, 0].vlines(2 * int(len(y) / 3), minY, maxY, 'k', alpha=0.2)
        #axs[1, 0].text(0.8 * int(len(y) / 6), minY + 35, 'Lens 1', backgroundcolor='r', fontsize=20)
        #axs[1, 0].text(2.8 * int(len(y) / 6), minY + 35, 'Lens 2', backgroundcolor='g', fontsize=20)
        #axs[1, 0].text(4.8 * int(len(y) / 6), minY + 35, 'Lens 3', backgroundcolor='b', fontsize=20)
        axs[1, 0].plot(np.linspace(1, len(y), num=len(y)), y, 'k', alpha=0.2)
        if 'rig1' in meas_params['barcodes']:
            axs[1, 0].plot(np.linspace(1, len(y), num=len(y)), y, 'r', alpha=0.2)
            axs[1, 0].text(0, 40, 'rtv', color='red', fontsize=5)
            rtv_phase = np.append(rtv_phase, y)
        else:
            axs[1, 0].plot(np.linspace(1, len(y), num=len(y)), y, 'k', alpha=0.2)
            new_gasket_phase = np.append(new_gasket_phase, y)
        axs[1, 0].set_xlabel('port')
        axs[1, 0].set_ylabel('Phase [deg]')
        axs[1, 0].set_xlim([1, len(y) + 1])
        axs[1, 0].set_ylim([minY, maxY])
        axs[1, 0].set_yticks(np.linspace(0, 360, num=int(360 / 45) + 1))
        axs[1, 0].set_xticks([0.5 * int(len(y) / 3), 1 * int(len(y) / 3), 1.5 * int(len(y) / 3), 2 * int(len(y) / 3),2.5 * int(len(y) / 3), 3 * int(len(y) / 3)])
        axs[1, 0].grid('on')

        # out
        loaded = True
    else:
        loaded = False

all_barcodes =[]
mean_list = []
sigma_list = []
beam_list =[]
previous_f_set = None
new_gasket = np.array([])
# run
for p in range(2):
    beam =  p + 1

    for l in range(len(f_set_list)):
        f_set = f_set_list[l]
        droppedThresh = droppedThreshList[l]

        if beam == 1 and f_set != previous_f_set:
            new_gasket= np.array([])
            new_gasket_phase = np.array([])
        if beam == 1 and f_set != previous_f_set:
            rtv = np.array([])
            rtv_phase = np.array([])
        if beam == 2 and f_set != previous_f_set:
            new_gasket= np.array([])
            new_gasket_phase = np.array([])
        if beam == 2 and f_set != previous_f_set:
            rtv = np.array([])
            rtv_phase = np.array([])

        previous_f_set = f_set

        # find all meas files
        find_measFiles(filePath, file_type, beam)

        fig, axs = plt.subplots(3, 2, figsize=(25, 15))
        stat_TLM_median_log = []
        barcode_num =[]
        y_gain_log = []
        tlm_log = []

        for k in range(len(measFiles) - measFileShift):
            #print(range(len(files)))
            # load meas file
            if '_4' in measFiles[k]:  # if str(temperature) + 'C' in measFiles[k]:
                load_measFiles(measFiles[k])
                #print('-------------------------------------')
                #print(meas_params['date time'][1:])
                #print(meas_params['barcodes'])
                #print('Temperature = ' + meas_params['Temp. [°C]'])
                #print('-------------------------------------')
                #for i in range(len(meas_params['barcodes'])):
                    #print('DDDDDD:',i)

                # plot
                if '.' in meas_params['acu_version']:
                    plot__gainVport(f_set, measType)
                    # colate
                    if loaded == True:
                        y_gain_log.append(y_gain)
                        tlm_log.append(meas_params['barcodes'])
                        all_barcodes.append(meas_params['barcodes'])#
                        list(set(all_barcodes))
                        all_barcodes.sort()
                        print(all_barcodes)

        # mask
        import_mask(f_set, mask, 0.0)
        mask_lim = mask_lim_variable
        mask_offset = np.median(np.array(stat_TLM_median_log)) - np.median(np.array(mask_gain))
        if mask_status == 'ON':
            axs[0, 0].plot(np.linspace(1, len(mask_gain), num=len(mask_gain)), mask_gain + mask_offset, 'g-', alpha=0.5)
            axs[0, 0].fill_between(np.linspace(1, len(mask_gain), num=len(mask_gain)), mask_gain + mask_offset - mask_lim,mask_gain + mask_offset + mask_lim, color='green', alpha=0.2)
        else:
            print('MASK_OFF')
        #print(mask_gain + mask_offse


        # plot histogram
        ymax1 = 25.0
        mean = np.mean(np.array(stat_TLM_median_log))

        axs[2, 0].hist(np.array(stat_TLM_median_log), bins=11)
        axs[2, 0].set_xlabel('TLM median [dB]')
        axs[2, 0].set_ylabel('count')
        axs[2, 0].set_xlim([mean - 5, mean + 5])
        axs[2, 0].set_ylim([0, 25])
        axs[2, 0].axvline(mean, ymin=0.0, ymax=ymax1, color='k')
        axs[2, 0].grid('on')
        variance = np.var(np.array(stat_TLM_median_log))
        sigma = np.sqrt(variance)
        x = np.linspace(-50, 50, 10001)
        axs[2, 0].plot(x, ymax1 * norm.pdf(x, mean, sigma) / (max(norm.pdf(x, mean, sigma))), 'r')
        axs[2, 0].text(mean + 0.1, 10.25, str(round(mean, 2)) + ' dB ($\sigma$ = ' + str(round(sigma, 1)) + ')',rotation=90)
        mean_list.append(mean)
        sigma_list.append(sigma)
        beam_list.append(beam)
        Average_mean_across_all_freq = sum(mean_list) / 16
        Average_sigma = sum(sigma_list) / 16
        Terminal_Score = Average_mean_across_all_freq / Average_sigma
        #print('mean_list', mean_list)
        #print('sigma_List', sigma_list)
        data = {'Mean': mean_list,
                'Sigma': sigma_list,
                'Beam': beam_list,
                'Average_mean_across_all_freq': Average_mean_across_all_freq,
                'Terminal_Score': Terminal_Score}
        #print(f_set_list*2)

        df = pd.DataFrame(data)
        #print(df)

        # mask_check
        tlm_numbers = []
        for jj in range(len(y_gain_log)):
         delta = y_gain_log[jj] - (mask_gain + mask_offset)
         if max(abs(delta)) > mask_lim:
                print('TLMs_in_List:',tlm_log[jj])
                for k in range(len(tlm_log)):
                    tlm_numbers.append(len(tlm_log))
                    tlm_numbers = list(set(tlm_numbers))

                    axs[0,1].text(0,stat_TLM_median - 35, 'Total_Number_of_TLMs: ' + str(tlm_numbers))
                    median_of_all_TLMs = np.median(stat_TLM_median_log)
                    axs[0, 1].axhline(y=median_of_all_TLMs)
                    axs[0,1].text(0,stat_TLM_median - 25,'Median_of_all_TLMs:' + str(median_of_all_TLMs))


                ports_dropped = []
                for i in range(len(delta)):
                    if abs(delta[i]) > mask_lim:
                        if Dropped_Port_indentifier == 'ON':
                            less_than_5 = y_gain_log[jj][i] <= Drop_level
                            if less_than_5:
                                axs[0, 0].plot(i + 1, y_gain_log[jj][i], 'ro', markersize=1)
                                if port_Label == 'ON':
                                    if y_gain_log[jj][i] <= Drop_level:
                                       Test = axs[0, 0].text(i + 1, y_gain_log[jj][i], str(tlm_log[jj]) + ': port ' + str(i + 1), fontsize=5)
                                       #print(Test)
                                       ports_dropped.append(str(i + 1))
                        else:
                            axs[0, 0].plot(i + 1, y_gain_log[jj][i], 'ro', markersize=1)
                            if port_Label == 'ON':
                                axs[0, 0].text(i + 1, y_gain_log[jj][i],str(tlm_log[jj]) + ': port ' + str(i + 1), fontsize=5)

                        #axs[0,0].gcf().gca().add_artist(plt.Circle(i+1, y_gain_log[jj][i], radius = 1, edgecolor='red', facecolor=0.5))

        if Regression_comparison == 'ON':
            rtv = np.squeeze(rtv)
            new_gasket = np.squeeze(new_gasket)
            rtv_phase = np.squeeze(rtv_phase)
            new_gasket_phase = np.squeeze(new_gasket_phase)
            axs[0, 0].plot(np.linspace(1, len(y), num=len(y)), new_gasket - rtv, 'b', alpha=0.2)
            axs[0, 0].text(10, 5, 'Amplitude_Difference',color= 'blue',fontsize=6)
            axs[1, 0].plot(np.linspace(1, len(y), num=len(y)), new_gasket_phase - rtv_phase, 'b', alpha=0.2)
            axs[1, 0].text(10, 5, 'Phase_Difference', color='blue', fontsize=6)
        else:
            print('Regression_comparison_off')


        barcodes = []


        #with open(r'C:\Users\RyanFairclough\Downloads\Dropped_ports\ports_dropped.csv', mode='w') as file:
        #    writer = csv.writer(file)
        #    writer.writerow(['Dropped_Ports_RFIC_Fault'])
        #    for port in ports_dropped:
        #        writer.writerow([port])
                #print('dropped_ports',ports_dropped)


        with open('S2000_TX_RFIC_PORT_MAP.json') as json_file:
            S2000_TX_RFIC_PORT_MAP = json.load(json_file)
        with open('rx_s2000_rfic_map.json') as json_file:
            rx_s2000_rfic_map = json.load(json_file)

        lens1 = []
        lens2 =[]
        lens3 =[]
        for port in ports_dropped:
            if tlmType == 'Rx' and int(port) <= 96:
                result = int(port)
                #print('Lens_1:\n',result)
                lens1.append(result)
                #print("Lens1:",lens1)
            elif tlmType == 'Rx' and 96 <= int(port) <= 192:
                result1 = int(port) - 96
                #print('Lens_2:\n',result1)
                #print("Lens2:",lens2)
                lens2.append(result1)
            elif tlmType == 'Rx' and 192 < int(port) < 288:
                result2 = int(port) - 192
                #print('Lens_3:\n',result2)
                lens3.append(result2)
                #print("Lens3:",lens3)   ######------------------Fix Below here-------------------
        if beam == 1:
            Beam1_drops = "Lens1:" + str(lens1) + "  Lens2:" + str(lens2) + "  Lens3:" + str(lens3)

            #print(Beam1_drops)
        elif beam == 2:
            Beam2_drops = "Lens1:" + str(lens1) + "  Lens2:" + str(lens2) + "  Lens3:" + str(lens3)

        lst = []
        rfic_list = []
        appended_values = set()   #At the moment it is manual to display each lenses dropped ports, integrate this so it can see all lenses.
        append_rfic_val = set()

        for key in sorted(rx_s2000_rfic_map.keys(), key=lambda x: int(x)):
            if 1 <= int(key) <= 12:
                for value in lens1:
                    if value not in appended_values:
                        lst.append(value)
                        appended_values.add(value)
                for val in rx_s2000_rfic_map[key]:
                    rfic_list.append(val)
                    append_rfic_val.add(val)

        #print(rfic_list)
        #print('----',lst)
        Common_val = set(lst) & set(rfic_list)
        #print('xxx',Common_val)
        for key in rx_s2000_rfic_map.keys():
            if any(common_value in rx_s2000_rfic_map[key] for common_value in Common_val):
                print(key) #### Only gives 1 lens at a time, need to change so it provides all.


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
#print("Done.")

if Add_mean_sigma == '0N':
    index = ['27.5', '28.0','28.5','29.0', '29.5', '30.0', '30.5', '31.0','27.5', '28.0','28.5','29.0', '29.5', '30.0', '30.5', '31.0']
    df = pd.DataFrame(data,index=index)
    df.index.name = 'Frequency'
    df.to_csv(os.path.join(filePath,r"Mean_Sigma.csv"))
else:
    print('finish')

