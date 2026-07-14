import re
from collections import OrderedDict
import pandas as pd
import numpy as np
import matplotlib.patches as patches
import matplotlib.pyplot as plt;
import statistics

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
import seaborn as sns

# file path
dirScript = os.getcwd()

# parmas
temperature = '45'
tlmType = 'Tx'
measType = 'Calibration'  # 'Calibration' or 'Evaluation'
filePath = r'C:\Users\RyanFairclough\Downloads\IFBW_-40_Tx'
SaveFileName = '\Post_Processed_Data'
BoardFont = '6'
counter = 0
external_folder_name = "Figures\\StressTest\\MCR1_Rig1"
measFileShift = 0
droppedThresh = -15
Exempt_Folder = 'combiner'



# frequencies to iterate through
if measType == 'Evaluation' and tlmType == 'Tx':
    f_set_list = [29.0]
    droppedThreshList = [droppedThresh]
elif measType == 'Calibration' and tlmType == 'Tx':
    f_set_list = [27.5, 28.0, 28.5, 29.0, 29.5, 30.0, 30.5, 31.0]#[27.5, 29.5, 31]
    droppedThreshList = [-15, -15, -11, -9, -15, -6, -15, -20]
elif measType == 'Evaluation' and tlmType == 'Rx':
    f_set_list = [19.2]
    droppedThreshList = [droppedThresh]
elif measType == 'Calibration' and tlmType == 'Rx':
    f_set_list = [17.7, 18.2, 18.7, 19.2, 19.7, 20.2, 20.7, 21.2]
    droppedThreshList = [10, 10, 15, 15, 15, 12, 12, -5]


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
total_seconds_changes = []
total_meas_ifbw =[]
def plot__gainVport(f_set, measType):
    global y, stat_TLM_median, loaded, y_gain, G_base, P_base
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
        stat_l2_dropped = ((y[int(len(y) / 3):2 * int(len(y) / 3)]) < droppedThresh).sum()
        stat_l3_dropped = ((y[2 * int(len(y) / 3):3 * int(len(y) / 3)]) < droppedThresh).sum()
        stat_TLM_std = np.std(y, dtype=np.float64)  ##

        stat_l1_std = np.std(y[0:int(len(y) / 3)])
        stat_l2_std = np.std(y[int(len(y) / 3):2 * int(len(y) / 3)])
        stat_l3_std = np.std(y[2 * int(len(y) / 3):3 * int(len(y) / 3)])
        meas_ifbw = int(float(meas_info[18][1]))
        print('IFBW=:', meas_ifbw)
        meas_date_time = (meas_info[2][1])
        meas_time = []
        meas_time.append(meas_date_time)
        time_part = meas_date_time.split(' ')[2]
        meas_time = time_part
        print('Time:',meas_time)
        hours, minutes, seconds = map(int, meas_time.split(':'))
        total_seconds = hours * 3600 + minutes * 60 + seconds
        if total_meas_ifbw and meas_ifbw != total_meas_ifbw [-1]:
            total_meas_ifbw.append(meas_ifbw)
        elif not total_meas_ifbw:
            total_meas_ifbw.append(meas_ifbw)
        if total_seconds_changes and total_seconds != total_seconds_changes[-1]:
            total_seconds_changes.append(total_seconds)
        elif not total_seconds_changes:
            total_seconds_changes.append(total_seconds)
        Num_ifbw = len(set(total_meas_ifbw))
        print('Number:',Num_ifbw)
        print("Total IFBW:", total_meas_ifbw)
        print("Total seconds:", total_seconds_changes)
        ifbw_dict = {}

        # Iterate through the data and populate the dictionary
        for ifbw, seconds in zip(total_meas_ifbw, total_seconds_changes):
            if ifbw not in ifbw_dict:
                ifbw_dict[ifbw] = []
            ifbw_dict[ifbw].append(seconds)

        # Convert the dictionary values to a list of lists
        sublists = list(ifbw_dict.values())

        print(sublists)
        Total_Cal_time =[]
        total_times = []
        for sublist in ifbw_dict.values():
            total_times.append((max(sublist) - min(sublist)) /60)
        print(total_times)
        if meas_ifbw == 200:
            Total_Cal_time.append(total_times[0])
        if meas_ifbw == 2000:
            Total_Cal_time.append(total_times[1])
        if meas_ifbw == 5000:
            Total_Cal_time.append(total_times[2])
        if meas_ifbw == 10000:
            Total_Cal_time.append(total_times[3])
        if meas_ifbw == 210:
            Total_Cal_time.append(total_times[4])
        print('xxx:',Total_Cal_time)
        RNum = Total_Cal_time[0]
        rd = round(RNum, 1)
        print(rd)
        p = meas_array[:, col + 1]
        if meas_ifbw == 200:
            G_base = y * 1.0
            P_base = p * 1.0
            print(G_base)
            G = y / G_base
            Ph = (p / P_base) % 360
        elif meas_ifbw == 2000:
            G = y / G_base
            Ph = (p / P_base) % 360
        elif meas_ifbw == 5000:
            G = y / G_base
            Ph = (p / P_base) % 360
        elif meas_ifbw == 10000:
            G = y / G_base
            Ph = (p / P_base) % 360
        elif meas_ifbw == 210:
            G = y / G_base
            Ph = (p / P_base) % 360
        else:
            print("Unsupported value of meas_ifbw")
        #for i, value in enumerate(G):
            #print(f"G[{i}]/y[200] = {value}")
        # plots
        dataSetLabel = ', IFBW: ' + meas_params['IFBW [Hz]'] + '\n' +meas_params['barcodes']

        print(Ph)
        # plot 1
        minY = -10
        maxY = 70
        axs[0, 0].vlines(int(len(y) / 3), minY, maxY, 'k', alpha=0.2)
        axs[0, 0].vlines(2 * int(len(y) / 3), minY, maxY, 'k', alpha=0.2)
        axs[0, 0].text(0.8 * int(len(y) / 6), minY + 5, 'Lens 1', backgroundcolor='r', fontsize=20)
        axs[0, 0].text(2.8 * int(len(y) / 6), minY + 5, 'Lens 2', backgroundcolor='g', fontsize=20)
        axs[0, 0].text(4.8 * int(len(y) / 6), minY + 5, 'Lens 3', backgroundcolor='b', fontsize=20)
        axs[0, 0].plot(np.linspace(1, len(y), num=len(y)), y, 'k', alpha=0.2)
        axs[0, 0].set_xlabel('port')
        axs[0, 0].set_ylabel('S$_{21}$ [dB]')
        axs[0, 0].set_xticks([0.5 * int(len(y) / 3), 1 * int(len(y) / 3), 1.5 * int(len(y) / 3), 2 * int(len(y) / 3),2.5 * int(len(y) / 3), 3 * int(len(y) / 3)])
        axs[0, 0].set_xlim([1, len(y) + 1])
        axs[0, 0].set_ylim([minY, maxY])
        axs[0, 0].grid('on')
        axs[0, 0].axhline(y=droppedThresh, color="red", linestyle='--')

        # plot 2
        minY = -10
        maxY = 70
        minX = 0
        maxX = 5500

        ListIFBW = []
        ListIFBW.append(meas_ifbw)
        print(ListIFBW)
        np.array(y).tolist()
        Xaxis = (ListIFBW * len(y))
        df = pd.DataFrame(data={'S21': G,'IFBW': Xaxis})
        box_plot = sns.boxplot(x=Xaxis, y='S21', data=df, showfliers=False, ax=axs[0, 1], width=0.2, whis= 2, order= ['200','210','2000','5000','10000'])
        #sns.pointplot(x=Xaxis, y='S21', data=df, ax=axs[0, 1], color="k")
        axs[0, 1].set_xlabel('IFBW[Hz]')
        mean_value = statistics.mean(G)
        print('XS:::',mean_value)
        #axs[0, 1].text(meas_ifbw, 6, mean_value)
        axs[0, 1].set_ylabel('G/G$_{IF=200Hz}$')
        axs[0, 1].tick_params(axis='x', labelsize=10)
        axs[0, 1].set_ylim([0, 2])
        #axs[0, 1].set_xlim([minX, maxX])
        axs[0, 1].grid('on')

        # plot 3
        minX = 0
        maxX = 10200
        minY = 0
        maxy = 20
        df = pd.DataFrame(data={'S21': Ph, 'IFBW': Xaxis})
        sns.boxplot(x=Xaxis, y='S21', data=df, showfliers=False, ax=axs[1, 1], width=0.2, whis= 2, order= ['200','210','2000','5000','10000'])
        axs[1, 1].set_xlabel('IFBW')
        axs[1, 1].set_ylabel('Phase Difference from$_{IF=200Hz}$')
        axs[1, 1].tick_params(axis='x', labelrotation=90, labelsize=10)
        axs[1, 1].set_ylim([0, 2])
        #axs[1, 1].set_xlim([minX, maxX])
        axs[1, 1].grid('on')
        # plot 4
        minY = 0
        maxy = 60
        minx = 0
        maxx = 11000
        axs[2, 1].plot(meas_ifbw, Total_Cal_time,'kx', markersize= 10)
        RNum = Total_Cal_time[0]
        axs[2, 1].text(meas_ifbw, RNum + 5, rd)
        #axs[2, 1].axhline(y=Total_Cal_time, color="k", linestyle='--')
        axs[2, 1].set_ylabel('Time Per Frequency (Minutes)')
        axs[2, 1].set_xlabel('IFBW')
        axs[2, 1].set_yticks(np.arange(0, 125, 5))
        #axs[2, 1].set_xticks(np.arange(0,10100, 200))
        axs[2, 1].tick_params(axis='x', labelsize=10)
        axs[2, 1].set_xlim([minx, maxx])
        # plot 5
        y = meas_array[:, col + 1]
        minY = -90
        maxY = 360 + 45
        axs[1, 0].vlines(int(len(y) / 3), minY, maxY, 'k', alpha=0.2)
        axs[1, 0].vlines(2 * int(len(y) / 3), minY, maxY, 'k', alpha=0.2)
        axs[1, 0].text(0.8 * int(len(y) / 6), minY + 35, 'Lens 1', backgroundcolor='r', fontsize=20)
        axs[1, 0].text(2.8 * int(len(y) / 6), minY + 35, 'Lens 2', backgroundcolor='g', fontsize=20)
        axs[1, 0].text(4.8 * int(len(y) / 6), minY + 35, 'Lens 3', backgroundcolor='b', fontsize=20)
        axs[1, 0].plot(np.linspace(1, len(y), num=len(y)), y, 'k', alpha=0.2)
        axs[1, 0].set_xlabel('port')
        axs[1, 0].set_ylabel('Phase [deg]')
        axs[1, 0].set_xlim([1, len(y) + 1])
        axs[1, 0].set_ylim([minY, maxY])
        axs[1, 0].set_yticks(np.linspace(0, 360, num=int(360 / 45) + 1))
        axs[1, 0].set_xticks([0.5 * int(len(y) / 3), 1 * int(len(y) / 3), 1.5 * int(len(y) / 3), 2 * int(len(y) / 3), 2.5 * int(len(y) / 3), 3 * int(len(y) / 3)])
        axs[1, 0].grid('on')
        # out
        loaded = True
    else:
        loaded = False

# run
for p in range(2):
    beam = p + 1
    for l in range(len(f_set_list)):
        f_set = f_set_list[l]
        droppedThresh = droppedThreshList[l]
        sns.set_style('darkgrid')
        sns.set_palette('Set2')
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

        # plot
        ymax1 = 25.0
        mean = np.mean(np.array(stat_TLM_median_log))
        # plot histogram
        ymax1 = 25.0
        mean = np.mean(np.array(stat_TLM_median_log))

        # print(measFiles)
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

        # format
        plt.tight_layout()

        # save
        fileName = measType + '_f-set' + str(f_set) + '_b' + str(beam) + '.png'
        newPath = filePath + SaveFileName
        if not os.path.exists(newPath):
            os.makedirs(newPath)
        plt.savefig(newPath + '/' + fileName, dpi=200)
        try:
            total_seconds_changes_df = pd.DataFrame({'Total Seconds': total_seconds_changes})
            total_seconds_changes_df.to_csv(os.path.join(filePath, 'total_seconds_changes.csv'), index=False)
            print("Total seconds changes saved to 'total_seconds_changes.csv'")
        except PermissionError as e:
            print(f"Error saving total seconds changes: {e}.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

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