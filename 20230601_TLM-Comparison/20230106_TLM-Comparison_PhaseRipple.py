import pandas as pd
import numpy as np
import matplotlib.pyplot as plt; plt.rcParams['font.size'] = 12
from matplotlib.markers import MarkerStyle
from scipy.stats import norm
import os
import glob
import copy
import csv
import json
import time
from pylab import *
plt.close('all')

mapPlot = False

folders = [r'C:\Users\jmitchell\Downloads\RFA_Files(1)\RFA_Files', r'C:\Users\jmitchell\Downloads\RFA_Files(1)\RFA_Files']
f_set_list = [27.5] #[27.5, 28.0, 28.5, 29.0, 29.5, 30.0, 30.5, 31.0]
savePath = 'C:\\Scratch\\FiguresTx\\'
map_tlm = np.genfromtxt(r'C:\Users\jmitchell\Documents\GitHub\Post-Processing\20230601_TLM-Comparison\Mrk1_S2000_TLM_TX_ArrayGeometry_V20062022_CalInfo.csv', skip_header=2, dtype=float, delimiter=',')

# folders = [r'C:\Scratch\Ref_TLM_Rx\Ref', r'C:\\Scratch\\Ref_TLM_Rx\forCompare']
# f_set_list = [17.7, 18.2, 18.7, 19.2, 19.7, 20.2, 20.7, 21.2]
# savePath = 'C:\\Scratch\\FiguresRx\\'
# map_tlm = np.genfromtxt(r'C:\Users\JamieMitchell\PycharmProjects\Post-Processing\20230601_TLM-Comparison\Mrk1_S2000_TLM_RX_ArrayGeometry_V20062022_CalInfo.csv', skip_header=2, dtype=float, delimiter=',')


# file path
dirScript = os.getcwd()
# definitions
def find_measFiles(path, fileString, beam):
    global measFiles, files
    files = []
    for root, directories, file in os.walk(path):
        for file in file:
            if (file.endswith(".csv")) == True:
                files.append(os.path.join(root, file))
    measFiles = []
    for i in range(len(files)):
        if fileString in files[i] and 'eam' + str(beam) in files[i]:
            measFiles.append(files[i])
            

def load_measFiles(filePath):
    global meas_info, meas_array, meas_frequencies, meas_params, meas_array_gain, meas_array_phase
    meas_params = {}
    meas_info = []
    # meas_info, array and measurement frequencies
    with open(filePath, 'r') as file:
        filecontent = csv.reader(file, delimiter=',')
        time.sleep(0.10)
        for row in filecontent:
            meas_info.append(row)
        index_start = [index for index in range(len(meas_info)) if 'barcodes' in meas_info[index]][0] + 2
        meas_info = meas_info[0:index_start]
        meas_array = np.genfromtxt(filePath, delimiter=',', skip_header=index_start)
        meas_array_gain = meas_array[:,::2]
        meas_array_phase = meas_array[:,1:][:,::2]
        meas_frequencies = np.array(meas_info[index_start - 1])[::2].astype(float)    
        
    # meas_params
    for i in range(len(meas_info) - 1):
        if len(meas_info[i]) > 1:
            paramName = meas_info[i][0]

            if paramName[0:2] == '# ':
                paramName = paramName[2:]
            meas_params[paramName] = meas_info[i][1]
            
def plot_phaseDrift(deltaNew, title, cmin, cmax, cstp, f_set):
    global Z, Y
    x = []
    y=[]
    rot = []
    for i in range(len(map_tlm)):
        x.append(map_tlm[i,4])
        # x.append(map_tlm[i,4])
        y.append(map_tlm[i,5])
        # y.append(map_tlm[i,5])
        rot.append(map_tlm[i,8])
        # rot.append(map_tlm[i,8])
    x = np.array(x)
    y = np.array(y)

    plt.figure()
    Z = deltaNew-np.mean(deltaNew)
    Z = Z[1:][::2]
    Y=3e8/(f_set*1e9)
    # Z = 1000.0*Z/360.0*Y

    m = MarkerStyle("s")
    m._transform.rotate_deg(float(rot[i]))
    cseg = int((cmax-cmin)/cstp)
    plt.scatter(x, y, c=Z, marker=m, s=50, edgecolors='black', cmap = cm.get_cmap('jet', cseg))
    plt.colorbar()

    plt.clim(cmin, cmax)
    plt.xlabel('X [mm]'); plt.ylabel('Y [mm]')
    plt.title(title)
    plt.tight_layout()
            
minmax_log = []
stdev_log = []
FN_log = []
beam_log = []
f_set_log = []
date_log = []
time_log = []
rig_log = []
side_log = []
for beamChoice in range(2):
    beamChoice = beamChoice+1
    for f_set in f_set_list:
        if mapPlot == False:
            plt.figure()
        arrayList = []
        labelList = []
        for folder in folders:
            find_measFiles(folder, 'OP', beamChoice)
            for measFile in measFiles:
                print(measFile)
                load_measFiles(measFile)
                if float(meas_params['f_c']) == float(f_set):
                    loc = np.argmin((meas_frequencies - f_set)**2)
                    arrayList.append(meas_array_phase[:,loc])
                    if folder == folders[0]:
                        labelList.append('REF: ' + (measFile.split('\\')[-3]))
                    else:
                        labelList.append(measFile.split('\\')[-3])
                    
      
        for i in range(len(arrayList)):
            delta = arrayList[i]-arrayList[0]
            deltaMean = np.median(delta)
            deltaNew = delta.copy()
            for j in range(len(delta)):
                if np.abs(delta[j] - deltaMean) > 120.0:
                    if delta[j] < 0:
                        deltaNew[j] = delta[j] + 360.0
                    if delta[j] > 0:
                        deltaNew[j] = delta[j] - 360.0
            minmax = round(max(deltaNew)-min(deltaNew),2)
            stdev = round(np.std(deltaNew),2)
            minmax_log.append(minmax)
            stdev_log.append(stdev)
            details = '(max-min)/2 = ' + str(minmax/2.0) + ', st. dev. = ' + str(stdev)
            print(str(labelList[i].split('_')[0:2]) + str(labelList[i].split('_')[7:9]) + ', beam' + str(beamChoice) + ', ' + str(f_set) + ', ' + str(details))
            label = str(labelList[i].split('_')[0:2]) + str(labelList[i].split('_')[7:9])
            date_log.append(labelList[i].split('_')[0])
            time_log.append(labelList[i].split('_')[1])
            rig_log.append(labelList[i].split('_')[7] + '_' + labelList[i].split('_')[-3])
            side_log.append(labelList[i].split('_')[8])
            FN_log.append(label)
            beam_log.append(beamChoice)
            f_set_log.append(f_set)
        
            title = 'f_set = ' + str(f_set) + ' GHz, Beam ' + str(beamChoice)
            plotLabel = label+ '\n' + 'max-min = ' + str(minmax) + ', st. dev. = ' + str(stdev)
            if mapPlot == True:
                plot_phaseDrift(deltaNew, title + '\n' + plotLabel, -45,  40.0, 5, f_set)
                plt.savefig(savePath + labelList[i].split('_')[7] + '_' + labelList[i].split('_')[8] + '_f_set_' + str(f_set) + 'GHz_Beam_' + str(beamChoice) + '_map' + str(mapPlot) + '.png', dpi=400)
            if mapPlot == False:
                plt.plot(deltaNew-np.mean(deltaNew), label = plotLabel)
        if mapPlot == False:
            plt.xlabel('Port'); plt.ylabel('$\Delta \Theta$ [deg]')
            plt.ylim([-45,45]);
            plt.yticks(np.linspace(-45, 45, num=int(90/5)+1))
            plt.grid('on')   
            plt.legend(ncol=1, loc='lower right', fontsize=15)
            plt.tight_layout()
            
            plt.title(title)
            plt.savefig(savePath + 'f_set_' + str(f_set) + 'GHz_Beam_' + str(beamChoice) + '_map' + str(mapPlot) + '.png', dpi=400)
        
out = np.transpose(np.vstack([np.array(date_log), np.array(time_log), np.array(rig_log), np.array(beam_log), np.array(f_set_log), np.array(minmax_log), np.array(stdev_log)]))
outSorted = out[np.argsort(out[:, 0])]



















# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt; plt.rcParams['font.size'] = 12
# from matplotlib.markers import MarkerStyle
# from scipy.stats import norm
# import os
# import glob
# import copy
# import csv
# import json
# import time
# from pylab import *
# plt.close('all')

# mapPlot = True

# folders = [r'C:\Scratch\Ref_TLM_Tx\Ref', r'C:\\Scratch\\Ref_TLM_Tx\forCompare']
# f_set_list = [27.5] #[27.5, 28.0, 28.5, 29.0, 29.5, 30.0, 30.5, 31.0]
# savePath = 'C:\\Scratch\\FiguresTx\\'
# map_tlm = np.genfromtxt(r'C:\Users\JamieMitchell\PycharmProjects\Post-Processing\20230601_TLM-Comparison\Mrk1_S2000_TLM_TX_ArrayGeometry_V20062022_CalInfo.csv', skip_header=2, dtype=float, delimiter=',')

# # folders = [r'C:\Scratch\Ref_TLM_Rx\Ref', r'C:\\Scratch\\Ref_TLM_Rx\forCompare']
# # f_set_list = [17.7, 18.2, 18.7, 19.2, 19.7, 20.2, 20.7, 21.2]
# # savePath = 'C:\\Scratch\\FiguresRx\\'
# # map_tlm = np.genfromtxt(r'C:\Users\JamieMitchell\PycharmProjects\Post-Processing\20230601_TLM-Comparison\Mrk1_S2000_TLM_RX_ArrayGeometry_V20062022_CalInfo.csv', skip_header=2, dtype=float, delimiter=',')


# # file path
# dirScript = os.getcwd()
# # definitions
# def find_measFiles(path, fileString, beam):
#     global measFiles, files
#     files = []
#     for root, directories, file in os.walk(path):
#         for file in file:
#             if (file.endswith(".csv")) == True:
#                 files.append(os.path.join(root, file))
#     measFiles = []
#     for i in range(len(files)):
#         if fileString in files[i] and 'eam' + str(beam) in files[i]:
#             measFiles.append(files[i])
            

# def load_measFiles(filePath):
#     global meas_info, meas_array, meas_frequencies, meas_params, meas_array_gain, meas_array_phase
#     meas_params = {}
#     meas_info = []
#     # meas_info, array and measurement frequencies
#     with open(filePath, 'r') as file:
#         filecontent = csv.reader(file, delimiter=',')
#         time.sleep(0.10)
#         for row in filecontent:
#             meas_info.append(row)
#         index_start = [index for index in range(len(meas_info)) if 'barcodes' in meas_info[index]][0] + 2
#         meas_info = meas_info[0:index_start]
#         meas_array = np.genfromtxt(filePath, delimiter=',', skip_header=index_start)
#         meas_array_gain = meas_array[:,::2]
#         meas_array_phase = meas_array[:,1:][:,::2]
#         meas_frequencies = np.array(meas_info[index_start - 1])[::2].astype(float)    
        
#     # meas_params
#     for i in range(len(meas_info) - 1):
#         if len(meas_info[i]) > 1:
#             paramName = meas_info[i][0]

#             if paramName[0:2] == '# ':
#                 paramName = paramName[2:]
#             meas_params[paramName] = meas_info[i][1]
            
# def plot_phaseDrift(deltaNew, title, cmin, cmax, cstp, f_set):
#     global Z, Y
#     x = []
#     y=[]
#     rot = []
#     for i in range(len(map_tlm)):
#         x.append(map_tlm[i,4])
#         # x.append(map_tlm[i,4])
#         y.append(map_tlm[i,5])
#         # y.append(map_tlm[i,5])
#         rot.append(map_tlm[i,8])
#         # rot.append(map_tlm[i,8])
#     x = np.array(x)
#     y = np.array(y)

#     plt.figure()
#     Z = deltaNew#-np.mean(deltaNew)
#     Z = Z[1:][::2]
#     Y=3e8/(f_set*1e9)
#     # Z = 1000.0*Z/360.0*Y

#     m = MarkerStyle("s")
#     m._transform.rotate_deg(float(rot[i]))
#     cseg = int((cmax-cmin)/cstp)
#     plt.scatter(x, y, c=Z, marker=m, s=50, edgecolors='black', cmap = cm.get_cmap('jet', cseg))
#     plt.colorbar()

#     plt.clim(cmin, cmax)
#     plt.xlabel('X [mm]'); plt.ylabel('Y [mm]')
#     plt.title(title)
#     plt.tight_layout()
            
# minmax_log = []
# stdev_log = []
# FN_log = []
# beam_log = []
# f_set_log = []
# date_log = []
# time_log = []
# rig_log = []
# side_log = []
# for beamChoice in range(2):
#     beamChoice = beamChoice+1
#     for f_set in f_set_list:
#         if mapPlot == False:
#             plt.figure()
#         arrayList = []
#         labelList = []
#         for folder in folders:
#             find_measFiles(folder, 'OP', beamChoice)
#             for measFile in measFiles:
#                 print(measFile)
#                 load_measFiles(measFile)
#                 if float(meas_params['f_c']) == float(f_set):
#                     loc = np.argmin((meas_frequencies - f_set)**2)
#                     arrayList.append(meas_array_phase[:,loc])
#                     if folder == folders[0]:
#                         labelList.append('REF: ' + (measFile.split('\\')[-3]))
#                     else:
#                         labelList.append(measFile.split('\\')[-3])
                    
      
#         for i in range(len(arrayList)):
#             delta = arrayList[i]-arrayList[0]
#             delta = arrayList[i]
#             deltaMean = np.median(delta)
#             deltaNew = delta.copy()
#             # for j in range(len(delta)):
#             #     if np.abs(delta[j] - deltaMean) > 120.0:
#             #         if delta[j] < 0:
#             #             deltaNew[j] = delta[j] + 360.0
#             #         if delta[j] > 0:
#             #             deltaNew[j] = delta[j] - 360.0
#             minmax = round(max(deltaNew)-min(deltaNew),2)
#             stdev = round(np.std(deltaNew),2)
#             minmax_log.append(minmax)
#             stdev_log.append(stdev)
#             details = '(max-min)/2 = ' + str(minmax/2.0) + ', st. dev. = ' + str(stdev)
#             print(str(labelList[i].split('_')[0:2]) + str(labelList[i].split('_')[-4:-2]) + ', beam' + str(beamChoice) + ', ' + str(f_set) + ', ' + str(details))
#             label = str(labelList[i].split('_')[0:2]) + str(labelList[i].split('_')[-4:-2])
#             date_log.append(labelList[i].split('_')[0])
#             time_log.append(labelList[i].split('_')[1])
#             rig_log.append(labelList[i].split('_')[-4] + '_' + labelList[i].split('_')[-3])
#             side_log.append(labelList[i].split('_')[-3])
#             FN_log.append(label)
#             beam_log.append(beamChoice)
#             f_set_log.append(f_set)
        
#             title = 'f_set = ' + str(f_set) + ' GHz, Beam ' + str(beamChoice)
#             plotLabel = label+ '\n' + 'max-min = ' + str(minmax) + ', st. dev. = ' + str(stdev)
#             if mapPlot == True:
#                 plot_phaseDrift(deltaNew, title + '\n' + plotLabel, -360.0,  360.0, 5, f_set)
#                 plt.savefig(savePath + labelList[i].split('_')[-4] + '_' + labelList[i].split('_')[-3] + '_f_set_' + str(f_set) + 'GHz_Beam_' + str(beamChoice) + '_map' + str(mapPlot) + '.png', dpi=400)
#             if mapPlot == False:
#                 plt.plot(deltaNew-np.mean(deltaNew), label = plotLabel)
#         if mapPlot == False:
#             plt.xlabel('Port'); plt.ylabel('$\Delta \Theta$ [deg]')
#             plt.ylim([-45,45]);
#             plt.yticks(np.linspace(-45, 45, num=int(90/5)+1))
#             plt.grid('on')   
#             plt.legend(ncol=1, loc='lower right', fontsize=7)
#             plt.tight_layout()
            
#             plt.title(title)
#             plt.savefig(savePath + 'f_set_' + str(f_set) + 'GHz_Beam_' + str(beamChoice) + '_map' + str(mapPlot) + '.png', dpi=400)
        
# out = np.transpose(np.vstack([np.array(date_log), np.array(time_log), np.array(rig_log), np.array(beam_log), np.array(f_set_log), np.array(minmax_log), np.array(stdev_log)]))
# outSorted = out[np.argsort(out[:, 0])]