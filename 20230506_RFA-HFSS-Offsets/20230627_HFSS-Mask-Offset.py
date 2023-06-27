import numpy
import csv
import os
import numpy as np

filePath = r'C:\Scratch\20230627_offsetFiles'

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
            
hfss_offs = np.genfromtxt('Rx_hfss_offset_13mm_Cal.csv', delimiter=',', skip_header=1)
            
find__measFiles(filePath, 'RFA')
for measFile in measFiles:
    find__fileDetails(measFile)
    newGain = meas_array_gain.copy()
    for i in range(len(meas_frequencies)):
        f_c = float(meas_params['f_c'])
        row = np.argmin((hfss_offs[:,0]-f_c)**2)
        col = int(meas_params['Beam']); print(col)
        newGain[:,i] = newGain[:,i] - hfss_offs[row, col]
        
    meas_array_new = np.zeros_like(meas_array)
    for j in range(meas_array_gain.shape[1]):
        meas_array_new[:,2*j] = newGain[:,j]
        meas_array_new[:,2*j+1] = meas_array_phase[:,j]
    meas_array_new_list = meas_info.copy()
    for k in range(len(meas_array_new)):
        meas_array_new_list.append(list(meas_array_new[k,:]))
    # write new file
    file = open(measFile[0:-4] + '-HFSSmaskOff.csv', 'w+', newline ='') 
    with file:
        write = csv.writer(file) 
        write.writerows(meas_array_new_list)
    