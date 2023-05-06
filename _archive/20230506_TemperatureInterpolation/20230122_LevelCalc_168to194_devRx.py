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
freqLog = [17.7]
boardType = 'Rx'
Gain = True

# 45 deg
levelDictT45 = {}

# run (beam 1 and 2 for single set point)
freqSetLog = [17.7]
sw1 = r'Rxv168_b53\2023-01-14_19-27-47_Minicalrig_calibration_0_QR440-0111-00053_17.7_45C'
sw2 = r'Rxv194_b53\2023-01-21_00-41-52_Minicalrig_calibration_1_QR440-0111-00053_17.7_45C'
plot__evals(freqLog, 1, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams = levelDict
plot__evals(freqLog, 2, boardType, -45, 90, 20, freqSetLog[0], sw1, sw2, Gain)
levelDictBeams[str(freqSetLog[0])]['beam2'] = levelDict[str(freqSetLog[0])]['beam2']
levelDictT45[str(freqSetLog[0])] = levelDictBeams[str(freqSetLog[0])]
