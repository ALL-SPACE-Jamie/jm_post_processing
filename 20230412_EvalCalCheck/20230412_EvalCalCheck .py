import pandas as pd
import numpy as np
import matplotlib.pyplot as plt; plt.rcParams['font.size'] = 12
from scipy.stats import norm
import os
import glob
import copy
import csv
import json
import time
plt.close('all')

# file path
dirScript = os.getcwd()

# parmas

temperature = '45'
tlmType = 'Rx'
measType = 'Evaluation' # 'Calibration' or 'Evaluation'
filePath = r'C:\Users\RyanFairclough\Downloads\Chosen_Rx_Boards'
SaveFileName = '\Analysis'

# definitions
def find_measFiles(path, fileString, beam):
    global measFiles, files
    files = []
    for root, directories, file in os.walk(path):
        for file in file:
            if (file.endswith(".csv"))==True:
                files.append(os.path.join(root,file))
    measFiles = []
    for i in range(len(files)):
        if fileString in files[i] and 'eam' + str(beam) in files[i]:
            measFiles.append(files[i])
    #print(measFiles)
                      
def load__measFiles(filePath):
    global meas_info, meas_array, meas_frequencies, meas_params
    meas_params = {}
    meas_info = []
    # meas_info, array and measurement frequencies
    with open(filePath, 'r') as file:
        filecontent = csv.reader(file, delimiter=',')
        time.sleep(0.10)
        for row in filecontent:
            meas_info.append(row)
        index_start = [index for index in range(len(meas_info)) if 'barcodes' in meas_info[index]][0]+2
        meas_info = meas_info[0:index_start]

        meas_array = np.genfromtxt(filePath, delimiter=',', skip_header=index_start)
        meas_frequencies = np.array(meas_info[index_start-1])[::2].astype(float)

    # meas_params
    for i in range(len(meas_info)-1):
        if len(meas_info[i]) > 1:
            paramName = meas_info[i][0]

            if paramName[0:2] == '# ':
                paramName = paramName[2:]
            meas_params[paramName] = meas_info[i][1]


def plot__gainVport(f_set, measType):
    global y, stat_TLM_median, loaded
    print(measType)
    fig.suptitle(measType + ': ' + str(f_set) + ' GHz, Beam ' + str(beam) + ', ' + str(temperature) + ' degC', fontsize=25)
    print(meas_params['f_c'])
    if float(meas_params['f_c']) == f_set and len(meas_array) > 2:
        print('blah2')
        # array
        col = int(np.where(meas_frequencies == f_set)[0][0]*2)
        y = meas_array[:, col]
        # stats
        stat_TLM_median = np.median(y); stat_TLM_median_log.append(stat_TLM_median)
        stat_l1_median = np.median(y[0:int(len(y)/3)])
        stat_l2_median = np.median(y[int(len(y)/3):2*int(len(y)/3)])
        stat_l3_median = np.median(y[2*int(len(y)/3):3*int(len(y)/3)])
        stat_TLM_std = np.std(y)
        stat_l1_std = np.std(y[0:int(len(y)/3)])
        stat_l2_std = np.std(y[int(len(y)/3):2*int(len(y)/3)])
        stat_l3_std = np.std(y[2*int(len(y)/3):3*int(len(y)/3)])
        # plot 1
        minY = -40; maxY = 40
        axs[0, 0].vlines(int(len(y)/3), minY, maxY, 'k', alpha=0.2)
        axs[0, 0].vlines(2*int(len(y)/3), minY, maxY, 'k', alpha=0.2)
        axs[0, 0].text(0.8*int(len(y)/6), minY+5, 'Lens 1', backgroundcolor = 'r', fontsize=20)
        axs[0, 0].text(2.8*int(len(y)/6), minY+5, 'Lens 2', backgroundcolor = 'g', fontsize=20)
        axs[0, 0].text(4.8*int(len(y)/6), minY+5, 'Lens 3', backgroundcolor = 'b', fontsize=20)
        axs[0, 0].plot(np.linspace(1, len(y)+1, num=len(y)), y, 'k', alpha = 0.2)
        axs[0, 0].set_xlabel('port'); axs[0, 0].set_ylabel('S$_{21}$ [dB]')
        axs[0, 0].set_xlim([1, len(y)+1]); axs[0, 0].set_ylim([minY,maxY])
        axs[0, 0].grid('on')
        # plot 2
        axs[0, 1].plot(meas_params['lens type (rx/tx)'] + meas_params['barcodes'], stat_l1_median, 'rs')
        axs[0, 1].plot(meas_params['lens type (rx/tx)'] + meas_params['barcodes'], stat_l2_median, 'g^')
        axs[0, 1].plot(meas_params['lens type (rx/tx)'] + meas_params['barcodes'], stat_l3_median, 'bP')
        axs[0, 1].plot(meas_params['lens type (rx/tx)'] + meas_params['barcodes'], stat_TLM_median, 'kX', markersize=10)
        axs[0, 1].set_xlabel('board'); axs[0, 1].set_ylabel('Median [dB]'); axs[0, 1].tick_params(axis = 'x', labelrotation = 90)
        axs[0, 1].set_ylim([minY,maxY])
        axs[0, 1].grid('on')
        # plot 3
        axs[1, 1].plot(meas_params['lens type (rx/tx)'] + meas_params['barcodes'], stat_l1_std, 'rs')
        axs[1, 1].plot(meas_params['lens type (rx/tx)'] + meas_params['barcodes'], stat_l2_std, 'g^')
        axs[1, 1].plot(meas_params['lens type (rx/tx)'] + meas_params['barcodes'], stat_l3_std, 'bP')
        axs[1, 1].plot(meas_params['lens type (rx/tx)'] + meas_params['barcodes'], stat_TLM_std, 'kX', markersize=10)
        axs[1, 1].set_xlabel('board'); axs[1, 1].set_ylabel('$\sigma$ [dB]'); axs[1, 1].tick_params(axis = 'x', labelrotation=90)
        axs[1, 1].set_ylim([0,20])
        axs[1, 1].grid('on')
        # plot 4
        axs[2, 1].plot(meas_params['lens type (rx/tx)'] + meas_params['barcodes'], stat_l1_median-stat_TLM_median, 'rs')
        axs[2, 1].plot(meas_params['lens type (rx/tx)'] + meas_params['barcodes'], stat_l2_median-stat_TLM_median, 'g^')
        axs[2, 1].plot(meas_params['lens type (rx/tx)'] + meas_params['barcodes'], stat_l3_median-stat_TLM_median, 'bP')
        axs[2, 1].set_xlabel('board'); axs[2, 1].set_ylabel('Difference from TLM [dB]'); axs[2, 1].tick_params(axis = 'x', labelrotation = 90)
        axs[2, 1].set_ylim([-10,10])
        axs[2, 1].grid('on')
        # plot 5
        y = meas_array[:, col+1]
        minY = -90; maxY = 360+45
        axs[1, 0].vlines(int(len(y)/3), minY, maxY, 'k', alpha=0.2)
        axs[1, 0].vlines(2*int(len(y)/3), minY, maxY, 'k', alpha=0.2)
        axs[1, 0].text(0.8*int(len(y)/6), minY+35, 'Lens 1', backgroundcolor = 'r', fontsize=20)
        axs[1, 0].text(2.8*int(len(y)/6), minY+35, 'Lens 2', backgroundcolor = 'g', fontsize=20)
        axs[1, 0].text(4.8*int(len(y)/6), minY+35, 'Lens 3', backgroundcolor = 'b', fontsize=20)
        axs[1, 0].plot(np.linspace(1, len(y)+1, num=len(y)), y, 'k', alpha = 0.2)
        axs[1, 0].set_xlabel('port'); axs[1, 0].set_ylabel('Phase [deg]')
        axs[1, 0].set_xlim([1, len(y)+1]); axs[1, 0].set_ylim([minY,maxY]); axs[1, 0].set_yticks(np.linspace(0, 360, num=int(360/45)+1))
        axs[1, 0].grid('on')
        # out
        loaded = True
    else:
        loaded = False
        
## RUN ##


# filePath = r'C:\Users\JamieMitchell\Downloads\tx2'
# filePath = r'C:\Users\JamieMitchell\Downloads\Eval_Somacis_multi_frequency'
if measType =='Evaluation' and tlmType == 'Tx':
    f_set_list = [29.5]
elif measType =='Calibration' and tlmType == 'Tx':
    f_set_list = [27.5, 28.0, 28.5, 29.0, 29.5, 30.0, 30.5, 31.0]
elif measType =='Evaluation' and tlmType == 'Rx':
    f_set_list = [19.2]
elif measType =='Calibration' and tlmType == 'Rx':
    f_set_list = [17.7, 18.2, 18.7, 19.2, 19.7, 20.2, 20.7, 21.2]

# run
for p in range(2):
    beam = p+1
    for l in range(len(f_set_list)):
        f_set = f_set_list[l]
        #print(f_set)
        
        # find all meas files
        find_measFiles(filePath, 'OP', beam)
        
        fig, axs = plt.subplots(3, 2, figsize=(25,15))
        stat_TLM_median_log = []
        for k in range(len(measFiles)):

            # load meas file
            if '_' + temperature + 'C' in measFiles[k]:#str(temperature) + 'C' in measFiles[k]:# and 'teration_1' in measFiles[k]:
                load__measFiles(measFiles[k])

                #print(load__measFiles(measFiles[k]))
                # plot
                plot__gainVport(f_set, measType)
                #print('k=', k)
                #print(measFiles[k])
                #print(beam)
                #print(loaded)
                # colate
                if loaded == True:
                    stat_TLM_median_log.append(stat_TLM_median)
                    #print(stat_TLM_median)
                    print('Added to plot')
        # plot histogram
        ymax1 = 25.0

        mean = np.mean(np.array(stat_TLM_median_log))

        #print(measFiles)
        axs[2, 0].hist(np.array(stat_TLM_median_log), bins=11)
        axs[2, 0].set_xlabel('TLM median [dB]'); axs[2, 0].set_ylabel('count')
        axs[2, 0].set_xlim([mean-5,mean+5]); axs[2, 0].set_ylim([0,25])
        axs[2, 0].axvline(mean, ymin = 0.0, ymax = ymax1, color='k')
        axs[2, 0].text(mean+0.1, 10.25, str(round(mean, 2))+' dB', rotation=90)
        axs[2, 0].grid('on')
        variance = np.var(np.array(stat_TLM_median_log))
        sigma = np.sqrt(variance)
        x = np.linspace(-50, 50, 1001)
        axs[2, 0].plot(x, ymax1*norm.pdf(x, mean, sigma)/(max(norm.pdf(x, mean, sigma))), 'r')
        
        # format
        plt.tight_layout()
        
        # save
        fileName = measType + '_f-set' + str(f_set) + '_b' + str(beam) + '.png'
        newPath=filePath + SaveFileName
        print(newPath)
        if not os.path.exists(newPath):
            os.makedirs(newPath)
        plt.savefig(newPath +'/'+ fileName, dpi = 200)