import numpy as np
import os
import json
import csv
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt;

plt.close('all')
import pickle

matplotlib.use('Agg')

filePath = r'C:\Users\RyanFairclough\Downloads\P10_Asssembly_Candidates_RFA' # Location of Raw Data
tlmType = 'Rx' # TLM Type

multiIt = 'False' # Whether the calibration measurement has multiple iterations. If it does the RFA files will be picked from the first iteration. It is not a valid parameter for RFC files

if tlmType == 'Rx':
    f_set_Log = [17.7, 18.2, 18.7, 19.2, 19.7, 20.2, 20.7, 21.2]
    normVal = 3  # Min attenuation value for RFA optimisation
    multiplier = 2  # sigma range away from the median value that is considered acceptable
    RFC_offset = [5, 5, 5, 5, 5, 5, 5, 5]  # Frequency dependent attenuation added to the Rx RFC files
    beamEq='False'
    lensEq='False'
    mask = 'HFSS'  # Type of calibration mask
    diffPP = 'False'  # Different post processing for 30.5GHz (only Tx) files are required to be either recalculated beforehand with expected HFSS offset or to be calibrated with the correct mask
    numPorts=96

elif tlmType == 'Tx':
    f_set_Log = [27.5, 28.0, 28.5, 29.0, 29.5, 30.0, 30.5, 31.0]
    normVal = 0  # Min attenuation value for RFA optimisation
    multiplier = 1  # sigma range away from the median value that is considered acceptable
    RFC_offset = [0, 0, 0, 0, 0, 0, 0, 0]  # Frequency dependent attenuation added to the Rx RFC files
    beamEq='True'
    lensEq='True'
    mask = 'FM'  # Type of calibration mask
    diffPP = 'True'  # Different post processing for 30.5GHz (only Tx) files are required to be either recalculated beforehand with expected HFSS offset or to be calibrated with the correct mask
    numPorts=152



def find__RFAfiles(path, f_set, fileType, filesRFAtest):

    files = []
    for root, directories, file in os.walk(path):
        for file in file:
            if (file.endswith(".csv")):
                files.append(os.path.join(root, file))

    for beamChoice in range(2):
        beam = beamChoice + 1
        k = 0
        for i in range(len(files)):
            if multiIt==True and fileType=='RFA_2':
                if fileType in files[i] and 'GHz_' + str(f_set) + '0_GHz' in files[i] and 'Beam' + str(beam) and 'teration_1' in files[i]:

                    if beam==1:
                        filesRFAtest.append([files[i]])
                        k=k+1
                    elif beam==2:
                        filesRFAtest[k].extend([files[i]])
                        k = k + 1
            else:
                if fileType in files[i] and 'GHz_' + str(f_set) + '0_GHz' in files[i] and 'Beam' + str(beam) in files[i]:

                    if beam==1:
                        filesRFAtest.append([files[i]])
                        k=k+1
                    elif beam==2:
                        filesRFAtest[k].extend([files[i]])
                        k = k + 1
                    #print(filesRFAtest)


def load__RFA(filePath):
    global meas_info, meas_array, f_measPoints
    meas_info = []
    with open(filePath, 'r') as file:
        filecontent = csv.reader(file, delimiter=',')
        for row in filecontent:
            meas_info.append(row)
            header_offset = 29
        meas_info = meas_info[0:header_offset]
        meas_array = np.genfromtxt(filePath, delimiter=',', skip_header=header_offset)
        f_measPoints = np.array(meas_info[header_offset - 1])[::2].astype(float)


for i in range(len(f_set_Log)):
    f_set=f_set_Log[i]

    filesRFA = list()
    filesRFC = list()
    find__RFAfiles(filePath, f_set, 'RFA_2',filesRFA)
    if tlmType=='Tx':
        find__RFAfiles(filePath, f_set, 'RFC_2', filesRFC)

    else:
        filesRFC=filesRFA

    global_std = np.empty(2)
    global_median = np.empty(2)
    global_minVal = np.empty(2)

    if normVal >= 0:
        RFA_offset_val = 'Offset_' + str(normVal) + 'dB_' + str(multiplier) + 'sig'
    elif normVal < 0:
        RFA_offset_val = 'Offset_m' + str(abs(normVal)) + 'dB_' + str(multiplier) + 'sig'

    if RFC_offset[i] >= 0:
        RFC_offset_val = 'Offset_' + str(RFC_offset[i]) + 'dB'
    elif RFC_offset[i] < 0:
        RFC_offset_val = 'Offset_m' + str(abs(RFC_offset[i])) + 'dB'

    for beamChoice in range(2):

        minValLog = np.empty(len(filesRFA))
        stdLog = np.empty(len(filesRFA))
        medianLog = np.empty(len(filesRFA))
        print(f_set)
        print('Beam is   ', beamChoice+1)

        for j in range(len(filesRFA)):
            load__RFA(filesRFA[j][beamChoice])
            col = np.argmin(np.abs((f_measPoints - float(f_set)) ** 2)) * 2
            gain = meas_array[:, col]
            medianVal = np.median(gain);
            medianLog[j]=medianVal
            stdVal = np.std(gain);
            stdLog[j]=stdVal

            boardName = filesRFA[j][beamChoice].split('\\')[-1].split('_')[6];
            print(boardName);

        global_std[beamChoice] = np.mean(stdLog)

        global_median[beamChoice] = np.average(medianLog)

        global_minVal[beamChoice] = global_median[beamChoice] - global_std[beamChoice] * multiplier

    beamCorrMin= np.min(global_minVal)

    if beamEq=='True':
        RFC_gain_Corr= global_minVal-beamCorrMin
    else:
        RFC_gain_Corr =[0, 0]

    print('beamCorrMin is    ', beamCorrMin)
    print('GlobalMinVal is    ', global_minVal)
    print('RFC_Gain_Corr is    ', RFC_gain_Corr)

    for beamChoice in range(2):

        for j in range(len(filesRFA)):
            load__RFA(filesRFA[j][beamChoice])
            #print(filesRFA[j][beamChoice])

            RFA_meas_info = meas_info
            RFA_meas_array = meas_array
            RFA_f_measPoints = f_measPoints
            NumColumn = len(RFA_meas_array[1])

            if tlmType=='Tx':
                load__RFA(filesRFC[j][beamChoice])
                RFC_meas_info = meas_info
                RFC_meas_array = meas_array
                RFC_f_measPoints = f_measPoints
            else:
                RFC_meas_info = RFA_meas_info
                RFC_meas_info[0][0] = RFC_meas_info[0][0].replace('RFA', 'RFC')
                RFC_meas_array = np.zeros([6, NumColumn])
                RFC_f_measPoints = f_measPoints

            RFA_gain_full = RFA_meas_array[:, ::2]
            RFA_phase_full = RFA_meas_array[:, 1:][:, ::2]

            RFC_gain_full = RFC_meas_array[:, ::2]
            RFC_phase_full = RFC_meas_array[:, 1:][:, ::2]

            col = np.argmin(np.abs((RFA_f_measPoints - float(f_set)) ** 2)) * 2
            RFA_gain = RFA_meas_array[:, col]
            RFC_gain = RFC_meas_array[:, col]

            if diffPP=='True' and f_set==30.5:
                RFA_gain=RFA_gain
            else:
                RFA_gain=RFA_gain-global_minVal[beamChoice]+normVal


            if lensEq=='True':
                L1_att = np.mean(gain[0:int(numPorts)]);
                L2_att = np.mean(gain[int(numPorts):int(2*numPorts)]);
                L3_att = np.mean(gain[int(2*numPorts):(3*numPorts)]);

                scaleval = min(L1_att, L2_att, L3_att)

                L1_att = L1_att - scaleval
                L2_att = L2_att - scaleval
                L3_att = L3_att - scaleval
            else:
                L1_att = 0
                L2_att = 0
                L3_att = 0



            RFA_gain[0:int(numPorts)] = RFA_gain[0:int(numPorts)] - L1_att
            RFA_gain[int(numPorts):int(2*numPorts)] = RFA_gain[int(numPorts):int(2*numPorts)] - L2_att
            RFA_gain[int(2*numPorts):(3*numPorts)] = RFA_gain[int(2*numPorts):(3*numPorts)] - L3_att

            RFC_gain[0] = RFC_gain[0] + L1_att + RFC_gain_Corr[beamChoice]+ RFC_offset[i]
            RFC_gain[1] = RFC_gain[1] + L1_att + RFC_gain_Corr[beamChoice] + RFC_offset[i]
            RFC_gain[2] = RFC_gain[2] + L2_att + RFC_gain_Corr[beamChoice] + RFC_offset[i]
            RFC_gain[3] = RFC_gain[3] + L2_att + RFC_gain_Corr[beamChoice] + RFC_offset[i]
            RFC_gain[4] = RFC_gain[4] + L3_att + RFC_gain_Corr[beamChoice] + RFC_offset[i]
            RFC_gain[5] = RFC_gain[5] + L3_att + RFC_gain_Corr[beamChoice] + RFC_offset[i]

            col1 = np.argmin(np.abs((RFA_f_measPoints - float(f_set)) ** 2))

            RFA_gain_full[:, col1] = RFA_gain

            RFC_gain_full[:, col1] = RFC_gain

            for k in range(RFA_gain_full.shape[0]):
                for l in range(RFA_gain_full.shape[1]):
                    if normVal >= 0:
                        if RFA_gain_full[k, l] <= normVal:
                            RFA_gain_full[k, l] = normVal
                    elif normVal<0:
                        if RFA_gain_full[k, l] <= 0:
                            RFA_gain_full[k, l] = 0

            RFA_meas_info_list = RFA_meas_info.copy()
            RFA_meas_array_corrected = RFA_meas_array.copy() * 0.0
            for m in range(RFA_gain_full.shape[1]):
                RFA_meas_array_corrected[:, 2 * m] = RFA_gain_full[:, m]
                RFA_meas_array_corrected[:, 2 * m + 1] = RFA_phase_full[:, m]
            for o in range(len(RFA_meas_array_corrected)):
                RFA_meas_info_list.append(list(RFA_meas_array_corrected[o, :]))

            RFA_savePath = filePath + '_post-processed' + '\\' + RFA_offset_val + '\\Corrected_RFA'
            if not os.path.exists(RFA_savePath):
                os.makedirs(RFA_savePath)
                # write new file
            RFA_filename = filesRFA[j][beamChoice].split('\\')[-1]
            RFA_filename = RFA_filename.split('.csv')[-2]

            if diffPP=='True' and f_set==30.5:
                file = open(RFA_savePath + '\\' + RFA_filename + '_' + 'Offset' + '_' + mask + '.csv', 'w+', newline='')
            else:
                file = open(RFA_savePath + '\\' + RFA_filename + '_' + RFA_offset_val + '_' + mask + '.csv', 'w+', newline='')
            with file:
                write = csv.writer(file)
                write.writerows(RFA_meas_info_list)

            RFC_meas_info_list = RFC_meas_info.copy()
            RFC_meas_array_corrected = RFC_meas_array.copy() * 0.0
            for m in range(RFC_gain_full.shape[1]):
                RFC_meas_array_corrected[:, 2 * m] = RFC_gain_full[:, m]
                RFC_meas_array_corrected[:, 2 * m + 1] = RFC_phase_full[:, m]
            for o in range(len(RFC_meas_array_corrected)):
                RFC_meas_info_list.append(list(RFC_meas_array_corrected[o, :]))

            RFC_savePath = filePath + '_post-processed' + '\\' + RFA_offset_val + '\\Corrected_RFC'
            if not os.path.exists(RFC_savePath):
                os.makedirs(RFC_savePath)
                # write new file
            if tlmType=='Tx':
                RFC_filename = filesRFC[j][beamChoice].split('\\')[-1]
                RFC_filename = RFC_filename.split('.csv')[-2]
            else:
                RFC_filename = filesRFA[j][beamChoice].split('\\')[-1]
                RFC_filename = RFC_filename.split('.csv')[-2]
                RFC_filename = RFC_filename.replace('RFA', 'RFC')

            if diffPP=='True' and f_set==30.5:
                if beamEq=='True':
                    if lensEq=='True':
                        file = open(RFC_savePath + '\\' + RFC_filename + '_' + 'Offset' + '_BE_LE_'+ mask + '.csv', 'w+', newline='')
                    else:
                        file = open(RFC_savePath + '\\' + RFC_filename + '_' + 'Offset' + '_BE_' + mask + '.csv',
                                    'w+', newline='')
                else:
                    file = open(RFC_savePath + '\\' + RFC_filename + '_' + 'Offset' + '_' + mask + '.csv', 'w+',
                                newline='')
            else:
                if beamEq == 'True':
                    if lensEq == 'True':
                        file = open(RFC_savePath + '\\' + RFC_filename + '_' + RFC_offset_val + '_BE_LE_' + mask + '.csv', 'w+', newline='')
                    else:
                        file = open(RFC_savePath + '\\' + RFC_filename + '_' + RFC_offset_val + '_BE_' + mask + '.csv',
                                    'w+', newline='')
                else:
                    file = open(RFC_savePath + '\\' + RFC_filename + '_' + RFC_offset_val + '_' + mask + '.csv',
                                'w+', newline='')


            with file:
                write = csv.writer(file)
                write.writerows(RFC_meas_info_list)
