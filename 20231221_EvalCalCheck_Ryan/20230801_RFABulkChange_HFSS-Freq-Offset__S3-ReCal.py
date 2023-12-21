import numpy as np
import os
import json
import csv
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt; plt.close('all')
import pickle

matplotlib.use('Agg')

filePath = r'C:\Users\RyanFairclough\Downloads\Rx_Batch_2_Recal2Original_Files\Rx_Batch_2_Recal2Original_Files'

tlmType = 'Rx'
normVal = 3
multiplier=2

if normVal>=0:
    offset='HFSS_offset_'+str(normVal)+'dB_'+str(multiplier)+'sig'
elif normVal<0:
    offset = 'HFSS_offset_m' + str(abs(normVal)) + 'dB_' + str(multiplier) + 'sig'


if tlmType=='Rx':
    f_set_Log = [17.7, 18.2, 18.7, 19.2, 19.7, 20.2, 20.7,21.2] #[17.7, 18.2, 18.7, 19.2, 19.7, 20.2, 20.7, 21.2]
elif tlmType=='Tx':
    f_set_Log = [27.5, 28.0, 28.5, 29.0, 29.5, 30.0, 30.5, 31.0]

for beamChoice in range(2):
    beam = beamChoice + 1

    def find__RFAfiles(path, f_set, beam):
        global filesRFA
        files = []
        for root, directories, file in os.walk(path):
        	for file in file:
        		if(file.endswith(".csv")):
        			files.append(os.path.join(root,file))
        filesRFA = []
        for i in range(len(files)):
            if 'RFA' in files[i] and 'GHz_' + str(f_set) + '0_GHz' in files[i] and 'Beam' + str(beam) in files[i]:
            #if 'RFA' in files[i] and 'both_' + str(f_set) + '_GHz' in files[i] and 'Beam'+str(beam) in files[i]:
                filesRFA.append(files[i])
                
    def analyse__RFAparams(filesRFA):
        global RFAparamDict, fileName
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
            log_f_set.append(fileName.split('_')[-3])
            log_beam.append(fileName.split('_')[9][-1])
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
                header_offset = 28
            meas_info = meas_info[0:header_offset]
            meas_array = np.genfromtxt(filePath, delimiter=',', skip_header=header_offset)
            f_measPoints = np.array(meas_info[header_offset-1])[::2].astype(float)

########## RUN ##########

    portFailDict = {}
    for f_set in f_set_Log:
        find__RFAfiles(filePath, f_set, beam)
        analyse__RFAparams(filesRFA)
        
        ## Collate values and find global offsets
        minValLog = []
        stdLog = []
        medianLog = []
        badPortsLog = []
        boardLog = []
        for j in range(len(filesRFA)):
            fig, axs = plt.subplots(3, figsize=(10,5))
            fig.suptitle('HFSS-Freq_Offset ' + str(f_set) + ' GHz')
            load__RFA(filesRFA[j])
            col = np.argmin(np.abs((f_measPoints-float(f_set))**2))*2
            gain = meas_array[:, col]
            medianVal = np.median(gain); medianLog.append(medianVal)
            stdVal = np.std(gain); stdLog.append(stdVal)
            axs[0].set_title('RFA file')
            boardName = filesRFA[j].split('\\')[-1].split('_')[4]; print(boardName); print(medianVal)
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
            correctedGain = gain-minVal+normVal
            for m in range(len(correctedGain)):
                if correctedGain[m] <= 0:
                    correctedGain[m] = correctedGain[m]*0.0+normVal ######################
            axs[2].set_title('New RFA file')
            axs[2].plot(correctedGain, label='Shifted:' + str(round(abs(minVal-normVal),2)) + ' dB')
            axs[2].legend(loc='lower right')
            
            yaxMin = -5; yaxMax = 55
            axs[0].set_ylim([yaxMin, yaxMax]); axs[0].grid()
            axs[1].set_ylim([yaxMin, yaxMax]); axs[1].grid()
            axs[2].set_ylim([yaxMin, yaxMax]); axs[2].grid()
            axs[0].set_xlabel('port'); axs[0].set_ylabel('dB')
            axs[1].set_xlabel('port'); axs[1].set_ylabel('dB')
            axs[2].set_xlabel('port'); axs[2].set_ylabel('dB')
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
        global_median = np.average(medianLog) ####################was mean
        plt.hlines(global_median, 0, 18)
        
        global_minVal = global_median-global_std*multiplier
        print(global_minVal)

        ## Apply global offsets
        minValLog = []
        stdLog = []
        medianLog = []
        for j in range(len(filesRFA)):
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
            correctedGain = gain-minVal+normVal
            for m in range(len(correctedGain)):
                if correctedGain[m] <= normVal:
                    correctedGain[m] = normVal
            axs[2].set_title('New RFA file')
            axs[2].plot(correctedGain, label='Shifted:' + str(round(abs(minVal-normVal),2)) + ' dB')
            axs[2].legend(loc='lower right')
            
            yaxMin = -5; yaxMax = 55
            axs[0].set_ylim([yaxMin, yaxMax]); axs[0].grid()
            axs[1].set_ylim([yaxMin, yaxMax]); axs[1].grid()
            axs[2].set_ylim([yaxMin, yaxMax]); axs[2].grid()
            axs[0].set_xlabel('port'); axs[0].set_ylabel('dB')
            axs[1].set_xlabel('port'); axs[1].set_ylabel('dB')
            axs[2].set_xlabel('port'); axs[2].set_ylabel('dB')
            plt.tight_layout()
            savePath = filePath + '_post-processed'+ '\\' + offset + '\\figures'
            if not os.path.exists(savePath):
                os.makedirs(savePath)
            plt.savefig(savePath + '\\' + str(j) + '____' + filesRFA[j].split('\\')[-1] + '.png', dpi=200)


        ## Open and edit RFA files
        for j in range(len(filesRFA)):
        # for j in range(2):
            plt.figure()
            load__RFA(filesRFA[j])
            gain = meas_array[:, ::2]
            phase = meas_array[:,1:][:, ::2]
            gain = gain - global_minVal+normVal
            for k in range(gain.shape[0]):
                for l in range(gain.shape[1]):
                    if normVal>=0:
                        if gain[k, l] <= normVal:
                            gain[k, l] = normVal

                    elif normVal<0:
                        if gain[k, l] <= 0:
                            gain[k, l] = 0

                        
            # merge back
            meas_info_list = meas_info.copy()
            meas_array_corrected = meas_array.copy()*0.0
            for m in range(gain.shape[1]):
                meas_array_corrected[:,2*m] = gain[:,m]
                meas_array_corrected[:,2*m+1] = phase[:,m]
            for o in range(len(meas_array_corrected)):
                meas_info_list.append(list(meas_array_corrected[o,:]))
    
            savePath = filePath + '_post-processed'+ '\\' + offset
            if not os.path.exists(savePath):
                os.makedirs(savePath) 
            # write new file
            RFAfilename = filesRFA[j].split('\\')[-1]
            RFAfilename = RFAfilename.split('.csv')[-2]

            file = open(savePath +'\\'+ RFAfilename + '_'+offset+'.csv', 'w+', newline ='')
            with file:
                write = csv.writer(file) 
                write.writerows(meas_info_list)
                          
        plt.close('all')
    
    
        
                
                
                
            
                
        
    
