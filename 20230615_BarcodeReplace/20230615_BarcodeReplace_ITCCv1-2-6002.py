import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import csv
import pickle

# inputs
filePath = r'C:\Users\JamieMitchell\Downloads\Batch_1_RFC\Batch_1'
bc1_Replace = '440'
bc2_Replace = '0238'
txrx = 'tx'

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
        if fileString in files[i]:
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
        
    meas_params
    for i in range(len(meas_info) - 1):
        if len(meas_info[i]) > 1:
            paramName = meas_info[i][0]
            # print(paramName)
            if paramName[0:2] == '# ':
                paramName = paramName[2:]
            meas_params[paramName] = meas_info[i][1]
            print('hh'+meas_params[paramName])
            if len(meas_params[paramName])>1:
                if meas_params[paramName][0] == ' ':
                    meas_params[paramName] = meas_params[paramName][1:]
            
            
## run ##

# check barcode
fileTypes = ['RFC']
for fileType in fileTypes:
    find__measFiles(filePath, fileType)
    for measFile in measFiles:
        find__fileDetails(measFile)
        barcodeOLD = meas_params['barcodes']
        bc1 = meas_params['barcodes'].split('-')[0]
        bc2 = meas_params['barcodes'].split('-')[1]
        bc3 = meas_params['barcodes'].split('-')[2]
        bc1 = bc1_Replace
        bc2 = bc2_Replace
        bc3 = bc3[-4:]
        barcodeNEW = bc1 + '-' + bc2 + '-0' + bc3
        
        # change barcode
        if barcodeNEW != barcodeOLD:
            meas_infoNEW = meas_info
            meas_infoNEW[27][1] = barcodeNEW
            
            meas_array_list = meas_infoNEW.copy()
            for k in range(len(meas_array)):
                meas_array_list.append(list(meas_array[k,:]))
                
            # new fileName
            measFileNEW = measFile[0:measFile.find('_QR')+len('_QR')] + barcodeNEW + measFile[measFile.find('_'+txrx):]
            
            # write new file
            file = open(measFileNEW, 'w+', newline ='') 
            with file:
                write = csv.writer(file) 
                write.writerows(meas_array_list)
                
            # delete old file
            os.remove(measFile)
