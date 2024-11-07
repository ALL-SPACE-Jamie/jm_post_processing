import numpy as np
import os
import json
import csv
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt;
import shutil


filePath = r'C:\Users\RyanFairclough\Downloads\561_383'
# savePath = r'C:\Users\mmarinova\Downloads\RFA_Rx_I1\RFA_Files\17G7-20G7'

tlmType = 'Rx'
fileN='RFA'
fileType = fileN+'_2'  # RFC or RFA file. The _2 is needed otherwise it picks all csv files and throws an error

if tlmType == 'Rx':
    f_set_Log = [17.7, 18.2, 18.7, 19.2, 19.7, 20.2, 20.7, 21.2]
    # f_set_Log = [17.7, 18.2, 18.7, 19.2, 19.7, 20.2, 20.7] #[17.7, 18.2, 18.7, 19.2, 19.7, 20.2, 20.7, 21.2]
    # f_set_Log = [21.2]
elif tlmType == 'Tx':
    f_set_Log = [27.5, 28.0, 28.5, 29.0, 29.5, 30.0, 30.5, 31.0]
    # f_set_Log = [29.5]

for beamChoice in range(2):
    beam = beamChoice + 1


    def find__RFAfiles(path, f_set, beam, fileType):
        global filesRFA
        files = []
        for root, directories, file in os.walk(path):
            for file in file:
                if (file.endswith(".csv")):
                    files.append(os.path.join(root, file))
        filesRFA = []
        for i in range(len(files)):
            if fileType in files[i] and 'GHz_' + str(f_set) + '0_GHz' in files[i] and 'Beam' + str(beam) in files[i]:# and 'teration_1' in files[i]:
                # if 'RFA' in files[i] and 'both_' + str(f_set) + '_GHz' in files[i] and 'Beam'+str(beam) in files[i]:
                filesRFA.append(files[i])

    ########## RUN ##########

    portFailDict = {}
    for f_set in f_set_Log:
        find__RFAfiles(filePath, f_set, beam, fileType)


        savePath = filePath + '_' +fileN
        if not os.path.exists(savePath):
            os.makedirs(savePath)

        for j in range(len(filesRFA)):
            RFAfilename = filesRFA[j].split('\\')[-1]
            RFAfilename = RFAfilename.split('.csv')[-2]
            fileName_Output = savePath + '\\' + RFAfilename + '.csv'
            shutil.copyfile(filesRFA[j], fileName_Output)











