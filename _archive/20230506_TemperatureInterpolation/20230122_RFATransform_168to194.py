import numpy as np
import os
import json
import csv
import math

# definitions

def find__OPfiles(path):
    global filesRFA
    files = []
    for root, directories, file in os.walk(path):
    	for file in file:
    		if(file.endswith(".csv")):
    			files.append(os.path.join(root,file))
    filesRFA = []
    for i in range(len(files)):
        if 'OP' in files[i]:
            filesRFA.append(files[i])
            
def find__OTAfiles(path):
    global filesOTAL1, filesOTAL2, filesOTAL3
    files = []
    for root, directories, file in os.walk(path):
    	for file in file:
    		if(file.endswith(".acal")):
    			files.append(os.path.join(root,file))
    filesOTAL1 = []
    filesOTAL2 = []
    filesOTAL3 = []
    for i in range(len(files)):
        if 'lensN01' in files[i]:
            filesOTAL1.append(files[i])
            filesOTAL2.append(files[i])
            filesOTAL3.append(files[i])    
            
def load__JSON(path, jsonIN):
    global levelDictLoad
    os.chdir(path)
    levelDictLoad = json.load(open(jsonIN, 'r'))    

def analyse__RFAparams(filesRFA):
    global RFAparamDict
    RFAparamDict = {}
    log_fileName = []
    log_temperature = []
    log_f_set = []
    log_beam = []
    for i in range(len(filesRFA)):
        fileName = filesRFA[i].split('\\')[-1]
        log_fileName.append(fileName)
        log_temperature.append(fileName.split('_')[-1][0:-5])
        log_f_set.append(fileName.split('_')[11])
        log_beam.append(fileName.split('_')[5][-1])
    RFAparamDict['fileNames'] = log_fileName
    RFAparamDict['temperatures'] = log_temperature
    RFAparamDict['f_sets'] = log_f_set
    RFAparamDict['beams'] = log_beam
    
def load__RFA(filePath):
    global meas_info, meas_array, f_measPoints
    meas_info = []
    with open(filePath, 'r')as file:
        filecontent = csv.reader(file, delimiter=',')
        for row in filecontent:
            meas_info.append(row)
        meas_info = meas_info[0:22]
        meas_array = np.genfromtxt(filePath, delimiter=',', skip_header=22)
        f_measPoints = np.array(meas_info[21])[::2].astype(float)

def fix__RFAfile(m):
    global meas_array_fix
    countG = 0
    countPh = 0
    meas_array_fix = meas_array.copy()
    for p in range(len(f_measPoints)*2):
        if p % 2 == 0:
            colFix = meas_array[:, p]
            l1 = colFix[0:int(len(colFix)/3)]
            l2 = colFix[int(len(colFix)/3):int(2*len(colFix)/3)]
            l3 = colFix[2*int(len(colFix)/3):int(3*len(colFix)/3)]
            var1 = 'Gain'
            var2 = 'T' + RFAparamDict['temperatures'][m]
            var3 = RFAparamDict['f_sets'][m]
            var4 = 'beam' + RFAparamDict['beams'][m]
            var5 = str(f_measPoints[countG])
            countG= countG + 1
            level1 = levelDictLoad[var1][var2][var3][var4][var5]['L1']
            level2 = levelDictLoad[var1][var2][var3][var4][var5]['L2']
            level3 = levelDictLoad[var1][var2][var3][var4][var5]['L3']
            l1new = l1 + level1
            l2new = l2 + level2
            l3new = l3 + level3
            colReplace = np.transpose(np.hstack([l1new, l2new, l3new]))
            meas_array_fix[:, p] = colReplace
        else:
            colFix = meas_array[:, p]
            l1 = colFix[0:int(len(colFix)/3)]
            l2 = colFix[int(len(colFix)/3):int(2*len(colFix)/3)]
            l3 = colFix[2*int(len(colFix)/3):int(3*len(colFix)/3)]
            var1 = 'Phase'
            var2 = 'T' + RFAparamDict['temperatures'][m]
            var3 = RFAparamDict['f_sets'][m]
            var4 = 'beam' + RFAparamDict['beams'][m]
            var5 = str(f_measPoints[countPh])
            countPh = countPh + 1
            level1 = levelDictLoad[var1][var2][var3][var4][var5]['L1']
            level2 = levelDictLoad[var1][var2][var3][var4][var5]['L2']
            level3 = levelDictLoad[var1][var2][var3][var4][var5]['L3']
            l1new = l1 + level1
            l2new = l2 + level2
            l3new = l3 + level3
            colReplace = np.transpose(np.hstack([l1new, l2new, l3new]))
            for h in range(len(colReplace)):
                if colReplace[h] > 360.0:
                    colReplace[h] = colReplace[h] -360.0
                if colReplace[h] < 0.0:
                    colReplace[h] = colReplace[h] + 360.0
            meas_array_fix[:, p] = colReplace

def save__newRFA(pathOUT, j):
    np2list = []
    listArrays = list(meas_array_fix)
    for i in range(len(listArrays)):
        np2list.append(list(listArrays[i]))
    fixedList = meas_info + np2list
    file = open(pathOUT + RFAparamDict['fileNames'][j][0:-4] + '_168to194' + '.csv', 'w+', newline ='') 
    with file:     
        write = csv.writer(file) 
        write.writerows(fixedList)
        


## RUN
find__OPfiles(r'C:\codeRun\20230121_data\OneDrive_1_21-01-2023\TX_Thermal_Cal_168_EV7')
find__OTAfiles(r'C:\codeRun\20230121_data\OneDrive_1_21-01-2023\TX_Thermal_Cal_168_EV7')
load__JSON(r'C:\codeRun\jsonFiles', 'levelDict_b48.json')
analyse__RFAparams(filesRFA)

for j in range(len(filesRFA)):
    load__RFA(filesRFA[j])
    fix__RFAfile(j)
    save__newRFA('C:\codeRun\outFiles\\', j)
    print(str(int(round((100*float(j)/float(len(filesRFA))),0))) + '%')

# meas_array_fix_ReIm = meas_array_fix*1.0
# for i in range(int(meas_array_fix.shape[1]/2)):
#     forConvert = meas_array_fix[:, i*2:(i*2)+2]*1.0
#     for k in range(len(forConvert)):
#         Re = np.cos(forConvert[k,1]*np.pi/180.0)*10**(forConvert[k,0]/20.0)
#         Im = np.sin(forConvert[k,1]*np.pi/180.0)*10**(forConvert[k,0]/20.0)
#         forConvert[k,0] = Re*1.0
#         forConvert[k,1] = Im*1.0
#     meas_array_fix_ReIm[:, i*2:(i*2)+2] = forConvert*1.0
# meas_array_fix_ReImL1 = meas_array_fix_ReIm[0:int(len(meas_array_fix_ReIm)/3)]
# meas_array_fix_ReImL2 = meas_array_fix_ReIm[int(len(meas_array_fix_ReIm)/3):int(2*len(meas_array_fix_ReIm)/3)]
# meas_array_fix_ReImL3 = meas_array_fix_ReIm[2*int(len(meas_array_fix_ReIm)/3):int(3*len(meas_array_fix_ReIm)/3)]









