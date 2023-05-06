import numpy as np
import os
import json
import csv
import pandas as pd
import matplotlib.pyplot as plt; plt.close('all')
import pickle

def find__measFiles(path, fileString, beam):
    global measFiles, files
    files = []
    for root, directories, file in os.walk(path):
    	for file in file:
    		if(file.endswith(".csv")):
    			files.append(os.path.join(root,file))
    measFiles = []
    for i in range(len(files)):
        if fileString in files[i] and 'eam' + str(beam) in files[i]:
            measFiles.append(files[i])
                      
def load__measFiles(filePath):
    global meas_info, meas_array, meas_frequencies, meas_params
    meas_params = {}
    meas_info = []
    # meas_info, array and measurement frequencies
    with open(filePath, 'r')as file:
        filecontent = csv.reader(file, delimiter=',')
        for row in filecontent:
            meas_info.append(row)
        index_start = [index for index in range(len(meas_info)) if 'barcodes' in meas_info[index]][0]+2
        meas_info = meas_info[0:index_start]
        meas_array = np.genfromtxt(filePath, delimiter=',', skip_header=index_start)
        meas_frequencies = np.array(meas_info[index_start-1])[::2].astype(float)
    # meas_params
    for i in range(len(meas_info)-1):
        if len(meas_info[i]) > 1:
            paramName = meas_info[i][0]
            if paramName[0:2] == '# ': paramName = paramName[2:]
            meas_params[paramName] = meas_info[i][1]
    # set frequency (as not in param table)
    meas_params['f_set'] = filePath.split('_')[-3]

filePath = r'C:\codeRun\SES_Terminal_Rx'
# parmas
beam = 1
limit = -24
find__measFiles(filePath, 'OP', beam)

f_sets = []
boardOffsets = []
countZeroLog = []
for k in range(len(measFiles)):
# for k in range(16):
    plt.figure()
    # OP file
    find__measFiles(filePath, 'OP', beam)
    load__measFiles(measFiles[k])
    gain = meas_array[:, ::2]; phase = meas_array[:,1:][:, ::2]
    forCol = (meas_frequencies-float(meas_params['f_set']))**2
    col = np.argmin(forCol)
    # print(float(meas_params['f_set']))
    gain_OP = gain[:, col]
    x = np.arange(1,len(gain)+1)
    plt.plot(x, gain_OP, label = 'OP')
    gain_OP_median = np.median(gain_OP)
    plt.hlines(gain_OP_median, min(x)-10, max(x)+10, linewidth=3, linestyle='-')
    
    # RFA file 
    find__measFiles(filePath, 'RFA', beam)
    load__measFiles(measFiles[k])
    gain = meas_array[:, ::2]; phase = meas_array[:,1:][:, ::2]
    forCol = (meas_frequencies-float(meas_params['f_set']))**2
    col = np.argmin(forCol)
    gain_RFA = gain[:, col]
    x = np.arange(1,len(gain)+1)
    plt.plot(x, gain_RFA, label = 'RFA')
    gain_RFA_median = np.median(gain_RFA)
    plt.hlines(gain_RFA_median, min(x)-10, max(x)+10, linewidth=3, linestyle='-', color='orange')
    
    # OP - RFA
    # gain_diff = gain_OP - gain_RFA
    gain_diff = (gain_OP*0.0+gain_OP_median) - (gain_RFA*0.0+gain_RFA_median)
    plt.plot(x, gain_diff, label = 'Diff-Offset')
    
    # Offset parameter
    gain_offset = gain_diff - limit
    plt.plot(x, gain_offset, label = 'Offset')
    
    # New RFA
    gain_RFA_prime = gain_RFA - np.abs(gain_offset)
    gain_RFA_out = gain*1.0 - np.mean(gain_offset)
    for p in range(len(gain_RFA_out)):
        for q in range(gain_RFA_out.shape[1]):
            if gain_RFA_out[p, q] < 0.0:
                gain_RFA_out[p, q] = gain_RFA_out[p, q]*0.0
    plt.plot(x, gain_RFA_out[:, col], label = 'RFA new')
    
    plt.legend()
    plt.xlabel('port')
    plt.ylabel('dB')
    plt.ylim([-40,100])
    plt.xlim(min(x)-10, max(x)+10)
    plt.title(meas_params['barcodes'] + ', beam ' + str(beam) + ', f_set = ' + str(float(meas_params['f_set'])) + ', OFFSET = ' + str(limit) + ' dB')
    plt.grid()
    plt.savefig('C:\Scratch\\' + measFiles[k].split('\\')[-1][0:-3] + ', OFFSET = ' + str(limit) + ' dB' + '.png', dpi=200)
    
    # merge back
    meas_info_list = meas_info.copy()
    meas_array_corrected = meas_array.copy()*0.0
    for m in range(gain.shape[1]):
        meas_array_corrected[:,2*m] = gain_RFA_out[:,m]
        meas_array_corrected[:,2*m+1] = phase[:,m]
    for o in range(len(meas_array_corrected)):
        meas_info_list.append(list(meas_array_corrected[o,:]))
        
    # write new file
    file = open('C:\Scratch\\' + measFiles[k].split('\\')[-1][0:-3] + '_HFSS-f-offset-v2.csv', 'w+', newline ='') 
    with file:     
        write = csv.writer(file) 
        write.writerows(meas_info_list)
    
    f_sets.append(float(meas_params['f_set']))
    boardOffsets.append(np.mean(gain_offset))
    countZeroLog.append(np.count_nonzero(gain_RFA_out[:, col]))
    plt.close('all')
    
plt.figure()
plt.plot(f_sets, boardOffsets, 'o')
plt.xlabel('f [GHz]'); plt.ylabel('offset [dB]')

plt.figure()
plt.plot(f_sets, countZeroLog, 'o')
plt.xlabel('f [GHz]'); plt.ylabel('non zero ports')
plt.ylim([0,456])

























import numpy as np
import os
import json
import csv
import pandas as pd
import matplotlib.pyplot as plt; plt.close('all')
import pickle

def find__measFiles(path, fileString, beam):
    global measFiles, files
    files = []
    for root, directories, file in os.walk(path):
    	for file in file:
    		if(file.endswith(".csv")):
    			files.append(os.path.join(root,file))
    measFiles = []
    for i in range(len(files)):
        if fileString in files[i] and 'eam' + str(beam) in files[i]:
            measFiles.append(files[i])
                      
def load__measFiles(filePath):
    global meas_info, meas_array, meas_frequencies, meas_params
    meas_params = {}
    meas_info = []
    # meas_info, array and measurement frequencies
    with open(filePath, 'r')as file:
        filecontent = csv.reader(file, delimiter=',')
        for row in filecontent:
            meas_info.append(row)
        index_start = [index for index in range(len(meas_info)) if 'barcodes' in meas_info[index]][0]+2
        meas_info = meas_info[0:index_start]
        meas_array = np.genfromtxt(filePath, delimiter=',', skip_header=index_start)
        meas_frequencies = np.array(meas_info[index_start-1])[::2].astype(float)
    # meas_params
    for i in range(len(meas_info)-1):
        if len(meas_info[i]) > 1:
            paramName = meas_info[i][0]
            if paramName[0:2] == '# ': paramName = paramName[2:]
            meas_params[paramName] = meas_info[i][1]
    # set frequency (as not in param table)
    meas_params['f_set'] = filePath.split('_')[-3]

filePath = r'C:\codeRun\SES_Terminal_Rx'
# parmas
beam = 2
limit = -24
find__measFiles(filePath, 'OP', beam)

f_sets = []
boardOffsets = []
countZeroLog = []
for k in range(len(measFiles)):
# for k in range(16):
    plt.figure()
    # OP file
    find__measFiles(filePath, 'OP', beam)
    load__measFiles(measFiles[k])
    gain = meas_array[:, ::2]; phase = meas_array[:,1:][:, ::2]
    forCol = (meas_frequencies-float(meas_params['f_set']))**2
    col = np.argmin(forCol)
    # print(float(meas_params['f_set']))
    gain_OP = gain[:, col]
    x = np.arange(1,len(gain)+1)
    plt.plot(x, gain_OP, label = 'OP')
    gain_OP_median = np.median(gain_OP)
    plt.hlines(gain_OP_median, min(x)-10, max(x)+10, linewidth=3, linestyle='-')
    
    # RFA file 
    find__measFiles(filePath, 'RFA', beam)
    load__measFiles(measFiles[k])
    gain = meas_array[:, ::2]; phase = meas_array[:,1:][:, ::2]
    forCol = (meas_frequencies-float(meas_params['f_set']))**2
    col = np.argmin(forCol)
    gain_RFA = gain[:, col]
    x = np.arange(1,len(gain)+1)
    plt.plot(x, gain_RFA, label = 'RFA')
    gain_RFA_median = np.median(gain_RFA)
    plt.hlines(gain_RFA_median, min(x)-10, max(x)+10, linewidth=3, linestyle='-', color='orange')
    
    # OP - RFA
    # gain_diff = gain_OP - gain_RFA
    gain_diff = (gain_OP*0.0+gain_OP_median) - (gain_RFA*0.0+gain_RFA_median)
    plt.plot(x, gain_diff, label = 'Diff-Offset')
    
    # Offset parameter
    gain_offset = gain_diff - limit
    plt.plot(x, gain_offset, label = 'Offset')
    
    # New RFA
    gain_RFA_prime = gain_RFA - np.abs(gain_offset)
    gain_RFA_out = gain*1.0 - np.mean(gain_offset)
    for p in range(len(gain_RFA_out)):
        for q in range(gain_RFA_out.shape[1]):
            if gain_RFA_out[p, q] < 0.0:
                gain_RFA_out[p, q] = gain_RFA_out[p, q]*0.0
    plt.plot(x, gain_RFA_out[:, col], label = 'RFA new')
    
    plt.legend()
    plt.xlabel('port')
    plt.ylabel('dB')
    plt.ylim([-40,100])
    plt.xlim(min(x)-10, max(x)+10)
    plt.title(meas_params['barcodes'] + ', beam ' + str(beam) + ', f_set = ' + str(float(meas_params['f_set'])) + ', OFFSET = ' + str(limit) + ' dB')
    plt.grid()
    plt.savefig('C:\Scratch\\' + measFiles[k].split('\\')[-1][0:-3] + ', OFFSET = ' + str(limit) + ' dB' + '.png', dpi=200)
    
    # merge back
    meas_info_list = meas_info.copy()
    meas_array_corrected = meas_array.copy()*0.0
    for m in range(gain.shape[1]):
        meas_array_corrected[:,2*m] = gain_RFA_out[:,m]
        meas_array_corrected[:,2*m+1] = phase[:,m]
    for o in range(len(meas_array_corrected)):
        meas_info_list.append(list(meas_array_corrected[o,:]))
        
    # write new file
    file = open('C:\Scratch\\' + measFiles[k].split('\\')[-1][0:-3] + '_HFSS-f-offset-v2.csv', 'w+', newline ='') 
    with file:     
        write = csv.writer(file) 
        write.writerows(meas_info_list)
    
    f_sets.append(float(meas_params['f_set']))
    boardOffsets.append(np.mean(gain_offset))
    countZeroLog.append(np.count_nonzero(gain_RFA_out[:, col]))
    plt.close('all')
    
plt.figure()
plt.plot(f_sets, boardOffsets, 'o')
plt.xlabel('f [GHz]'); plt.ylabel('offset [dB]')

plt.figure()
plt.plot(f_sets, countZeroLog, 'o')
plt.xlabel('f [GHz]'); plt.ylabel('non zero ports')
plt.ylim([0,456])

























