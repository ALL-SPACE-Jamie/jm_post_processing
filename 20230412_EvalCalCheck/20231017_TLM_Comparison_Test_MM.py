import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt;

plt.rcParams['font.size'] = 10
import scipy
from scipy.stats import norm
import os
import glob
import copy
import csv
import json
import time
from pylab import *

plt.close('all')

filePath = r'C:\Users\RyanFairclough\Downloads\Algo2_vsAlgo1' #Location of data
filename = r'Port_Spread' #Filename for the output plots
tlmType = ['QR420-0344-00004']#, '00006', '00338_I-Type']
plotTitle='P-Type_Rx_Algo-1_420-0344-00004 '
termType = 'P-Type_v4_Rx_Algo 2_00004'
fqRange = 'Rx'
chop = False
pltMinMax=False
line='None' #'One'
mark='o'

if fqRange == 'Rx':
    f_set_list = [17.7, 18.2, 18.7, 19.2, 19.7, 20.2, 20.7, 21.2]
    plotXlimMin = 17.7
    plotXlimMax = 21.2
    plotYlimMin = 0
    plotYlimMax = 50
elif fqRange == 'Tx':
    f_set_list = [27.50, 28.00, 28.50, 29.00, 29.50, 30.00, 30.50, 31.00]
    plotXlimMin = 27.5
    plotXlimMax = 31.0
    plotYlimMin = -20
    plotYlimMax = 15


# file path
dirScript = os.getcwd()


# definitions
def find_measFiles(path, fileString, beam, f_set):
    global measFiles, files
    files = []
    for root, directories, file in os.walk(path):
        for file in file:
            if (file.endswith(".csv")) == True:
                files.append(os.path.join(root, file))
    measFiles = []
    for i in range(len(files)):
        if fileString in files[i] and 'eam' + str(beam) in files[i] and '_GHz_'+str(f_set)+'0_GHz_45C' in files[i]:
            measFiles.append(files[i])


def load_measFiles(filePath):
    global meas_info, meas_array, meas_frequencies, meas_params, meas_array_gain, meas_array_phase
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
        meas_array_phase = meas_array[:, 1:][:, ::2]
        meas_frequencies = np.array(meas_info[index_start - 1])[::2].astype(float)

        # meas_params
    for i in range(len(meas_info) - 1):
        if len(meas_info[i]) > 1:
            paramName = meas_info[i][0]

            if paramName[0:2] == '# ':
                paramName = paramName[2:]
            meas_params[paramName] = meas_info[i][1]


colourMap = [['b','orange','g','r','purple','brown','magenta','grey'],
             ['c', 'peru', 'darkgreen', 'darksalmon', 'plum', 'chocolate', 'hotpink', 'k'],
             ['cornflowerblue', 'tan', 'greenyellow', 'darkred', 'blueviolet', 'rosybrown', 'mediumvioletred', 'darkslategrey'],
             ['deepskyblue', 'gold', 'olivedrab', 'crimson', 'indigo', 'sienna', 'orchid', 'silver'],
             ['dodgerblue', 'goldenrod', 'seagreen', 'lightcoral', 'thistle', 'peachpuff', 'palevioletred', 'gainsboro']]

for beamChoice in range(2):
    beamChoice = beamChoice + 1
    plt.figure(figsize=(7, 4))
    count = 0
    if chop == False:
        plt.close('all')
        plt.figure(figsize=(7, 4))
    for f_set in f_set_list:
        #plt.figure(figsize=(7,4))

        #print('GHz_' + str(f_set))
        find_measFiles(filePath, 'OP_2', beamChoice,f_set)

        if chop == False:
            plt.close('all')
            plt.figure(figsize=(7, 4))
        for measFile in measFiles:
            # print(measFile)

            load_measFiles(measFile)
            if float(meas_params['f_c']) == float(f_set):

                fileN = measFile.split('\\')[-1]
                #print(len(tlmType))
                measLabel = []

                if len(tlmType)>2 and chop==False:
                    pltMinMax=False
                for i in range(len(tlmType)):
                    if chop == True:
                        locLeft = np.argmin((meas_frequencies - (float(f_set) - 0.25)) ** 2);
                        locRight = np.argmin((meas_frequencies - (float(f_set) + 0.25)) ** 2)
                        plotLabel = str(f_set)
                    if chop == False:
                        locLeft = 0;
                        locRight = len(meas_frequencies) - 1
                        plotLabel= tlmType[i]
                    #print(i)
                    colMap=colourMap[i]
                    #print(plotLabel)
                    if tlmType[i] in fileN:

                        # if beamChoice == 1:
                        #     plt.plot(meas_frequencies[locLeft:locRight+1], np.median(meas_array_gain, axis=0)[locLeft:locRight+1], color = colMap[count], linewidth = 5, label = str(f_set) + ' GHz')
                        # if beamChoice == 2:
                        #     plt.plot(meas_frequencies[locLeft:locRight+1], np.median(meas_array_gain, axis=0)[locLeft:locRight+1], color = colMap[count], linestyle = '--', linewidth = 5, label = str(f_set) + ' GHz')
                        #print(len(meas_array_gain))
                        #print(len(meas_array_gain[1]))
                        if line=='None' and pltMinMax==False:
                            plt.plot(range(int(len(meas_array_gain) / 3)),
                                 meas_array_gain[0:int(len(meas_array_gain) / 3),np.argwhere((meas_frequencies==f_set))[0]], color = 'b', linestyle=line, marker=mark, markersize=2, label='Lens 1')
                            plt.plot(range(int(len(meas_array_gain) / 3)),
                                     meas_array_gain[int(len(meas_array_gain) / 3):int(2*len(meas_array_gain) / 3), np.argwhere((meas_frequencies==f_set))[0]], color='g', linestyle=line, marker=mark, markersize=2, label='Lens 2')
                            plt.plot(range(int(len(meas_array_gain) / 3)),
                                     meas_array_gain[int(2*len(meas_array_gain) / 3): len(meas_array_gain), np.argwhere((meas_frequencies==f_set))[0]], color='orange', linestyle=line, marker=mark, markersize=2, label='Lens 3')
                        else:
                            plt.plot(meas_frequencies[locLeft:locRight + 1],
                                     np.median(meas_array_gain, axis=0)[locLeft:locRight + 1], color=colMap[count],
                                     linewidth=5, label=plotLabel)#+str(tlmType[i]))


                        if pltMinMax==True:
                            plt.fill_between(meas_frequencies[locLeft:locRight + 1],
                                         np.min(meas_array_gain, axis=0)[locLeft:locRight + 1],
                                         np.max(meas_array_gain, axis=0)[locLeft:locRight + 1], color = colMap[count],
                                         alpha=0.2)  # , label = '\n Port min/max')

                        temp = meas_array_gain * 1.0
                        plt.legend(ncol=3, loc='upper right', fontsize=5)
        count = count + 1
        if line == 'None' and pltMinMax == False:
            plt.xlabel('Port Number');
            plt.ylabel('S$_{21}$ (arb.) [dB]')
            plt.ylim([plotYlimMin, plotYlimMax]);
            plt.xlim([0, int(len(meas_array_gain) / 3)]);  # plt.xlim([min(f_set_list), max(f_set_list)])
            plt.yticks(np.linspace(plotYlimMin, plotYlimMax, num=int((abs(plotYlimMin) + abs(plotYlimMax)) / 5) + 1))
            plt.grid('on')
        else:
            plt.xlabel('Frequency [GHz]');
            plt.ylabel('S$_{21}$ (arb.) [dB]')
            plt.ylim([plotYlimMin, plotYlimMax]);
            plt.xlim([plotXlimMin, plotXlimMax]);  # plt.xlim([min(f_set_list), max(f_set_list)])
            plt.yticks(np.linspace(plotYlimMin, plotYlimMax, num=int((abs(plotYlimMin) + abs(plotYlimMax)) / 5) + 1))
            plt.grid('on')

        #plt.tight_layout()
        # plt.title(termType+'\nf_set = ' + str(f_set) + ' GHz, Beam ' + str(beamChoice))

        if chop==True:
            plt.title(termType + '\nBeam ' + str(beamChoice))
            plt.savefig(filePath + '\\' + filename + '_Beam_' + str(beamChoice) + '.png',
                    dpi=400)
        elif chop==False:
            plt.title(plotTitle + '\nBeam ' + str(beamChoice) + ', f_set = ' + str(f_set) + ' GHz')
            plt.savefig(filePath + '\\'+filename + '_'+ str(tlmType[0])+'_f_set_' + str(f_set) + 'GHz_Beam_' + str(beamChoice) + '.png', dpi=400)
