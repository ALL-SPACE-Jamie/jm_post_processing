import pandas as pd
import numpy as np
import matplotlib.pyplot as plt; plt.rcParams['font.size'] = 18
import os
import glob
import copy
import csv
plt.close('all')

# file path
dirScript = os.getcwd()
# example file path with sync to SharePoint: 'C:\Users\JamieMitchell\OneDrive - ALL.SPACE\Desktop\sort\_readyGH\Rx Comparisons\20230116_Evaluations'
filePath = 'C:\Users\JamieMitchell\OneDrive - ALL.SPACE\Desktop\sort\_readyGH\Rx Comparisons\20230116_Evaluations'

# definitions
def plot__evals(freqLog, beam, boardType):
    global avLog, avLogFreqs, freqs, folders, stdLogFreqs, array
    avLogFreqs = []
    stdLogFreqs = []
    for freq in freqLog:
        avLog = []
        stdLog = []
        os.chdir(filePath)
        
        folders = next(os.walk(filePath))[1]
        
        # Beam 1
        foldersLog = []
        csvFiles = []
        for folder in folders:
            filePathFolder = filePath + '/' + folder
            if boardType == 'Rx':
                filePathFolder = filePathFolder + '/Iteration_1'
            os.chdir(filePathFolder)
            csvFileLog = glob.glob('*.csv')
            for file in csvFileLog:
                if 'OP' in file:
                    if 'Beam' + str(beam) in file:
                        csvFiles.append(file)
                        foldersLog.append(folder)
                                      
        os.chdir(filePath)
        pltarray = []
        investLog = []
        plt.figure(figsize=(12,7))
        for i in range(len(csvFiles)):
            filePathFolder = filePath + '/' + foldersLog[i]
            if boardType == 'Rx':
                filePathFolder = filePathFolder + '/Iteration_1'
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
                    plt.plot(x,array[:,col],label=foldersLog[i][0:-3])
                    investLog.append(np.mean(array[:,col]))
                    avLog.append(np.average(array[:, col]))
                    stdLog.append(np.std(array[:, col]))
        avLogFreqs.append(avLog)
        stdLogFreqs.append(stdLog)
                
        plt.xlabel('port'); plt.ylabel('Gain [dB]')
        plt.grid('on')
        plt.legend(loc='upper center',fontsize=8, ncol=2)
        plt.ylim([-80,0])
        title = boardType + 'TLM board evaluations (' + str(freqMeas) + ' GHz - beam ' + str(beam) + ')'
        plt.title(title)
        plt.savefig(filePath[0:-5] + "\\figures\\" + title + '.png')
        
## RUN
# params
freqLog = [17.7, 17.8, 17.9, 18. , 18.1, 18.2, 18.3, 18.4, 18.5, 18.6, 18.7,
       18.8, 18.9, 19. , 19.1, 19.2, 19.3, 19.4, 19.5, 19.6, 19.7, 19.8,
       19.9, 20. , 20.1, 20.2, 20.3, 20.4, 20.5, 20.6, 20.7, 20.8, 20.9,
       21. , 21.1, 21.2]
freqLog = [17.7,18.7,19.2,19.7,20.7]
#freqLog = [27.5,28.5,29.5,30,30.5]
beam = 1
boardType = 'Rx'

# run
plot__evals(freqLog, beam, boardType)

# overview plot
for i in range(len(folders)):
    if boardType == 'Rx':
        folders[i] = folders[i].split(' ')[2]
    if boardType == 'Tx':
        folders[i] = folders[i].split('_')[5]

plt.figure(figsize=(7,6))
for i in range(len(avLogFreqs)):
    plt.errorbar(folders,avLogFreqs[i],yerr=stdLogFreqs[i],marker='o',linestyle = ' ' ,label = 'f = ' + str(freqLog[i]) + ' GHz')
    
plt.xticks(rotation=90)
plt.xlabel('board'); plt.ylabel('Average Gain [dB]')
plt.yticks([-80,-70,-60,-50,-40,-30,-20,-10,0])
plt.grid('on')
plt.legend(loc='upper center',fontsize=8, ncol=2)
plt.ylim([-70,-10])
plt.title('Beam ' + str(beam))
plt.tight_layout()
plt.savefig(filePath[0:-5] + "\\figures\\" + boardType + '_beam' + str(beam) + '_Overview.png')


    
    
    
    