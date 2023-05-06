import pandas as pd
import numpy as np
import os
import glob
import csv

freqIns = 'N'
freqStartEndIns = 'N'
phaseFlip = 'Y'

# directory
dirScript = os.getcwd()

# files in
os.chdir(os.path.join(dirScript, 'C:\\codeRun\\_____run\\E5_RFAs\\E5_Thermal_Cal_Tx\\E5_Thermal_Cal'))
fileLog = glob.glob('*RFA*.csv')

for i in range(len(fileLog)):
    # open file
    csvFile = []
    with open(fileLog[i], 'r') as file:
        filecontent = csv.reader(file, delimiter=',')
        for row in filecontent:
            csvFile.append(row)

    # append new info
    if freqIns == 'Y':
        freq = fileLog[i].split('_')[-3]
        csvFile.insert(1, ['cal_frequency:', freq])
    if freqStartEndIns == 'Y':
        f_s = 27.5
        f_e = 31.0
        csvFile.insert(11, ['f_s', f_s])
        csvFile.insert(12, ['f_e', f_e])

    # phase reverse
    header_offset = 24
    print(len(csvFile))
    if phaseFlip == 'Y':
        for j in range(len(csvFile) - header_offset):
            if (j % 2) == 1:
                row = csvFile[j + header_offset]
                for k in range(len(row)):
                    if (k % 2) == 1:
                        newPhase = float(row[k]) + 180.0
                        if newPhase > 360.0:
                            newPhase = newPhase - 360.0
                        row[k] = str(newPhase)

    # files out
    os.chdir(os.path.join(dirScript, 'C:\\codeRun\\_____run\\E5_RFAs\\E5_Thermal_Cal_Tx\\E5_Thermal_Cal_PhaseFlip'))

    # write new file
    file = open(
        fileLog[i][0:-4] + '_freqIns' + freqIns + '_ph180' + phaseFlip + '_fStartEnd' + freqStartEndIns + '.csv', 'w+',
        newline='')
    with file:
        write = csv.writer(file)
        write.writerows(csvFile)

        # files in
    os.chdir(os.path.join(dirScript, 'C:\\codeRun\\_____run\\E5_RFAs\\E5_Thermal_Cal_Tx\\E5_Thermal_Cal'))