import pandas as pd
import numpy as np
import matplotlib.pyplot as plt; plt.rcParams['font.size'] = 18
import os
import glob
import copy
import csv
import json
plt.close('all')

# file path
dirScript = os.getcwd()
# example file path with sync to SharePoint: r'C:\Users\JamieMitchell\OneDrive - ALL.SPACE\Desktop\sort\_readyGH\Rx Comparisons\20230116_Evaluations'
filePath = r'C:\codeRun\SW_version_comparison'
filePath = r'C:\codeRun\20230121_data\OneDrive_1_21-01-2023'

# definitions
def plot__evals(freqLog, beam, boardType, failThresh, portPerc, stdThresh, freqSet, sw1, sw2, Gain):
    global avLog, avLogFreqs, freqs, folders, stdLogFreqs, array, statDict, passLogFreqs, csvFiles, diffLens1, diffLens2, diffLens3, difference, fixData, levelDict, foldersFix, newDiff
    newDiffav = []
    newDiffstd = []
    levelDict = {}
    levelDict[str(freqSet)] = {}
    levelDict[str(freqSet)]['beam'+str(beam)] = {}
    for freq in freqLog:
        levelDict[str(freqSet)]['beam'+str(beam)][str(freq)] = {}
        
        # folders and files
        os.chdir(filePath)
        folders = next(os.walk(filePath))[1]
        folders = []
        folders = [sw1, sw2]
        foldersFix = []
        for d in range(len(folders)):
            if folders[d].split('_')[-2] == str(freqSet):
                foldersFix.append(folders[d])
        folders = foldersFix
        
        # log all paths and filenames
        foldersLog = []
        csvFiles = []
        for folder in folders:
            filePathFolder = filePath + '/' + folder
            filePathFolder = filePathFolder + '/iteration_1'
            os.chdir(filePathFolder)
            csvFileLog = glob.glob('*.csv')
            for file in csvFileLog:
                if 'OP' in file:
                    if 'Beam' + str(beam) in file:
                        csvFiles.append(file)
                        foldersLog.append(folder)
        
        # generate arrays, plot and store statistics
        os.chdir(filePath)
        pltarray = []
        fileDict = {}
        forDiff = []
        plt.figure(figsize=(12,7))
        for i in range(len(csvFiles)):
            fileDict[foldersLog[i]] = {}
            filePathFolder = filePath + '/' + foldersLog[i]
            filePathFolder = filePathFolder + '/iteration_1'
            os.chdir(filePathFolder)
            array = np.genfromtxt(filePathFolder + '/' + csvFiles[i], delimiter=',',skip_header=22)
            if len(array) == 0:
                print('FAIL\n'+filePathFolder)
            csvFile = []
            with open(filePathFolder + '/' + csvFiles[i],'r')as file:
                filecontent=csv.reader(file,delimiter=',')
                for row in filecontent:
                    csvFile.append(row)
                freqs = np.array(csvFile[21])[::2].astype(float)
                col = (np.argmin((freqs-freq)**2))*2
                freqMeas = freqs[int(col/2)]
        
            if len(array) > 10:
                if freqMeas == freq:
                    pltarray.append(copy.deepcopy(array))
                    x = np.linspace(1,len(array),num=len(array))
                    if Gain == True:
                        plt.scatter(x,array[:,col],label=foldersLog[i][0:-3], marker='o')
                        forDiff.append(array[:,col])
                    else:
                        plt.scatter(x,array[:,col+1],label=foldersLog[i][0:-3], marker='o')
                        forDiff.append(array[:,col+1])
                        
            else:
                print('Empty file!')
                
        if i == 1:
            difference = forDiff[1]-forDiff[0]
            plt.plot(x, difference,'g',label='difference')
            diffLens1 = difference[0:int(len(difference)/3)]
            diffLens2 = difference[int(len(difference)/3):int(2*len(difference)/3)]
            diffLens3 = difference[int(2*len(difference)/3):int(3*len(difference)/3)]
            diffLens1mean = np.average(diffLens1)
            diffLens2mean = np.average(diffLens2)
            diffLens3mean = np.average(diffLens3)
            diffLens1median = np.median(diffLens1)
            diffLens2median = np.median(diffLens2)
            diffLens3median = np.median(diffLens3)
            x1 = x[0:int(len(x)/3)]
            x2 = x[int(len(x)/3):int(2*len(x)/3)]
            x3 = x[int(2*len(x)/3):int(3*len(x)/3)]
            y1 = forDiff[0][0:int(len(difference)/3)]
            y2 = forDiff[0][int(len(difference)/3):int(2*len(difference)/3)]
            y3 = forDiff[0][int(2*len(difference)/3):int(3*len(difference)/3)]

            plt.plot(x1, x1*0.0+diffLens1median, 'r', linewidth=3, label='level1')
            plt.plot(x2, x2*0.0+diffLens2median, 'g', linewidth=3, label='level2')
            plt.plot(x3, x3*0.0+diffLens3median, 'b', linewidth=3, label='level3')
            
            fixData = np.transpose(np.hstack([(y1+diffLens1median), (y2+diffLens2median), (y3+diffLens3median)]))
            
            newDiff = abs(fixData-forDiff[1])
            newDiffavVal = np.median(newDiff)
            newDiffav.append(newDiffavVal)
            newDiffstdVal = np.std(newDiff)
            newDiffforCalc = []
            for m in range(len(newDiff)):
                if abs(newDiff[m] - newDiffavVal) < newDiffstdVal:
                    newDiffforCalc.append(newDiff[m])
            newDiffstd.append(np.std(newDiffforCalc))
            
            if Gain == False:
                for h in range(len(fixData)):
                    if fixData[h] > 360.0:
                        fixData[h] = fixData[h] -360.0
                    if fixData[h] < 0.0:
                        fixData[h] = fixData[h] + 360.0
            
            plt.plot(x, fixData, 'm', linewidth=1, label = 'corrected test data')
            
            levelDict[str(freqSet)]['beam'+str(beam)][str(freq)]['L1'] = diffLens1median
            levelDict[str(freqSet)]['beam'+str(beam)][str(freq)]['L2'] = diffLens2median
            levelDict[str(freqSet)]['beam'+str(beam)][str(freq)]['L3'] = diffLens3median
        else:
            print('ONLY 1 FILE!')
    
        plt.xlabel('port')
        plt.grid('on')
        plt.legend(loc='lower center',fontsize=12, ncol=2)
        if Gain == True:
            plt.ylabel('Gain [dB]'); plt.ylim([-30,30])
        else:
            plt.ylabel('Phase [deg]'); plt.ylim([-60,360+60])
        title = boardType + ' TLM board (f_meas = ' + str(freqMeas) + ' GHz - beam ' + str(beam) + ')'
        plt.title(title)
        # plt.close('all')
        # plt.savefig('C:\\codeRun\\figures\\b48_f_set = ' + str(freqSet) + '__' + title + ' GHz' + str(Gain) + '.png')
        
## RUN

# params
# freqLog = np.linspace(27.5,31.0,num=int((31-27.5)/0.1+1))
freqLog = [27.5]
boardType = 'Tx'
Gain = True

# 45 deg
levelDictT45 = {}

# run (beam 1 and 2 for single set point)
freqSetLog = [27.5]
sw1 = r'v168_b48\2023-01-18_18-14-08_Minicalrig_calibration_1_QR440-0110-00048_27.5_45C'
sw2 = r'v194_b48\2023-01-21_02-15-17_Minicalrig_calibration_1_QR440-0110-00048_27.5_45C'
plot__evals(freqLog, 1, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams = levelDict
plot__evals(freqLog, 2, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams[str(freqSetLog[0])]['beam2'] = levelDict[str(freqSetLog[0])]['beam2']
levelDictT45[str(freqSetLog[0])] = levelDictBeams[str(freqSetLog[0])]

stop

# run (beam 1 and 2 for single set point)
freqSetLog = [28.0]
sw1 = r'v168_b48\2023-01-18_18-32-04_Minicalrig_calibration_1_QR440-0110-00048_28.0_45C'
sw2 = r'v194_b48\2023-01-21_02-27-59_Minicalrig_calibration_1_QR440-0110-00048_28.0_45C'
plot__evals(freqLog, 1, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams = levelDict
plot__evals(freqLog, 2, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams[str(freqSetLog[0])]['beam2'] = levelDict[str(freqSetLog[0])]['beam2']
levelDictT45[str(freqSetLog[0])] = levelDictBeams[str(freqSetLog[0])]

# run (beam 1 and 2 for single set point)
freqSetLog = [28.5]
sw1 = r'v168_b48\2023-01-18_18-47-42_Minicalrig_calibration_1_QR440-0110-00048_28.5_45C'
sw2 = r'v194_b48\2023-01-21_02-37-58_Minicalrig_calibration_1_QR440-0110-00048_28.5_45C'
plot__evals(freqLog, 1, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams = levelDict
plot__evals(freqLog, 2, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams[str(freqSetLog[0])]['beam2'] = levelDict[str(freqSetLog[0])]['beam2']
levelDictT45[str(freqSetLog[0])] = levelDictBeams[str(freqSetLog[0])]

# run (beam 1 and 2 for single set point)
freqSetLog = [29.0]
sw1 = r'v168_b48\2023-01-18_19-03-14_Minicalrig_calibration_1_QR440-0110-00048_29.0_45C'
sw2 = r'v194_b48\2023-01-21_02-47-56_Minicalrig_calibration_1_QR440-0110-00048_29.0_45C'
plot__evals(freqLog, 1, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams = levelDict
plot__evals(freqLog, 2, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams[str(freqSetLog[0])]['beam2'] = levelDict[str(freqSetLog[0])]['beam2']
levelDictT45[str(freqSetLog[0])] = levelDictBeams[str(freqSetLog[0])]

# run (beam 1 and 2 for single set point)
freqSetLog = [29.5]
sw1 = r'v168_b48\2023-01-18_19-18-54_Minicalrig_calibration_1_QR440-0110-00048_29.5_45C'
sw2 = r'v194_b48\2023-01-21_02-57-56_Minicalrig_calibration_1_QR440-0110-00048_29.5_45C'
plot__evals(freqLog, 1, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams = levelDict
plot__evals(freqLog, 2, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams[str(freqSetLog[0])]['beam2'] = levelDict[str(freqSetLog[0])]['beam2']
levelDictT45[str(freqSetLog[0])] = levelDictBeams[str(freqSetLog[0])]

# run (beam 1 and 2 for single set point)
freqSetLog = [30.0]
sw1 = r'v168_b48\2023-01-18_19-34-16_Minicalrig_calibration_1_QR440-0110-00048_30.0_45C'
sw2 = r'v194_b48\2023-01-21_03-07-56_Minicalrig_calibration_1_QR440-0110-00048_30.0_45C'
plot__evals(freqLog, 1, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams = levelDict
plot__evals(freqLog, 2, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams[str(freqSetLog[0])]['beam2'] = levelDict[str(freqSetLog[0])]['beam2']
levelDictT45[str(freqSetLog[0])] = levelDictBeams[str(freqSetLog[0])]

# run (beam 1 and 2 for single set point)
freqSetLog = [30.5]
sw1 = r'v168_b48\2023-01-18_19-49-42_Minicalrig_calibration_1_QR440-0110-00048_30.5_45C'
sw2 = r'v194_b48\2023-01-21_03-17-55_Minicalrig_calibration_1_QR440-0110-00048_30.5_45C'
plot__evals(freqLog, 1, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams = levelDict
plot__evals(freqLog, 2, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams[str(freqSetLog[0])]['beam2'] = levelDict[str(freqSetLog[0])]['beam2']
levelDictT45[str(freqSetLog[0])] = levelDictBeams[str(freqSetLog[0])]

# run (beam 1 and 2 for single set point)
freqSetLog = [31.0]
sw1 = r'v168_b48\2023-01-18_20-05-36_Minicalrig_calibration_1_QR440-0110-00048_31.0_45C'
sw2 = r'v194_b48\2023-01-21_03-27-54_Minicalrig_calibration_1_QR440-0110-00048_31.0_45C'
plot__evals(freqLog, 1, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams = levelDict
plot__evals(freqLog, 2, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams[str(freqSetLog[0])]['beam2'] = levelDict[str(freqSetLog[0])]['beam2']
levelDictT45[str(freqSetLog[0])] = levelDictBeams[str(freqSetLog[0])]




# 25 deg
levelDictT25 = {}

# run (beam 1 and 2 for single set point)
freqSetLog = [27.5]
sw1 = r'v168_b48\2023-01-19_20-55-34_Minicalrig_calibration_1_QR440-0110-00048_27.5_25C'
sw2 = r'v194_b48\2023-01-21_00-55-04_Minicalrig_calibration_1_QR440-0110-00048_27.5_25C'
plot__evals(freqLog, 1, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams = levelDict
plot__evals(freqLog, 2, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams[str(freqSetLog[0])]['beam2'] = levelDict[str(freqSetLog[0])]['beam2']
levelDictT25[str(freqSetLog[0])] = levelDictBeams[str(freqSetLog[0])]

# run (beam 1 and 2 for single set point)
freqSetLog = [28.0]
sw1 = r'v168_b48\2023-01-19_21-14-34_Minicalrig_calibration_1_QR440-0110-00048_28.0_25C'
sw2 = r'v194_b48\2023-01-21_01-05-23_Minicalrig_calibration_1_QR440-0110-00048_28.0_25C'
plot__evals(freqLog, 1, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams = levelDict
plot__evals(freqLog, 2, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams[str(freqSetLog[0])]['beam2'] = levelDict[str(freqSetLog[0])]['beam2']
levelDictT25[str(freqSetLog[0])] = levelDictBeams[str(freqSetLog[0])]

# run (beam 1 and 2 for single set point)
freqSetLog = [28.5]
sw1 = r'v168_b48\2023-01-19_21-26-07_Minicalrig_calibration_1_QR440-0110-00048_28.5_25C'
sw2 = r'v194_b48\2023-01-21_01-15-22_Minicalrig_calibration_1_QR440-0110-00048_28.5_25C'
plot__evals(freqLog, 1, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams = levelDict
plot__evals(freqLog, 2, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams[str(freqSetLog[0])]['beam2'] = levelDict[str(freqSetLog[0])]['beam2']
levelDictT25[str(freqSetLog[0])] = levelDictBeams[str(freqSetLog[0])]

# run (beam 1 and 2 for single set point)
freqSetLog = [29.0]
sw1 = r'v168_b48\2023-01-19_21-37-40_Minicalrig_calibration_1_QR440-0110-00048_29.0_25C'
sw2 = r'v194_b48\2023-01-21_01-25-21_Minicalrig_calibration_1_QR440-0110-00048_29.0_25C'
plot__evals(freqLog, 1, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams = levelDict
plot__evals(freqLog, 2, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams[str(freqSetLog[0])]['beam2'] = levelDict[str(freqSetLog[0])]['beam2']
levelDictT25[str(freqSetLog[0])] = levelDictBeams[str(freqSetLog[0])]

# run (beam 1 and 2 for single set point)
freqSetLog = [29.5]
sw1 = r'v168_b48\2023-01-19_21-49-04_Minicalrig_calibration_1_QR440-0110-00048_29.5_25C'
sw2 = r'v194_b48\2023-01-21_01-35-20_Minicalrig_calibration_1_QR440-0110-00048_29.5_25C'
plot__evals(freqLog, 1, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams = levelDict
plot__evals(freqLog, 2, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams[str(freqSetLog[0])]['beam2'] = levelDict[str(freqSetLog[0])]['beam2']
levelDictT25[str(freqSetLog[0])] = levelDictBeams[str(freqSetLog[0])]

# run (beam 1 and 2 for single set point)
freqSetLog = [30.0]
sw1 = r'v168_b48\2023-01-19_22-00-25_Minicalrig_calibration_1_QR440-0110-00048_30.0_25C'
sw2 = r'v194_b48\2023-01-21_01-45-20_Minicalrig_calibration_1_QR440-0110-00048_30.0_25C'
plot__evals(freqLog, 1, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams = levelDict
plot__evals(freqLog, 2, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams[str(freqSetLog[0])]['beam2'] = levelDict[str(freqSetLog[0])]['beam2']
levelDictT25[str(freqSetLog[0])] = levelDictBeams[str(freqSetLog[0])]

# run (beam 1 and 2 for single set point)
freqSetLog = [30.5]
sw1 = r'v168_b48\2023-01-19_22-11-48_Minicalrig_calibration_1_QR440-0110-00048_30.5_25C'
sw2 = r'v194_b48\2023-01-21_01-55-19_Minicalrig_calibration_1_QR440-0110-00048_30.5_25C'
plot__evals(freqLog, 1, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams = levelDict
plot__evals(freqLog, 2, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams[str(freqSetLog[0])]['beam2'] = levelDict[str(freqSetLog[0])]['beam2']
levelDictT25[str(freqSetLog[0])] = levelDictBeams[str(freqSetLog[0])]

# run (beam 1 and 2 for single set point)
freqSetLog = [31.0]
sw1 = r'v168_b48\2023-01-19_22-23-16_Minicalrig_calibration_1_QR440-0110-00048_31.0_25C'
sw2 = r'v194_b48\2023-01-21_02-05-18_Minicalrig_calibration_1_QR440-0110-00048_31.0_25C'
plot__evals(freqLog, 1, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams = levelDict
plot__evals(freqLog, 2, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams[str(freqSetLog[0])]['beam2'] = levelDict[str(freqSetLog[0])]['beam2']
levelDictT25[str(freqSetLog[0])] = levelDictBeams[str(freqSetLog[0])]




# 65 deg
levelDictT65 = {}

# run (beam 1 and 2 for single set point)
freqSetLog = [27.5]
sw1 = r'v168_b48\2023-01-19_22-34-47_Minicalrig_calibration_1_QR440-0110-00048_27.5_65C'
sw2 = r'v194_b48\2023-01-21_03-37-53_Minicalrig_calibration_1_QR440-0110-00048_27.5_65C'
plot__evals(freqLog, 1, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams = levelDict
plot__evals(freqLog, 2, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams[str(freqSetLog[0])]['beam2'] = levelDict[str(freqSetLog[0])]['beam2']
levelDictT65[str(freqSetLog[0])] = levelDictBeams[str(freqSetLog[0])]

# run (beam 1 and 2 for single set point)
freqSetLog = [28.0]
sw1 = r'v168_b48\2023-01-19_22-55-47_Minicalrig_calibration_1_QR440-0110-00048_28.0_65C'
sw2 = r'v194_b48\2023-01-21_03-53-41_Minicalrig_calibration_1_QR440-0110-00048_28.0_65C'
plot__evals(freqLog, 1, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams = levelDict
plot__evals(freqLog, 2, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams[str(freqSetLog[0])]['beam2'] = levelDict[str(freqSetLog[0])]['beam2']
levelDictT65[str(freqSetLog[0])] = levelDictBeams[str(freqSetLog[0])]

# run (beam 1 and 2 for single set point)
freqSetLog = [28.5]
sw1 = r'v168_b48\2023-01-19_23-12-08_Minicalrig_calibration_1_QR440-0110-00048_28.5_65C'
sw2 = r'v194_b48\2023-01-21_04-03-40_Minicalrig_calibration_1_QR440-0110-00048_28.5_65C'
plot__evals(freqLog, 1, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams = levelDict
plot__evals(freqLog, 2, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams[str(freqSetLog[0])]['beam2'] = levelDict[str(freqSetLog[0])]['beam2']
levelDictT65[str(freqSetLog[0])] = levelDictBeams[str(freqSetLog[0])]

# run (beam 1 and 2 for single set point)
freqSetLog = [29.0]
sw1 = r'v168_b48\2023-01-19_23-28-05_Minicalrig_calibration_1_QR440-0110-00048_29.0_65C'
sw2 = r'v194_b48\2023-01-21_04-13-39_Minicalrig_calibration_1_QR440-0110-00048_29.0_65C'
plot__evals(freqLog, 1, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams = levelDict
plot__evals(freqLog, 2, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams[str(freqSetLog[0])]['beam2'] = levelDict[str(freqSetLog[0])]['beam2']
levelDictT65[str(freqSetLog[0])] = levelDictBeams[str(freqSetLog[0])]

# run (beam 1 and 2 for single set point)
freqSetLog = [29.5]
sw1 = r'v168_b48\2023-01-19_23-43-52_Minicalrig_calibration_1_QR440-0110-00048_29.5_65C'
sw2 = r'v194_b48\2023-01-21_04-23-38_Minicalrig_calibration_1_QR440-0110-00048_29.5_65C'
plot__evals(freqLog, 1, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams = levelDict
plot__evals(freqLog, 2, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams[str(freqSetLog[0])]['beam2'] = levelDict[str(freqSetLog[0])]['beam2']
levelDictT65[str(freqSetLog[0])] = levelDictBeams[str(freqSetLog[0])]

# run (beam 1 and 2 for single set point)
freqSetLog = [30.0]
sw1 = r'v168_b48\2023-01-20_00-00-07_Minicalrig_calibration_1_QR440-0110-00048_30.0_65C'
sw2 = r'v194_b48\2023-01-21_04-33-37_Minicalrig_calibration_1_QR440-0110-00048_30.0_65C'
plot__evals(freqLog, 1, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams = levelDict
plot__evals(freqLog, 2, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams[str(freqSetLog[0])]['beam2'] = levelDict[str(freqSetLog[0])]['beam2']
levelDictT65[str(freqSetLog[0])] = levelDictBeams[str(freqSetLog[0])]

# run (beam 1 and 2 for single set point)
freqSetLog = [30.5]
sw1 = r'v168_b48\2023-01-20_00-15-34_Minicalrig_calibration_1_QR440-0110-00048_30.5_65C'
sw2 = r'v194_b48\2023-01-21_04-43-36_Minicalrig_calibration_1_QR440-0110-00048_30.5_65C'
plot__evals(freqLog, 1, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams = levelDict
plot__evals(freqLog, 2, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams[str(freqSetLog[0])]['beam2'] = levelDict[str(freqSetLog[0])]['beam2']
levelDictT65[str(freqSetLog[0])] = levelDictBeams[str(freqSetLog[0])]

# run (beam 1 and 2 for single set point)
freqSetLog = [31.0]
sw1 = r'v168_b48\2023-01-20_00-31-29_Minicalrig_calibration_1_QR440-0110-00048_31.0_65C'
sw2 = r'v194_b48\2023-01-21_04-53-35_Minicalrig_calibration_1_QR440-0110-00048_31.0_65C'
plot__evals(freqLog, 1, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams = levelDict
plot__evals(freqLog, 2, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams[str(freqSetLog[0])]['beam2'] = levelDict[str(freqSetLog[0])]['beam2']
levelDictT65[str(freqSetLog[0])] = levelDictBeams[str(freqSetLog[0])]




# 45 deg board 41
levelDictT45_b41 = {}

# run (beam 1 and 2 for single set point)
freqSetLog = [27.5]
sw1 = r'v168_b48\2023-01-18_16-37-30_Minicalrig_calibration_0_QR440-0110-00041_27.5_45C'
sw2 = r'v194_b48\2023-01-20_21-56-13_Minicalrig_calibration_0_QR440-0110-00041_27.5_45C'
plot__evals(freqLog, 1, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams = levelDict
plot__evals(freqLog, 2, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams[str(freqSetLog[0])]['beam2'] = levelDict[str(freqSetLog[0])]['beam2']
levelDictT45_b41[str(freqSetLog[0])] = levelDictBeams[str(freqSetLog[0])]

# run (beam 1 and 2 for single set point)
freqSetLog = [28.0]
sw1 = r'v168_b48\2023-01-18_16-50-08_Minicalrig_calibration_0_QR440-0110-00041_28.0_45C'
sw2 = r'v194_b48\2023-01-20_22-09-10_Minicalrig_calibration_0_QR440-0110-00041_28.0_45C'
plot__evals(freqLog, 1, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams = levelDict
plot__evals(freqLog, 2, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams[str(freqSetLog[0])]['beam2'] = levelDict[str(freqSetLog[0])]['beam2']
levelDictT45_b41[str(freqSetLog[0])] = levelDictBeams[str(freqSetLog[0])]

# run (beam 1 and 2 for single set point)
freqSetLog = [28.5]
sw1 = r'v168_b48\2023-01-18_17-01-57_Minicalrig_calibration_0_QR440-0110-00041_28.5_45C'
sw2 = r'v194_b48\2023-01-20_22-19-16_Minicalrig_calibration_0_QR440-0110-00041_28.5_45C'
plot__evals(freqLog, 1, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams = levelDict
plot__evals(freqLog, 2, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams[str(freqSetLog[0])]['beam2'] = levelDict[str(freqSetLog[0])]['beam2']
levelDictT45_b41[str(freqSetLog[0])] = levelDictBeams[str(freqSetLog[0])]

# run (beam 1 and 2 for single set point)
freqSetLog = [29.0]
sw1 = r'v168_b48\2023-01-18_17-13-48_Minicalrig_calibration_0_QR440-0110-00041_29.0_45C'
sw2 = r'v194_b48\2023-01-20_22-29-21_Minicalrig_calibration_0_QR440-0110-00041_29.0_45C'
plot__evals(freqLog, 1, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams = levelDict
plot__evals(freqLog, 2, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams[str(freqSetLog[0])]['beam2'] = levelDict[str(freqSetLog[0])]['beam2']
levelDictT45_b41[str(freqSetLog[0])] = levelDictBeams[str(freqSetLog[0])]

# run (beam 1 and 2 for single set point)
freqSetLog = [29.5]
sw1 = r'v168_b48\2023-01-18_17-25-31_Minicalrig_calibration_0_QR440-0110-00041_29.5_45C'
sw2 = r'v194_b48\2023-01-20_22-39-31_Minicalrig_calibration_0_QR440-0110-00041_29.5_45C'
plot__evals(freqLog, 1, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams = levelDict
plot__evals(freqLog, 2, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams[str(freqSetLog[0])]['beam2'] = levelDict[str(freqSetLog[0])]['beam2']
levelDictT45_b41[str(freqSetLog[0])] = levelDictBeams[str(freqSetLog[0])]

# run (beam 1 and 2 for single set point)
freqSetLog = [30.0]
sw1 = r'v168_b48\2023-01-18_17-37-11_Minicalrig_calibration_0_QR440-0110-00041_30.0_45C'
sw2 = r'v194_b48\2023-01-20_22-49-39_Minicalrig_calibration_0_QR440-0110-00041_30.0_45C'
plot__evals(freqLog, 1, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams = levelDict
plot__evals(freqLog, 2, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams[str(freqSetLog[0])]['beam2'] = levelDict[str(freqSetLog[0])]['beam2']
levelDictT45_b41[str(freqSetLog[0])] = levelDictBeams[str(freqSetLog[0])]

# run (beam 1 and 2 for single set point)
freqSetLog = [30.5]
sw1 = r'v168_b48\2023-01-18_17-48-46_Minicalrig_calibration_0_QR440-0110-00041_30.5_45C'
sw2 = r'v194_b48\2023-01-20_22-59-45_Minicalrig_calibration_0_QR440-0110-00041_30.5_45C'
plot__evals(freqLog, 1, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams = levelDict
plot__evals(freqLog, 2, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams[str(freqSetLog[0])]['beam2'] = levelDict[str(freqSetLog[0])]['beam2']
levelDictT45_b41[str(freqSetLog[0])] = levelDictBeams[str(freqSetLog[0])]

# run (beam 1 and 2 for single set point)
freqSetLog = [31.0]
sw1 = r'v168_b48\2023-01-18_18-00-20_Minicalrig_calibration_0_QR440-0110-00041_31.0_45C'
sw2 = r'v194_b48\2023-01-20_23-09-53_Minicalrig_calibration_0_QR440-0110-00041_31.0_45C'
plot__evals(freqLog, 1, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams = levelDict
plot__evals(freqLog, 2, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams[str(freqSetLog[0])]['beam2'] = levelDict[str(freqSetLog[0])]['beam2']
levelDictT45_b41[str(freqSetLog[0])] = levelDictBeams[str(freqSetLog[0])]





# level dict out
if Gain == True:
    levelDict_b48_Gain = {}
    levelDict_b48_Gain['T25'] = levelDictT25
    levelDict_b48_Gain['T45'] = levelDictT45
    levelDict_b48_Gain['T65'] = levelDictT65
    gainRun = True
if Gain == False:
    levelDict_b48_Phase = {}
    levelDict_b48_Phase['T25'] = levelDictT25
    levelDict_b48_Phase['T45'] = levelDictT45
    levelDict_b48_Phase['T65'] = levelDictT65
    phaseRun = True

# if 'gainRun' in locals() and 'phaseRun' in locals():
#     levelDict_b48 = {}
#     levelDict_b48['Gain'] = levelDict_b48_Gain
#     levelDict_b48['Phase'] = levelDict_b48_Phase
#     os.chdir('C:\codeRun\jsonFiles')
#     json.dump(levelDict_b48, open( "levelDict_b48.json", 'w' ) )


