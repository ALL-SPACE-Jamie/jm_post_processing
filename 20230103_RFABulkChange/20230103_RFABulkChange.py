import pandas as pd
import numpy as np
import os
import glob
import csv

freqIns = 'Y'
phaseFlip = 'N'

# directory
dirScript = os.getcwd()

# files in
os.chdir(os.path.join(dirScript, 'TxIN'))
fileLog = glob.glob('*RFA*.csv')

for i in range(len(fileLog)):
    # open file
    csvFile = []
    with open(fileLog[i],'r')as file:
       filecontent=csv.reader(file,delimiter=',')
       for row in filecontent:
          csvFile.append(row)
          
    # append new info
    if freqIns == 'Y':
        freq = fileLog[i].split('_')[-3]
        csvFile.insert(1, ['cal_frequency:', freq])
    
    # phase reverse
    if phaseFlip == 'Y':
        for j in range(len(csvFile)-23):
            if (j % 2) == 1:
                row = csvFile[j+23]
                for k in range(len(row)):
                    if (k % 2) == 1:
                        newPhase = float(row[k])+180.0
                        if newPhase > 360.0:
                            newPhase = newPhase - 360.0
                        row[k] = str(newPhase)
    
    # files out
    os.chdir(os.path.join(dirScript, 'TxOUT'))
    
    # write new file
    file = open(fileLog[i][0:-4] + '_freqIns' + freqIns + '_ph180' + phaseFlip + '.csv', 'w+', newline ='') 
    with file:     
        write = csv.writer(file) 
        write.writerows(csvFile) 
        
    # files in
    os.chdir(os.path.join(dirScript, 'TxIN'))
    