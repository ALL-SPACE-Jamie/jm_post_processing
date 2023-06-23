import pandas as pd
import numpy as np
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

temperature = '45'
tlmType = 'Tx'
measType = 'Calibration' #'Calibration'  # 'Calibration' or 'Evaluation'
filePath = r'C:\Users\JamieMitchell\OneDrive - ALL.SPACE\S-Type\Rx_TLM\ES2c-Laser_Cut\TLM_Evaluation_Measurements\All_Boards'
filePath = r'C:\Users\JamieMitchell\OneDrive - ALL.SPACE\S-Type\Tx_TLM\ES2\TLM_Calibration_Measurements\Tx_Batch_1'
SaveFileName = '\Post_Processed_Data'
BoardFont = '10'
counter = 0
external_folder_name = "Figures"
measFileShift = 0
droppedThresh = -5


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
        if fileString in files[i] and 'eam' + str(beam) in files[i]:
            measFiles.append(files[i])
    # print(measFiles)


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

    # meas_params
    for i in range(len(meas_info) - 1):
        if len(meas_info[i]) > 1:
            paramName = meas_info[i][0]

            if paramName[0:2] == '# ':
                paramName = paramName[2:]
            meas_params[paramName] = meas_info[i][1]


def plot__gainVport(f_set, measType):
    global y, stat_TLM_median, loaded
    fig.suptitle(measType + ': ' + str(f_set) + ' GHz, Beam ' + str(beam) + ', ' + str(temperature) + ' degC',
                 fontsize=25)
    if float(meas_params['f_c']) == f_set and len(meas_array) > 2:
        print('Plotting')
        # array
        col = int(np.where(meas_frequencies == f_set)[0][0] * 2)
        y = meas_array[:, col]
        
        # stats
        stat_TLM_median = np.median(y)
        stat_TLM_median_log.append(stat_TLM_median)
        stat_l1_median = np.median(y[0:int(len(y) / 3)])
        stat_l2_median = np.median(y[int(len(y) / 3):2 * int(len(y) / 3)])
        stat_l3_median = np.median(y[2 * int(len(y) / 3):3 * int(len(y) / 3)])
        stat_l1_dropped = ((y[0:int(len(y) / 3)]) < droppedThresh).sum()
        stat_l2_dropped = ((y[int(len(y) / 3):2 * int(len(y) / 3)]) < -20).sum()
        stat_l3_dropped = ((y[2 * int(len(y) / 3):3 * int(len(y) / 3)]) < -20).sum()
        stat_TLM_std = np.std(y, dtype=np.float64) ##
        print(stat_l1_median)
        print(stat_l2_median)
        print(stat_l3_median)

        stat_l1_std = np.std(y[0:int(len(y) / 3)])
        stat_l2_std = np.std(y[int(len(y) / 3):2 * int(len(y) / 3)])
        stat_l3_std = np.std(y[2 * int(len(y) / 3):3 * int(len(y) / 3)])

        # plot 1
        minY = -30
        maxY = 50
        axs[0, 0].vlines(int(len(y) / 3), minY, maxY, 'k', alpha=0.2)
        axs[0, 0].vlines(2 * int(len(y) / 3), minY, maxY, 'k', alpha=0.2)
        axs[0, 0].text(0.8 * int(len(y) / 6), minY + 5, 'Lens 1', backgroundcolor='r', fontsize=20)
        axs[0, 0].text(2.8 * int(len(y) / 6), minY + 5, 'Lens 2', backgroundcolor='g', fontsize=20)
        axs[0, 0].text(4.8 * int(len(y) / 6), minY + 5, 'Lens 3', backgroundcolor='b', fontsize=20)
        axs[0, 0].plot(np.linspace(1, len(y) + 1, num=len(y)), y, 'k', alpha=0.2)
        axs[0, 0].set_xlabel('port')
        axs[0, 0].set_ylabel('S$_{21}$ [dB]')
        axs[0, 0].set_xlim([1, len(y) + 1])
        axs[0, 0].set_ylim([minY, maxY])
        axs[0, 0].grid('on')
        # plot 2
        axs[0, 1].plot(meas_params['lens type (rx/tx)'] + meas_params['barcodes'], stat_l1_median, 'rs')
        axs[0, 1].plot(meas_params['lens type (rx/tx)'] + meas_params['barcodes'], stat_l2_median, 'g^')
        axs[0, 1].plot(meas_params['lens type (rx/tx)'] + meas_params['barcodes'], stat_l3_median, 'bP')
        axs[0, 1].plot(meas_params['lens type (rx/tx)'] + meas_params['barcodes'], stat_TLM_median, 'kX', markersize=10)
        axs[0, 1].set_xlabel('board')
        axs[0, 1].set_ylabel('Median [dB]')
        axs[0, 1].tick_params(axis='x', labelrotation=90, labelsize=BoardFont)
        axs[0, 1].set_ylim([minY, maxY])
        axs[0, 1].grid('on')
        # plot 3
        axs[1, 1].plot(meas_params['lens type (rx/tx)'] + meas_params['barcodes'], stat_l1_std, 'rs')
        axs[1, 1].plot(meas_params['lens type (rx/tx)'] + meas_params['barcodes'], stat_l2_std, 'g^')
        axs[1, 1].plot(meas_params['lens type (rx/tx)'] + meas_params['barcodes'], stat_l3_std, 'bP')
        axs[1, 1].plot(meas_params['lens type (rx/tx)'] + meas_params['barcodes'], stat_TLM_std, 'kX', markersize=10)
        axs[1, 1].set_xlabel('board')
        axs[1, 1].set_ylabel('$\sigma$ [dB]')
        axs[1, 1].tick_params(axis='x', labelrotation=90, labelsize=BoardFont)
        axs[1, 1].set_ylim([0, 20])
        axs[1, 1].grid('on')
        # plot 4
        if stat_l1_dropped + stat_l2_dropped + stat_l3_dropped > 50:
            axs[2, 1].plot(meas_params['lens type (rx/tx)'] + meas_params['barcodes'], 50.0,
                           'r*', markersize=15)
            
        axs[2, 1].plot(meas_params['lens type (rx/tx)'] + meas_params['barcodes'], stat_l1_dropped,
                       'rs')
        axs[2, 1].plot(meas_params['lens type (rx/tx)'] + meas_params['barcodes'], stat_l2_dropped,
                       'g^')
        axs[2, 1].plot(meas_params['lens type (rx/tx)'] + meas_params['barcodes'], stat_l3_dropped,
                       'bP')
        axs[2, 1].set_xlabel('board')
        axs[2, 1].set_ylabel('Number of dropped ports (gain < ' + str(droppedThresh) + ' dB)')
        axs[2, 1].tick_params(axis='x', labelrotation=90, labelsize=BoardFont)
        axs[2, 1].set_ylim([0, 50])
        axs[2, 1].grid('on')

        # plot 5
        y = meas_array[:, col + 1]
        minY = -90
        maxY = 360 + 45
        axs[1, 0].vlines(int(len(y) / 3), minY, maxY, 'k', alpha=0.2)
        axs[1, 0].vlines(2 * int(len(y) / 3), minY, maxY, 'k', alpha=0.2)
        axs[1, 0].text(0.8 * int(len(y) / 6), minY + 35, 'Lens 1', backgroundcolor='r', fontsize=20)
        axs[1, 0].text(2.8 * int(len(y) / 6), minY + 35, 'Lens 2', backgroundcolor='g', fontsize=20)
        axs[1, 0].text(4.8 * int(len(y) / 6), minY + 35, 'Lens 3', backgroundcolor='b', fontsize=20)
        axs[1, 0].plot(np.linspace(1, len(y) + 1, num=len(y)), y, 'k', alpha=0.2)
        axs[1, 0].set_xlabel('port')
        axs[1, 0].set_ylabel('Phase [deg]')
        axs[1, 0].set_xlim([1, len(y) + 1])
        axs[1, 0].set_ylim([minY, maxY])
        axs[1, 0].set_yticks(np.linspace(0, 360, num=int(360 / 45) + 1))
        axs[1, 0].grid('on')

        # out
        loaded = True
    else:
        loaded = False


## RUN ##

if measType == 'Evaluation' and tlmType == 'Tx':
    f_set_list = [29.5]
elif measType == 'Calibration' and tlmType == 'Tx':
    f_set_list = [29.5, 28.0, 28.5, 29.0, 29.5, 30.0, 30.5, 31.0]
elif measType == 'Evaluation' and tlmType == 'Rx':
    f_set_list = [19.2]
elif measType == 'Calibration' and tlmType == 'Rx':
    f_set_list = [17.7, 18.2, 18.7, 19.2, 19.7, 20.2, 20.7, 21.2]

# run
for p in range(2):
    beam = p + 1
    for l in range(len(f_set_list)):
        f_set = f_set_list[l]

        # find all meas files
        find_measFiles(filePath, 'OP', beam)

        fig, axs = plt.subplots(3, 2, figsize=(25, 15))
        stat_TLM_median_log = []
        for k in range(len(measFiles)-measFileShift):

            # load meas file
            if '_' + temperature + 'C' in measFiles[
                k]:  # str(temperature) + 'C' in measFiles[k]:# and 'teration_1' in measFiles[k]:
                load_measFiles(measFiles[k])
                print(meas_params['barcodes'])

                # plot
                plot__gainVport(f_set, measType)
                # colate
                if loaded == True:
                    stat_TLM_median_log.append(stat_TLM_median)
                    print(stat_TLM_median)
                    print('Added to plot')
        # plot histogram
        ymax1 = 25.0

        mean = np.mean(np.array(stat_TLM_median_log))
        print(stat_TLM_median_log)

        # print(measFiles)
        axs[2, 0].hist(np.array(stat_TLM_median_log), bins=11)
        axs[2, 0].set_xlabel('TLM median [dB]')
        axs[2, 0].set_ylabel('count')
        axs[2, 0].set_xlim([mean - 5, mean + 5])
        axs[2, 0].set_ylim([0, 25])
        axs[2, 0].axvline(mean, ymin=0.0, ymax=ymax1, color='k')
        axs[2, 0].text(mean + 0.1, 10.25, str(round(mean, 2)) + ' dB', rotation=90)
        axs[2, 0].grid('on')
        variance = np.var(np.array(stat_TLM_median_log))
        sigma = np.sqrt(variance)
        x = np.linspace(-50, 50, 1001)
        axs[2, 0].plot(x, ymax1 * norm.pdf(x, mean, sigma) / (max(norm.pdf(x, mean, sigma))), 'r')

        # format
        plt.tight_layout()

        # save
        fileName = measType + '_f-set' + str(f_set) + '_b' + str(beam) + '.png'
        newPath = filePath + SaveFileName
        print(newPath)
        if not os.path.exists(newPath):
            os.makedirs(newPath)
        plt.savefig(newPath + '/' + fileName, dpi=200)

external_path = os.path.join(filePath, external_folder_name)
os.makedirs(external_path, exist_ok=True) #The path of the external folder

for dirpath, dirnames, filenames in os.walk(filePath):
    for file in filenames:
        if file.lower().endswith('png'):
            try:
               file_path = os.path.join(dirpath, file)
               shutil.copy(file_path, external_path)
               print(f"Copied_file_path_to_external_path")
            except shutil.SameFileError as e:
                print(f"Skipped copying file{file}:{e}")
print("done")

