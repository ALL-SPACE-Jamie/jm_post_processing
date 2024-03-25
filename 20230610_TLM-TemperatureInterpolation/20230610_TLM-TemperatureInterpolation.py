import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import csv
import pickle

# set-up
make_plots = True
setUp = {}
setUp['filePath'] = r'C:\Scratch\20240219\Tx'
setUp['pathCreate'] = ['figures', 'figuresBAD', 'files', 'pickles', 'overviews']
setUp['filePath_forGradGen'] = setUp['filePath'] + r'\_data_forGradGen'
setUp['filePath_forInterp'] = setUp['filePath'] + r'\_data_forInterp'
setUp['picklePath'] = setUp['filePath'] + r'\pickles'
setUp['fileOutPath'] = setUp['filePath'] + r'\files'
freq_list = ['17.70', '18.20', '18.70', '19.20', '19.70', '20.20', '20.70', '21.20']
freq_list = ['27.50', '28.00', '28.50', '29.00', '31.00']
freqChoice = '17.70'

# create directories
for subDirectory in setUp['pathCreate']:
    directory = setUp['filePath'] + '\\' + subDirectory
    print(directory)
    if not os.path.exists(directory):
        os.makedirs(directory)

# definitions
def find__measFiles(filePath, fileString, freqChoice):
    global measFiles, files
    files = []
    for root, directories, file in os.walk(filePath):
        for file in file:
            if (file.endswith(".csv")) == True:
                files.append(os.path.join(root, file))
    measFiles = []
    sizeLog = []
    for i in range(len(files)):
        if fileString in files[i] and 'GHz_'+freqChoice+'_GHz' in files[i]:
            if os.path.getsize(files[i]) > 1000:
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
        index_start = [index for index in range(
            len(meas_info)) if 'barcodes' in meas_info[index]][0] + 2
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

for freqChoice in freq_list:
    # find all of the measurements
    outFileType = 'OP_2'
    find__measFiles(setUp['filePath_forGradGen'], outFileType, freqChoice)
    
    # find all of the boards tested and make a dictionary
    globalDict = {}
    globalDict['barcodes'] = []
    boardTestTemperatures = {}
    for filePath in measFiles:
        print(filePath.split('\\')[-1])
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
    calcArrays['beam1'] = {}
    calcArrays['beam2'] = {}
    for filePath in measFiles:
        find__fileDetails(filePath)
        if meas_params['barcodes'] in globalDict['barcodes_threeTemps']:
            calcArrays['beam'+str(meas_params['Beam'])]['f_c='+str(meas_params['f_c'])] = {}
    for filePath in measFiles:
        find__fileDetails(filePath)
        if meas_params['barcodes'] in globalDict['barcodes_threeTemps']:
            calcArrays['beam'+str(meas_params['Beam'])]['f_c=' +
                                                        str(meas_params['f_c'])][meas_params['barcodes']] = {}
    for filePath in measFiles:
        find__fileDetails(filePath)
        if meas_params['barcodes'] in globalDict['barcodes_threeTemps']:
            calcArrays['beam'+str(meas_params['Beam'])]['f_c='+str(meas_params['f_c'])
                                                        ][meas_params['barcodes']]['T'+meas_params['Temp. [°C]']] = {}
            calcArrays['beam'+str(meas_params['Beam'])]['f_c='+str(meas_params['f_c'])
                                                        ][meas_params['barcodes']]['T'+'diffMin'] = {}
            calcArrays['beam'+str(meas_params['Beam'])]['f_c='+str(meas_params['f_c'])
                                                        ][meas_params['barcodes']]['T'+'diffMax'] = {}
    for filePath in measFiles:
        find__fileDetails(filePath)
        if meas_params['barcodes'] in globalDict['barcodes_threeTemps']:
            calcArrays['beam'+str(meas_params['Beam'])]['f_c='+str(meas_params['f_c'])
                                                        ][meas_params['barcodes']]['T'+meas_params['Temp. [°C]']]['freq'] = meas_frequencies
            calcArrays['beam'+str(meas_params['Beam'])]['f_c='+str(meas_params['f_c'])
                                                        ][meas_params['barcodes']]['T'+meas_params['Temp. [°C]']]['gain'] = meas_array_gain
            calcArrays['beam'+str(meas_params['Beam'])]['f_c='+str(meas_params['f_c'])
                                                        ][meas_params['barcodes']]['T'+meas_params['Temp. [°C]']]['phase'] = meas_array_phase
    
    # calculate differences
    for beam in calcArrays:
        for f_c in calcArrays[beam]:
            for barcode in globalDict['barcodes_threeTemps']:
                calcArrays[beam][f_c][barcode]['TdiffMin']['gain'] = calcArrays[beam][f_c][barcode]['T25']['gain'] - \
                    calcArrays[beam][f_c][barcode]['T45']['gain']
                calcArrays[beam][f_c][barcode]['TdiffMax']['gain'] = calcArrays[beam][f_c][barcode]['T65']['gain'] - \
                    calcArrays[beam][f_c][barcode]['T45']['gain']
                calcArrays[beam][f_c][barcode]['TdiffMin']['phase'] = calcArrays[beam][f_c][barcode]['T25']['phase'] - \
                    calcArrays[beam][f_c][barcode]['T45']['phase']
                calcArrays[beam][f_c][barcode]['TdiffMax']['phase'] = calcArrays[beam][f_c][barcode]['T65']['phase'] - \
                    calcArrays[beam][f_c][barcode]['T45']['phase']
    
    # average gain
    for beam in calcArrays:
        for f_c in calcArrays[beam]:
            avArrayMin_gain = np.zeros_like(meas_array_gain)
            avArrayMax_gain = np.zeros_like(meas_array_gain)
            for barcode in globalDict['barcodes_threeTemps']:
                avArrayMin_gain = avArrayMin_gain + \
                    10**(calcArrays[beam][f_c][barcode]['TdiffMin']['gain']/20.0)
                avArrayMax_gain = avArrayMax_gain + \
                    10**(calcArrays[beam][f_c][barcode]['TdiffMax']['gain']/20.0)
            avArrayMin_gain = 20.0*np.log10(avArrayMin_gain /
                                            float(len(globalDict['barcodes_threeTemps'])))
            avArrayMax_gain = 20.0*np.log10(avArrayMax_gain /
                                            float(len(globalDict['barcodes_threeTemps'])))
            calcArrays[beam][f_c]['Averages'] = {}
            calcArrays[beam][f_c]['Averages']['T'+'diffMin'] = {}
            calcArrays[beam][f_c]['Averages']['T'+'diffMax'] = {}
            calcArrays[beam][f_c]['Averages']['T'+'diffMin']['gain'] = avArrayMin_gain
            calcArrays[beam][f_c]['Averages']['T'+'diffMax']['gain'] = avArrayMax_gain
    
    # average phase (and unwrap)
    for beam in calcArrays:
        for f_c in calcArrays[beam]:
            diffList = ['TdiffMin', 'TdiffMax']
            for diff in diffList:
                for barcode in globalDict['barcodes_threeTemps']:
                    phase_arrays = []
                    phaseArray = calcArrays[beam][f_c][barcode][diff]['phase']
                    phaseArrayDiff = phaseArray - 0.0
                    for j in range(phaseArray.shape[0]):
                        for k in range(phaseArray.shape[1]):
                            if phaseArrayDiff[j, k] > 90.0:
                                phaseArray[j, k] = phaseArray[j, k] - 360.0
                            if phaseArrayDiff[j, k] < -90.0:
                                phaseArray[j, k] = phaseArray[j, k] + 360.0
                    calcArrays[beam][f_c][barcode][diff]['phase'] = phaseArray
                    phase_arrays.append(phaseArray)
                    phase_arrays_av = np.zeros_like(phase_arrays[0])
                    for l in range(len(phase_arrays)):
                        phase_arrays_av = phase_arrays_av + phase_arrays[l]
                    phase_arrays_av = phase_arrays_av/float(len(phase_arrays))
                phase_arrays_std = np.std(phase_arrays, axis=0)
                calcArrays[beam][f_c]['Averages'][diff]['phase'] = phase_arrays_av
    
    # save dictionary as pickle
    freq_save_name = freqChoice.replace('.', 'g')
    with open(setUp['picklePath'] + '\\' + f'gradients_{freq_save_name}' + '.pickle', 'wb') as file:
        pickle.dump(calcArrays, file, protocol=pickle.HIGHEST_PROTOCOL)
    # import pickle as dictionary
    with open(setUp['picklePath'] + '\\' + f'gradients_{freq_save_name}' + '.pickle', "rb") as file:
        loaded_dict = pickle.load(file)
    
    # plot check
    plt.close('all')
    temperatureGrads = {}
    count = 0
    for port in range(phaseArray.shape[0]):
        temperatureGrads[str(port)] = {}
        for beam in calcArrays:
            temperatureGrads[str(port)][beam] = {}
            for f_c in calcArrays[beam]:
                temperatureGrads[str(port)][beam][f_c] = {}
                plt.figure(figsize=(7, 4))
                frequency = float(f_c.split('=')[1])
                freqCol = np.argmin((meas_frequencies-frequency)**2)
                for barcode in globalDict['barcodes_threeTemps']:
                    y = [calcArrays[beam][f_c][barcode]['TdiffMin']['gain'][port, freqCol],
                         0.0, calcArrays[beam][f_c][barcode]['TdiffMax']['gain'][port, freqCol]]
                    x = [25, 45, 65]
                    plt.plot(x, y, 'ks-', markersize=10, alpha=0.2)
                y = [calcArrays[beam][f_c]['Averages']['TdiffMin']['gain'][port, freqCol],
                     0.0, calcArrays[beam][f_c]['Averages']['TdiffMax']['gain'][port, freqCol]]
                plt.plot(x, y, 'bo-')
                temperatureGrads[str(port)][beam][f_c]['gain'] = np.mean([(-calcArrays[beam][f_c]['Averages']['TdiffMin']
                                                                           ['gain'][port, freqCol]/20.0), (calcArrays[beam][f_c]['Averages']['TdiffMax']['gain'][port, freqCol]/20.0)])
                print(-calcArrays[beam][f_c]['Averages']['TdiffMin']['gain'][0, 0]/20.0)
                print(calcArrays[beam][f_c]['Averages']['TdiffMax']['gain'][0, 0]/20.0)
                plt.title('Frequency = ' + str(frequency) + ' GHz, Port = ' +
                          str(port) + ', Beam' + str(beam)[-1])
                plt.xlabel('Temperature [degC]')
                plt.ylabel(outFileType + ' (normalised to 45 degC) [dB]')
                plt.xlim([20, 70])
                plt.ylim([-10, 10])
                plt.xticks(np.linspace(25.0, 65.0, num=9))
                plt.yticks(np.linspace(-10.0, 10.0, num=21))
                plt.grid('on')
                plt.tight_layout()
                plt.savefig(setUp['filePath'] + '\\figures\\Frequency = ' + str(frequency) +
                            ' GHz, Port = ' + str(port) + ', Beam' + str(beam)[-1] + '_gain.png', dpi=400)
                plt.close('all')
    
                plt.figure(figsize=(7, 4))
                for barcode in globalDict['barcodes_threeTemps']:
                    y = [calcArrays[beam][f_c][barcode]['TdiffMin']['phase'][port, freqCol],
                         0.0, calcArrays[beam][f_c][barcode]['TdiffMax']['phase'][port, freqCol]]
                    x = [25, 45, 65]
                    plt.plot(x, y, 'ks-', markersize=10, alpha=0.2)
                y = [calcArrays[beam][f_c]['Averages']['TdiffMin']['phase'][port, freqCol],
                     0.0, calcArrays[beam][f_c]['Averages']['TdiffMax']['phase'][port, freqCol]]
                plt.plot(x, y, 'ro-')
                temperatureGrads[str(port)][beam][f_c]['phase'] = np.mean([(-calcArrays[beam][f_c]['Averages']['TdiffMin']
                                                                            ['phase'][port, freqCol]/20.0), (calcArrays[beam][f_c]['Averages']['TdiffMax']['phase'][port, freqCol]/20.0)])
                print(-calcArrays[beam][f_c]['Averages']['TdiffMin']['phase'][0, 0]/20.0)
                print(calcArrays[beam][f_c]['Averages']['TdiffMax']['phase'][0, 0]/20.0)
                plt.title('Frequency = ' + str(frequency) + ' GHz, Port = ' +
                          str(port) + ', Beam' + str(beam)[-1])
                plt.xlabel('Temperature [degC]')
                plt.ylabel('Phase (normalised to 45 degC) [deg]')
                plt.xlim([20, 70])
                plt.ylim([-90, 90])
                plt.xticks(np.linspace(25.0, 65.0, num=9))
                plt.yticks(np.linspace(-90, 90, num=19))
                plt.grid('on')
                plt.tight_layout()
                plt.savefig(setUp['filePath'] + '\\figures\\Frequency = ' + str(frequency) +
                            ' GHz, Port = ' + str(port) + ', Beam' + str(beam)[-1] + '_phase.png', dpi=400)
                if max(y)-min(y):
                    plt.savefig(setUp['filePath'] + '\\figuresBAD\\Frequency = ' + str(frequency) +
                                ' GHz, Port = ' + str(port) + ', Beam' + str(beam)[-1] + '_phase.png', dpi=400)
                plt.close('all')
    
                count = count + 1
                print('Fig ' + str(count) + ' / ' +
                      str(int(phaseArray.shape[0])*2*len(calcArrays[beam])))
    
    # plot grads
    if make_plots == True:
        plt.close('all')
        for f_c in temperatureGrads[str(0)][beam]:
            plt.figure(figsize=(7, 4))
            gainList_b1 = []
            gainList_b2 = []
            for port in temperatureGrads:
                gainList_b1.append(temperatureGrads[port]['beam1'][f_c]['gain'])
                gainList_b2.append(temperatureGrads[port]['beam2'][f_c]['gain'])
            plt.plot(np.linspace(1, len(gainList_b1), num=len(gainList_b1)),
                     np.array(gainList_b1), 'ro', alpha=0.5, label='Beam 1')
            plt.plot(np.linspace(1, len(gainList_b2), num=len(gainList_b2)),
                     np.array(gainList_b2), 'bo', alpha=0.5, label='Beam 2')
            plt.axhline(np.median(np.array(gainList_b1)), xmin=-10, xmax=len(gainList_b1), color='r')
            plt.axhline(np.median(np.array(gainList_b2)), xmin=-10, xmax=len(gainList_b2), color='b')
            plt.text(0.0, 0.15, str(round(np.median(np.array(gainList_b1)), 2)),
                     color='red', bbox=dict(facecolor='white', edgecolor='red', pad=10.0))
            plt.text(0.0, 0.05, str(round(np.median(np.array(gainList_b2)), 2)),
                     color='blue', bbox=dict(facecolor='white', edgecolor='blue', pad=10.0))
            plt.title('Frequency = ' + str(float(f_c.split('=')[1])) + ' GHz')
            plt.xlabel('Port')
            plt.ylabel('dB/degC')
            plt.ylim([-0.3, 0.3])
            plt.grid('on')
            plt.legend()
            plt.tight_layout()
            plt.savefig(setUp['filePath'] + '\\overviews\\' + 'Frequency = ' +
                        str(float(f_c.split('=')[1])) + ' GHz_gain.png', dpi=400)
    
        for f_c in temperatureGrads[str(0)][beam]:
            plt.figure(figsize=(7, 4))
            phaseList_b1 = []
            phaseList_b2 = []
            for port in temperatureGrads:
                phaseList_b1.append(temperatureGrads[port]['beam1'][f_c]['phase'])
                phaseList_b2.append(temperatureGrads[port]['beam2'][f_c]['phase'])
            plt.plot(np.linspace(1, len(phaseList_b1), num=len(phaseList_b1)),
                     np.array(phaseList_b1), 'ro', alpha=0.5, label='Beam 1')
            plt.plot(np.linspace(1, len(phaseList_b2), num=len(phaseList_b2)),
                     np.array(phaseList_b2), 'bo', alpha=0.5, label='Beam 2')
            plt.axhline(np.median(np.array(phaseList_b1)), xmin=-10, xmax=len(phaseList_b1), color='r')
            plt.axhline(np.median(np.array(phaseList_b2)), xmin=-10, xmax=len(phaseList_b2), color='b')
            plt.text(0.0, -0.25, str(round(np.median(np.array(phaseList_b1)), 2)),
                     color='red', bbox=dict(facecolor='white', edgecolor='red', pad=10.0))
            plt.text(0.0, -0.65, str(round(np.median(np.array(phaseList_b2)), 2)),
                     color='blue', bbox=dict(facecolor='white', edgecolor='blue', pad=10.0))
            plt.title('Frequency = ' + str(float(f_c.split('=')[1])) + ' GHz')
            plt.xlabel('Port')
            plt.ylabel('deg/degC')
            plt.ylim([-1.0, 1.0])
            plt.grid('on')
            plt.legend()
            plt.tight_layout()
            plt.savefig(setUp['filePath'] + '\\overviews\\' + 'Frequency = ' +
                        str(float(f_c.split('=')[1])) + ' GHz_phase.png', dpi=400)
    
    # open all files and create new files if multi-temperature not available
    find__measFiles(setUp['filePath_forInterp'], 'RFA', freqChoice)
    for filePath in measFiles:
        print(filePath)
        find__fileDetails(filePath)
        print(meas_params['Temp. [°C]'])
        if meas_params['Temp. [°C]'] == '45':
            meas_array_25 = np.zeros_like(meas_array)
            meas_array_gain_25 = meas_array_gain + \
                calcArrays[beam][f_c]['Averages']['TdiffMin']['gain']
            meas_array_phase_25 = meas_array_phase + \
                calcArrays[beam][f_c]['Averages']['TdiffMin']['phase']
            for j in range(meas_array_phase_25.shape[0]):
                for k in range(meas_array_phase_25.shape[1]):
                    if meas_array_phase_25[j, k] > 359.9999999999:
                        meas_array_phase_25[j, k] = meas_array_phase_25[j, k] - 360.0
                    if meas_array_phase_25[j, k] < 0.0:
                        meas_array_phase_25[j, k] = meas_array_phase_25[j, k] + 360.0
            for j in range(meas_array_gain_25.shape[1]):
                meas_array_25[:, 2*j] = meas_array_gain_25[:, j]
                meas_array_25[:, 2*j+1] = meas_array_phase_25[:, j]
            meas_array_25_list = meas_info.copy()
            for k in range(len(meas_array_25)):
                meas_array_25_list.append(list(meas_array_25[k, :]))
            temperature_index = [index for index in range(
                len(meas_info)) if 'Temp. [°C]' in meas_info[index]][0]
            meas_array_25_list[temperature_index][1] = str(25)
            # write new file
            file_path_save = setUp['filePath'] + '\\files' + \
                '\\' + filePath.split('\\')[-1][0:-4] + '.csv'
            file = open(file_path_save.replace('_45C_', '_25C_interp_'), 'w+', newline='')
            with file:
                write = csv.writer(file)
                write.writerows(meas_array_25_list)
    
    for filePath in measFiles:
        find__fileDetails(filePath)
        if meas_params['Temp. [°C]'] == '45':
            meas_array_65 = np.zeros_like(meas_array)
            meas_array_gain_65 = meas_array_gain + \
                calcArrays[beam][f_c]['Averages']['TdiffMax']['gain']
            meas_array_phase_65 = meas_array_phase + \
                calcArrays[beam][f_c]['Averages']['TdiffMax']['phase']
            for j in range(meas_array_phase_65.shape[0]):
                for k in range(meas_array_phase_65.shape[1]):
                    if meas_array_phase_65[j, k] > 359.9999999999:
                        meas_array_phase_65[j, k] = meas_array_phase_65[j, k] - 360.0
                    if meas_array_phase_65[j, k] < 0.0:
                        meas_array_phase_65[j, k] = meas_array_phase_65[j, k] + 360.0
            for j in range(meas_array_gain_65.shape[1]):
                meas_array_65[:, 2*j] = meas_array_gain_65[:, j]
                meas_array_65[:, 2*j+1] = meas_array_phase_65[:, j]
            meas_array_65_list = meas_info.copy()
            for k in range(len(meas_array_65)):
                meas_array_65_list.append(list(meas_array_65[k, :]))
            temperature_index = [index for index in range(
                len(meas_info)) if 'Temp. [°C]' in meas_info[index]][0]
            meas_array_65_list[temperature_index][1] = str(65)
            # write new file
            file_path_save = setUp['filePath'] + '\\files' + \
                '\\' + filePath.split('\\')[-1][0:-4] + '.csv'
            file = open(file_path_save.replace('_45C_', '_65C_interp_'), 'w+', newline='')
            with file:
                write = csv.writer(file)
                write.writerows(meas_array_65_list)
