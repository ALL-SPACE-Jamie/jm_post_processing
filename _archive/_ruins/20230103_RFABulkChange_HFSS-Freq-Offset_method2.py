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

filePath = r'C:\codeRun\SES_Terminal_Tx'
# parmas
beam = 1
f_low = 28.2; f_high = 29.5
limit = 15
# find all meas files
find__measFiles(filePath, 'OP', beam)
load__measFiles(measFiles[0])
gain = meas_array[:, ::2]
phase = meas_array[:,1:][:, ::2]
plt.plot(meas_frequencies,gain[0,:], label='1) OP file')
plt.vlines(f_low,-50,50,'r'); plt.vlines(f_high,-50,50,'r')
plt.ylim([-10,50])
gainFlat = gain.copy()
atts = meas_frequencies.copy()*0.0
for i in range(np.shape(gain)[1]):
    if f_low-0.01 < meas_frequencies[i] < f_high+0.01:
        gainFlat[0, i] = limit
        atts[i] = gain[0, i] - limit

plt.plot(meas_frequencies, gainFlat[0,:], label='2) OP diff calc')
plt.plot(meas_frequencies, atts, label='3) (1)-(2)')

find__measFiles(filePath, 'RFA', beam)
load__measFiles(measFiles[0])
gain = meas_array[:, ::2]
phase = meas_array[:,1:][:, ::2]
plt.plot(meas_frequencies, gain[0,:], 'k', label='4) RFA file')

gainRFACorr = gain[0,:]+atts
plt.plot(meas_frequencies, gainRFACorr, 'k--', label='5) RFA corrected')


plt.legend()
plt.xlabel('f [GHz]')
plt.ylabel('dB')
plt.grid()
plt.title('port 1 corrected RFA file')




























































stop


portFailDict = {}
f_set_Log = [27.5,28.0,28.5,29.0,29.5,30.0,30.5,31.0]
f_set_Log = [17.7,18.2,18.7,19.2,19.7,20.2,20.7,21.2]
for f_set in f_set_Log:
    ## RUN
    # f_set = 29.0
    filePath = r'C:\codeRun\Tx_processed\processed'
    filePath = r'C:\codeRun\rx-processed'
    find__RFAfiles(filePath, f_set, 2)
    analyse__RFAparams(filesRFA)
    
    ## Collate values and find global offsets
    minValLog = []
    stdLog = []
    medianLog = []
    badPortsLog = []
    boardLog = []
    for j in range(len(filesRFA)):
    # for j in range(5):
        fig, axs = plt.subplots(3, figsize=(10,5))
        fig.suptitle('HFSS-Freq_Offset ' + str(f_set) + ' GHz')
        load__RFA(filesRFA[j])
        col = np.argmin(np.abs((f_measPoints-float(f_set))**2))*2
        gain = meas_array[:, col]
        medianVal = np.median(gain); medianLog.append(medianVal)
        stdVal = np.std(gain); stdLog.append(stdVal)
        axs[0].set_title('RFA file')
        boardName = filesRFA[j].split('\\')[-1].split('_')[4]
        boardLog.append(boardName)
        axs[0].plot(gain, label = boardName)
        axs[0].fill_between(np.linspace(0, len(gain), num=101), medianVal-stdVal*2, medianVal+stdVal*2, color='red', alpha=0.2, label='$\pm$ 2$\sigma$')
        axs[0].hlines(medianVal, 0, len(gain), 'r', label='Median')
        axs[0].legend(loc='lower right')
        for k in range(len(gain)):
            if gain[k] <  medianVal-stdVal*2:
                axs[0].plot(k,gain[k],'rX')
                gain[k] = gain[k]*0.0
        axs[1].set_title('RFA file (filtered)')
        axs[1].plot(gain, label = filesRFA[j].split('\\')[-1].split('_')[4])
        newGain = gain[gain != 0]
        badPortsLog.append(len(gain) - len(newGain))
        minVal = np.min(newGain); minValLog.append(minVal)
        minVal_loc = np.argmin(newGain)
        axs[1].hlines(minVal, 0, len(gain), 'g', label = 'Min val') 
        axs[1].plot(minVal_loc, minVal,'g^', markersize=10)     
        axs[1].legend(loc='lower right')
        correctedGain = gain-minVal
        for m in range(len(correctedGain)):
            if correctedGain[m] < 0:
                correctedGain[m] = correctedGain[m]*0.0
        axs[2].set_title('New RFA file')
        axs[2].plot(correctedGain, label='Shifted:' + str(round(abs(minVal),2)) + ' dB')
        axs[2].legend(loc='lower right')
        
        yaxMin = -5; yaxMax = 55
        axs[0].set_ylim([yaxMin, yaxMax]); axs[0].grid()
        axs[1].set_ylim([yaxMin, yaxMax]); axs[1].grid()
        axs[2].set_ylim([yaxMin, yaxMax]); axs[2].grid()
        axs[0].set_xlabel('port'); axs[0].set_ylabel('dB')
        axs[1].set_xlabel('port'); axs[1].set_ylabel('dB')
        axs[2].set_xlabel('port'); axs[2].set_ylabel('dB')
        # plt.close('all')
    plt.tight_layout()
    
    portFailDict[str(f_set)] = {}
    portFailDict[str(f_set)]['boads'] = boardLog
    portFailDict[str(f_set)]['outlier ports'] = badPortsLog
    
    plt.figure()
    plt.plot(minValLog)
    plt.xlabel('board'); plt.ylabel('minVal')
    
    plt.figure()
    plt.plot(stdLog)
    plt.xlabel('board'); plt.ylabel('stdVal')
    global_std = np.mean(stdLog)
    plt.hlines(global_std, 0, 18)
    
    plt.figure()
    plt.plot(medianLog)
    plt.xlabel('board'); plt.ylabel('medianVal')
    global_median = np.mean(medianLog)
    plt.hlines(global_median, 0, 18)
    
    global_minVal = global_median-global_std*2.0
    print(global_minVal)
    
    ## Apply global offsets
    plt.close('all')
    minValLog = []
    stdLog = []
    medianLog = []
    for j in range(len(filesRFA)):
    # for j in range(1):
        fig, axs = plt.subplots(3, figsize=(20,10))
        fig.suptitle('HFSS-Freq_Offset ' + str(f_set) + ' GHz')
        load__RFA(filesRFA[j])
        col = np.argmin(np.abs((f_measPoints-float(f_set))**2))*2
        gain = meas_array[:, col]
        medianVal = np.median(gain); medianLog.append(medianVal)
        stdVal = np.std(gain); stdLog.append(stdVal)
        axs[0].set_title('RFA file')
        boardName = filesRFA[j].split('\\')[-1].split('_')[4]
        axs[0].plot(gain, label = boardName)
        axs[0].fill_between(np.linspace(0, len(gain), num=101), medianVal-stdVal*2, medianVal+stdVal*2, color='red', alpha=0.2, label='$\pm$ 2$\sigma$')
        axs[0].hlines(medianVal, 0, len(gain), 'r', label='Median')
        axs[0].hlines(global_minVal, 0, len(gain), 'k', label='Global Min Val')
        axs[0].legend(loc='lower right')
        for k in range(len(gain)):
            if gain[k] <  global_minVal:
                axs[0].plot(k,gain[k],'rX')
                gain[k] = gain[k]*0.0
        axs[1].set_title('RFA file (filtered)')
        axs[1].plot(gain, label = filesRFA[j].split('\\')[-1].split('_')[4])
        newGain = gain[gain != 0]
        minVal = np.min(newGain); minValLog.append(minVal)
        minVal_loc = np.argmin(newGain)
        minVal = global_minVal
        axs[1].hlines(minVal, 0, len(gain), 'k', label = 'Global Min Val')    
        axs[1].legend(loc='lower right')
        correctedGain = gain-minVal
        for m in range(len(correctedGain)):
            if correctedGain[m] < 0:
                correctedGain[m] = correctedGain[m]*0.0
        axs[2].set_title('New RFA file')
        axs[2].plot(correctedGain, label='Shifted:' + str(round(abs(minVal),2)) + ' dB')
        axs[2].legend(loc='lower right')
        
        yaxMin = -5; yaxMax = 55
        axs[0].set_ylim([yaxMin, yaxMax]); axs[0].grid()
        axs[1].set_ylim([yaxMin, yaxMax]); axs[1].grid()
        axs[2].set_ylim([yaxMin, yaxMax]); axs[2].grid()
        axs[0].set_xlabel('port'); axs[0].set_ylabel('dB')
        axs[1].set_xlabel('port'); axs[1].set_ylabel('dB')
        axs[2].set_xlabel('port'); axs[2].set_ylabel('dB')
        plt.tight_layout()
        plt.savefig('20230220_figures\\board' + str(j) + '____' + filesRFA[j].split('\\')[-1] + '.png', dpi=200)
    
    ## Open and edit RFA files
    for j in range(len(filesRFA)):
    # for j in range(1):
        plt.figure()
        load__RFA(filesRFA[j])
        gain = meas_array[:, ::2]
        phase = meas_array[:,1:][:, ::2]
        gain = gain - global_minVal
        for k in range(gain.shape[0]):
            for l in range(gain.shape[1]):
                if gain[k,l] < 0:
                    gain[k,l] = gain[k,l]*0.0
        plt.plot(gain[:,int(col/2)])
        
        # merge back
        meas_info_list = meas_info.copy()
        meas_array_corrected = meas_array.copy()*0.0
        for m in range(gain.shape[1]):
            meas_array_corrected[:,2*m] = gain[:,m]
            meas_array_corrected[:,2*m+1] = phase[:,m]
        for o in range(len(meas_array_corrected)):
            meas_info_list.append(list(meas_array_corrected[o,:]))
            
        # write new file
        file = open('C:\\codeRun\\20230220_HFSS-Freq-Offset_test\\' + filesRFA[j].split('\\')[-1] + '_HFSS-f-offset.csv', 'w+', newline ='') 
        with file:     
            write = csv.writer(file) 
            write.writerows(meas_info_list)
                      



    
            
            
            
        
            
    

