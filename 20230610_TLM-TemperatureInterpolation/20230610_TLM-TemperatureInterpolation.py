import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import csv

# set-up
setUp = {}
setUp['filePath'] = r'C:\Scratch\20230610_TLM-TemperatureInterpolation\SES_Terminal_Tx'

# definitions
def find__measFiles(filePath, fileString):
    global measFiles
    files = []
    for root, directories, file in os.walk(filePath):
        for file in file:
            if (file.endswith(".csv")) == True:
                files.append(os.path.join(root, file))
    measFiles = []
    for i in range(len(files)):
        if fileString in files[i] in files[i]:
            measFiles.append(files[i])

def find__fileDetails(filePath):
    global meas_info, meas_params, meas_array, meas_frequencies, meas_array_gain, meas_array_phase
    meas_params = {}
    meas_info = []
    
    # meas_info, array and measurement frequencies
    with open(filePath, 'r') as file:
        filecontent = csv.reader(file, delimiter=',')
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
            if meas_params[paramName][0] == ' ':
                meas_params[paramName] = meas_params[paramName][1:]

## run ##

# find all of the measurements
find__measFiles(setUp['filePath'], 'RFA')
measFiles = measFiles[0:200] ##### DelMe

# find all of the boards tested and make a dictionary
globalDict = {}; globalDict['barcodes'] = []
boardTestTemperatures = {}
for filePath in measFiles:
    find__fileDetails(filePath)
    if meas_params['barcodes'] not in globalDict['barcodes']:
        globalDict['barcodes'].append(meas_params['barcodes'])
    boardTestTemperatures[meas_params['barcodes']] = []

# add the tested temperatures
for filePath in measFiles:
    find__fileDetails(filePath)
    if meas_params['Temp. [°C]'] not in boardTestTemperatures[meas_params['barcodes']]:
        boardTestTemperatures[meas_params['barcodes']].append(meas_params['Temp. [°C]'])
 
# make list of boards tested at 3 temperatures
globalDict['barcodes_threeTemps'] = []
for barcode in globalDict['barcodes']:
    if len(boardTestTemperatures[barcode]) == 3:
        globalDict['barcodes_threeTemps'].append(barcode)
        
# dictionary of all arrays for calculation
calcArrays = {}
calcArrays['beam1'] = {};calcArrays['beam2'] = {}
for filePath in measFiles:
    find__fileDetails(filePath)
    if meas_params['barcodes'] in globalDict['barcodes_threeTemps']:
        calcArrays['beam'+str(meas_params['Beam'])]['f_c='+str(meas_params['f_c'])] = {}
for filePath in measFiles:
    find__fileDetails(filePath)
    if meas_params['barcodes'] in globalDict['barcodes_threeTemps']:
        calcArrays['beam'+str(meas_params['Beam'])]['f_c='+str(meas_params['f_c'])][meas_params['barcodes']] = {}
for filePath in measFiles:
    find__fileDetails(filePath)
    if meas_params['barcodes'] in globalDict['barcodes_threeTemps']:
        calcArrays['beam'+str(meas_params['Beam'])]['f_c='+str(meas_params['f_c'])][meas_params['barcodes']]['T'+meas_params['Temp. [°C]']] = {}
        calcArrays['beam'+str(meas_params['Beam'])]['f_c='+str(meas_params['f_c'])][meas_params['barcodes']]['T'+'diffMin'] = {}
        calcArrays['beam'+str(meas_params['Beam'])]['f_c='+str(meas_params['f_c'])][meas_params['barcodes']]['T'+'diffMax'] = {}
for filePath in measFiles:
    find__fileDetails(filePath)
    if meas_params['barcodes'] in globalDict['barcodes_threeTemps']:
        calcArrays['beam'+str(meas_params['Beam'])]['f_c='+str(meas_params['f_c'])][meas_params['barcodes']]['T'+meas_params['Temp. [°C]']]['freq'] = meas_frequencies
        calcArrays['beam'+str(meas_params['Beam'])]['f_c='+str(meas_params['f_c'])][meas_params['barcodes']]['T'+meas_params['Temp. [°C]']]['gain'] = meas_array_gain
        calcArrays['beam'+str(meas_params['Beam'])]['f_c='+str(meas_params['f_c'])][meas_params['barcodes']]['T'+meas_params['Temp. [°C]']]['phase'] = meas_array_phase

# calculation
for beam in calcArrays:
    for f_c in calcArrays[beam]:
        for barcode in globalDict['barcodes_threeTemps']:
            calcArrays[beam][f_c][barcode]['TdiffMin']['gain'] = calcArrays[beam][f_c][barcode]['T25']['gain']-calcArrays[beam][f_c][barcode]['T45']['gain']
            calcArrays[beam][f_c][barcode]['TdiffMax']['gain'] = calcArrays[beam][f_c][barcode]['T65']['gain']-calcArrays[beam][f_c][barcode]['T45']['gain']
            calcArrays[beam][f_c][barcode]['TdiffMin']['phase'] = calcArrays[beam][f_c][barcode]['T25']['phase']-calcArrays[beam][f_c][barcode]['T45']['phase']
            calcArrays[beam][f_c][barcode]['TdiffMax']['phase'] = calcArrays[beam][f_c][barcode]['T65']['phase']-calcArrays[beam][f_c][barcode]['T45']['phase']
            
for beam in calcArrays:
    for f_c in calcArrays[beam]:
        avArrayMin_gain = np.zeros_like(meas_array_gain)
        avArrayMax_gain = np.zeros_like(meas_array_gain)
        for barcode in globalDict['barcodes_threeTemps']:
            avArrayMin_gain = avArrayMin_gain + 10**(calcArrays[beam][f_c][barcode]['TdiffMin']['gain']/20.0)
            avArrayMax_gain = avArrayMax_gain + 10**(calcArrays[beam][f_c][barcode]['TdiffMax']['gain']/20.0)
        avArrayMin_gain = 20.0*np.log10(avArrayMin_gain/float(len(globalDict['barcodes_threeTemps']))) 
        avArrayMax_gain = 20.0*np.log10(avArrayMax_gain/float(len(globalDict['barcodes_threeTemps'])))
        calcArrays[beam][f_c]['Averages'] = {}
        calcArrays[beam][f_c]['Averages']['T'+'diffMin'] = {}
        calcArrays[beam][f_c]['Averages']['T'+'diffMax'] = {}
        calcArrays[beam][f_c]['Averages']['T'+'diffMin']['gain'] = avArrayMin_gain
        calcArrays[beam][f_c]['Averages']['T'+'diffMax']['gain'] = avArrayMax_gain
        
# for beam in calcArrays:
#     for f_c in calcArrays[beam]:
#         avArrayMin_phase = np.zeros_like(meas_array_phase)
#         avArrayMax_phase = np.zeros_like(meas_array_phase)
#         for barcode in globalDict['barcodes_threeTemps']:
#             avArrayMin_phase = avArrayMin_phase + calcArrays[beam][f_c][barcode]['TdiffMin']['phase']
#             avArrayMax_phase = avArrayMax_phase + calcArrays[beam][f_c][barcode]['TdiffMax']['phase']
#         avArrayMin_phase = avArrayMin_phase/float(len(globalDict['barcodes_threeTemps'])) 
#         avArrayMax_phase = avArrayMax_phase/float(len(globalDict['barcodes_threeTemps']))
#         calcArrays[beam][f_c]['Averages']['T'+'diffMin']['phase'] = avArrayMin_phase
#         calcArrays[beam][f_c]['Averages']['T'+'diffMax']['phase'] = avArrayMax_phase

for beam in calcArrays:
    for f_c in calcArrays[beam]:
        diffList = ['TdiffMin', 'TdiffMax']
        for barcode in globalDict['barcodes_threeTemps']:
            phase_arrays = []
            for diff in diffList:
                phase_arrays.append(calcArrays[beam][f_c][barcode][diff]['phase'])
            phase_arrays.append(np.zeros_like(calcArrays[beam][f_c][barcode][diff]['phase']))
            phase_arrays_av = np.median(phase_arrays, axis=0)
            phase_arrays_std= np.std(phase_arrays, axis=0)
            phase_arrays_unwrap = []
            for diff in diffList:
                phaseArray = calcArrays[beam][f_c][barcode][diff]['phase'].copy()
                for j in range(phase_arrays_av.shape[0]):
                    for k in range(phase_arrays_av.shape[1]):
                        if phaseArray[j,k] - phase_arrays_av[j,k] > 45.0:
                            phaseArray[j,k] = phaseArray[j,k] - 360.0
                        if phaseArray[j,k] - phase_arrays_av[j,k] < -45.0:
                            phaseArray[j,k] = phaseArray[j,k] + 360.0
                phase_arrays_unwrap.append(phaseArray)
                phase_arrays_av_unwrap = np.average(phase_arrays_unwrap, axis=0)
                phase_arrays_std_unwrap= np.std(phase_arrays_unwrap, axis=0)
                calcArrays[beam][f_c]['Averages'][diff]['phase'] = phase_arrays_av_unwrap

# plot check
port = 10
plt.close('all')


for beam in calcArrays:
    for f_c in calcArrays[beam]:
        # plt.figure(figsize=(7,4))
        frequency = float(f_c.split('=')[1])
        freqCol = np.argmin((meas_frequencies-frequency)**2)
        # for barcode in globalDict['barcodes_threeTemps']:
        #     y = [calcArrays[beam][f_c][barcode]['TdiffMin']['gain'][port,freqCol], 0.0, calcArrays[beam][f_c][barcode]['TdiffMax']['gain'][port,freqCol]]
        #     x = [65,45,25]
        #     plt.plot(x,y,'ko-',alpha=0.2)
        # y = [calcArrays[beam][f_c]['Averages']['TdiffMin']['gain'][port,freqCol], 0.0, calcArrays[beam][f_c]['Averages']['TdiffMax']['gain'][port,freqCol]]
        # plt.plot(x,y,'ro-')
        # plt.title('Frequency = ' + str(frequency) + ' GHz, Port = ' + str(port) + ', Beam' + str(beam)[-1])
        # plt.xlabel('Temperature [degC]'); plt.ylabel('S$_{21}$ (normalised to 45 degC) [dB]')
        # plt.xlim([20,70]); plt.ylim([-10,10])
        # plt.xticks(np.linspace(25.0, 65.0, num=9)); plt.yticks(np.linspace(-10.0, 10.0, num=21))
        # plt.grid('on')
        # plt.tight_layout()
        # plt.savefig('C:\\Scratch\\figures\\Frequency = ' + str(frequency) + ' GHz, Port = ' + str(port) + '_gain.png', dpi=400)
        
        plt.figure(figsize=(7,4))
        for barcode in globalDict['barcodes_threeTemps']:
            y = [calcArrays[beam][f_c][barcode]['TdiffMin']['phase'][port,freqCol], 0.0, calcArrays[beam][f_c][barcode]['TdiffMax']['phase'][port,freqCol]]
            x = [65,45,25]
            plt.plot(x,y,'ko-',alpha=0.2)
        y = [calcArrays[beam][f_c]['Averages']['TdiffMin']['phase'][port,freqCol], 0.0, calcArrays[beam][f_c]['Averages']['TdiffMax']['phase'][port,freqCol]]
        plt.plot(x,y,'ro-')
        plt.title('Frequency = ' + str(frequency) + ' GHz, Port = ' + str(port) + ', Beam' + str(beam)[-1])
        plt.xlabel('Temperature [degC]'); plt.ylabel('Phase (normalised to 45 degC) [deg]')
        plt.xlim([20,70]); plt.ylim([-45,45])
        plt.xticks(np.linspace(25.0, 65.0, num=9)); plt.yticks(np.linspace(-45.0, 45.0, num=19))
        plt.grid('on')
        plt.tight_layout()
        plt.savefig('C:\\Scratch\\figures\\Frequency = ' + str(frequency) + ' GHz, Port = ' + str(port) + ', Beam' + str(beam)[-1] + '_phase.png', dpi=400)

# # open all files and create new files if multi-temperature not available
# for filePath in measFiles:
#     find__fileDetails(filePath)
#     if meas_params['barcodes'] in globalDict['barcodes_threeTemps']:












            
