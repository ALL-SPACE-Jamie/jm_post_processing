import numpy as np
import os
import json
import csv
import pandas as pd
import matplotlib.pyplot as plt; plt.close('all')
import pickle

# import JSON
with open("Tx_Temperature_Dependancies_20230209_SES.pickle", "rb") as file:
    loaded_dict = pickle.load(file)
    
# definitions

def find__RFAfiles(path):
    global filesRFA
    files = []
    for root, directories, file in os.walk(path):
    	for file in file:
    		if(file.endswith(".csv")):
    			files.append(os.path.join(root,file))
    filesRFA = []
    for i in range(len(files)):
        if 'RFA' in files[i]:
            filesRFA.append(files[i])
            
def analyse__RFAparams(filesRFA):
    global RFAparamDict
    RFAparamDict = {}
    log_fileName = []
    log_temperature = []
    log_f_set = []
    log_beam = []
    log_board = []
    for i in range(len(filesRFA)):
        fileName = filesRFA[i].split('\\')[-1]
        log_fileName.append(fileName)
        log_temperature.append(fileName.split('_')[-1][0:-5])
        log_f_set.append(fileName.split('_')[11])
        log_beam.append(fileName.split('_')[5][-1])
        log_board.append(fileName.split('_')[4])
    RFAparamDict['fileNames'] = log_fileName
    RFAparamDict['temperatures'] = log_temperature
    RFAparamDict['f_sets'] = log_f_set
    RFAparamDict['beams'] = log_beam
    RFAparamDict['boards'] = log_board
    RFAparamDict['filePaths'] = filesRFA
    
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
        
## run
find__RFAfiles('C:\codeRun\_TemperatureInterpolation\_files\RFAIN')
analyse__RFAparams(filesRFA)
stop
df = pd.DataFrame.from_dict(RFAparamDict)
fileNames = list(set(RFAparamDict['fileNames']))

T = 65

for i in range(len(fileNames)):
    # select relevant column from dataframe
    dfSelect = df[df['fileNames'] == fileNames[i]]
    if len(dfSelect) != 1:
        print('Two cals saved that are the same')
        
    # load RFA file
    load__RFA(list(dfSelect['filePaths'])[0])
    
    # split into gain and phase
    gain = meas_array[:, ::2]
    phase = meas_array[:,1:][:, ::2]
    
    # offsets
    gainT = gain.copy()*1.0
    phaseT = phase.copy()*1.0
    for j in range(len(meas_array)): #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! NOT CORRECT
        beam = meas_info[16][1]
        f_set = meas_info[10][1]
        
        # gain offset
        z = loaded_dict['gain']['beam' + beam[1]]['port' + str(j+1)]['f_set=' + f_set[1:] + 'GHz']
        gain_offset = z[0]*T**2 + z[1]*T + z[2]
        gainT[j,:] = gainT[j,:] + gain_offset
        
        # phase offset
        z = loaded_dict['phase']['beam' + beam[1]]['port' + str(j+1)]['f_set=' + f_set[1:] + 'GHz']
        phase_offset = z[0]*T**2 + z[1]*T + z[2]
        phaseT[j,:] = phaseT[j,:] + phase_offset
        # wrap phase
        for k in range(len(phaseT)):
            for l in range(phaseT.shape[1]):
                if phaseT[k][l] > 360.0:
                    phaseT[k][l] = phaseT[k][l] - 360.0
                if phaseT[k][l] < 0.0:
                    phaseT[k][l] = phaseT[k][l] + 360.0
                    
    # merge back
    meas_arrayT_list = meas_info.copy()
    meas_arrayT = meas_array.copy()*0.0
    for m in range(gainT.shape[1]):
        meas_arrayT[:,2*m] = gainT[:,m]
        meas_arrayT[:,2*m+1] = phaseT[:,m]
    for o in range(len(meas_arrayT)):
        meas_arrayT_list.append(list(meas_arrayT[o,:]))
        
    # insert new temperature
    meas_arrayT_list[18][1] = str(T)
    
    # write new file
    file = open('C:\\codeRun\\Rx_SES_newRFA\\' + fileNames[i][0:-4] + '-' + str(T) + 'C.csv', 'w+', newline ='') 
    with file:     
        write = csv.writer(file) 
        write.writerows(meas_arrayT_list)
    print(str(i+1) + '/' + str(len(fileNames)))