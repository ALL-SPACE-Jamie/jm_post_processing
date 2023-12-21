import pandas as pd
import numpy as np
import matplotlib.pyplot as plt;
plt.rcParams['font.size'] = 12
from scipy.stats import norm
import os
import glob
import copy
import csv
import json
import time
from pylab import *
colMap = ['r','g','b','k','m','c','r','g','b','k','m','c','r','g','b','k','m','c','r','g','b','k','m','c','r','g','b','k','m','c','r','g','b','k','m','c','r','g','b','k','m','c']

plt.close('all')

# file path
dirScript = os.getcwd()

# parmas
filePath = r'C:\Users\RyanFairclough\Downloads\HFSS_Offset_Mod tx'
savePath = r'C:\Users\RyanFairclough\Downloads\HFSS_Offset_Mod tx'
fileType='RFA_'
termType='I-Type_I2'
tlmType= 'Tx'
freqTxt='0_GHz_45C'
ymax_RFA=60
ymax_hist=50
xmax_hist=30
if tlmType=='Rx':
    freqList = [17.7, 18.2, 18.7, 19.2, 19.7, 20.2, 20.7, 21.2]
elif tlmType=='Tx':
    freqList = [27.5, 28.0, 28.5, 29.0, 29.5, 30.0, 30.5, 31.0]


# definitions
def find_measFiles(path, fileString, beam, freqSelect):
    global measFiles, files
    files = []
    #print[str(freqSelect)]
    for root, directories, file in os.walk(path):
        for file in file:
            if (file.endswith(".csv")) == True:
                files.append(os.path.join(root, file))
    measFiles = []
    for i in range(len(files)):
        if fileString in files[i] and 'eam' + str(beam) in files[i] and 'rchive' not in files[i] and str(freqSelect) in files[i]:
            measFiles.append(files[i])

def load__measFiles(filePath):
    global meas_info, meas_params, meas_array, meas_frequencies, meas_array_gain, meas_array_phase, paramName, i
    if os.path.getsize(filePath) > 2000:
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
            if len(meas_params[paramName]) > 0:
                if meas_params[paramName][0] == ' ':
                    meas_params[paramName] = meas_params[paramName][1:]

def plot__1D(filePath, fileString, beam, title, freqSelect, ymax_RFA,ymax_hist, xmax_hist):
    global selection
    find_measFiles(filePath, str(fileString)+str(2), beam, freqSelect)
    fig, axs = plt.subplots(3, 2, figsize=(15, 10))
    
    count = 0
    for measFile in measFiles:
        load__measFiles(measFile)
        fcol = np.argmin((meas_frequencies-float(meas_params['f_c']))**2)

        x = np.linspace(1, 1*int(len(meas_array_gain[:, fcol])/3), num = 1*int(len(meas_array_gain[:, fcol])/3))

        sty = ''
        if len(x) < 10:
            sty = 'o-'
        axs[0, 0].plot(x, meas_array_gain[:, fcol][0*int(len(meas_array_gain[:, fcol])/3):1*int(len(meas_array_gain[:, fcol])/3)], colMap[count] + sty, label = meas_params['barcodes'])
        axs[1, 0].plot(x, meas_array_gain[:, fcol][1*int(len(meas_array_gain[:, fcol])/3):2*int(len(meas_array_gain[:, fcol])/3)], colMap[count] + sty, label = meas_params['barcodes'])
        axs[2, 0].plot(x, meas_array_gain[:, fcol][2*int(len(meas_array_gain[:, fcol])/3):3*int(len(meas_array_gain[:, fcol])/3)], colMap[count] + sty, label = meas_params['barcodes'])
        count = count + 1
    for i in range(3):
        axs[i,0].set_ylim([0,ymax_RFA])
        axs[i,0].set_ylabel('S$_{12}$ [dB] (Lens ' + str(i+1) + ')')
        axs[i,0].set_xlabel('port')
        axs[i,0].grid('on')
        #axs[i,0].legend(loc='upper left')
    
    # histogram 
    w = 1
    count = 0
    for measFile in measFiles:
        load__measFiles(measFile)
        selection = meas_array_gain[:, fcol][0*int(len(meas_array_gain[:, fcol])/3):1*int(len(meas_array_gain[:, fcol])/3)]
        axs[0,1].hist(np.array(selection), bins=np.arange(min(selection), max(selection) + w, w), color=colMap[count], alpha = 0.5)
        axs[0,1].axvline(x=np.median(selection), color=colMap[count]); axs[0,1].text(np.median(selection)+1, ymax_hist*2/3, str(round((np.median(selection)),1)) + ' dB', rotation=90, color=colMap[count])
        selection = meas_array_gain[:, fcol][1*int(len(meas_array_gain[:, fcol])/3):2*int(len(meas_array_gain[:, fcol])/3)]
        axs[1,1].hist(np.array(selection), bins=np.arange(min(selection), max(selection) + w, w), color=colMap[count], alpha = 0.5)
        axs[1,1].axvline(x=np.median(selection), color=colMap[count]); axs[1,1].text(np.median(selection)+1, ymax_hist*2/3, str(round((np.median(selection)),1)) + ' dB', rotation=90, color=colMap[count])
        selection = meas_array_gain[:, fcol][2*int(len(meas_array_gain[:, fcol])/3):3*int(len(meas_array_gain[:, fcol])/3)]
        axs[2,1].hist(np.array(selection), bins=np.arange(min(selection), max(selection) + w, w), color=colMap[count], alpha = 0.5)
        axs[2,1].axvline(x=np.median(selection), color=colMap[count]); axs[2,1].text(np.median(selection)+1, ymax_hist*2/3, str(round((np.median(selection)),1)) + ' dB', rotation=90, color=colMap[count])
        count = count + 1
    
    for i in range(3):
        axs[i,1].set_ylim([0,ymax_hist])
        axs[i,1].set_xlim([-10,xmax_hist])
        if 'RFC' in title:
            axs[i,0].set_xticks(x, ['A', 'B'])
            axs[i,0].set_xlim([0.8, 3.2])
        if 'OP_C' in title:
            axs[i,0].set_xticks(x, ['A', 'B', 'COMB'])
            axs[i,0].set_xlim([0.8, 3.2])
        axs[i,1].set_xlabel('dB (lens ' + str(i+1) + ')')
        axs[i,1].set_ylabel('Spread Lens ' + str(i+1) )
        axs[i,1].grid('on')
    fig.suptitle(title + ' \nfreq=' + str(meas_params['f_c']) + 'GHz, beam' + str(beam), fontsize=25)
    plt.tight_layout()
    plt.savefig(savePath + '\\' +  title + ' beam' + str(beam) + '.png')
    


##### run #####
for l in range(len(freqList)):
    for k in range(2):
        plot__1D(filePath, fileType,k+1, fileType + termType+'_'+tlmType+'_'+'Freq_' + str(freqList[l]), str(freqList[l])+freqTxt, ymax_RFA,ymax_hist,xmax_hist)

# def dict__maps(txrx):
#     global S2000_TX_RFIC_CHANNEL_MAP, S2000_TX_RFIC_PORT_MAP
#     if txrx == 'rx':
#         with open('rx_s2000_channel_map.json') as json_file:
#             S2000_TX_RFIC_CHANNEL_MAP = json.load(json_file)
#         with open('rx_s2000_rfic_map.json') as json_file:
#             S2000_TX_RFIC_PORT_MAP = json.load(json_file)
#     if txrx == 'tx':
#         with open('S2000_TX_RFIC_CHANNEL_MAP.json') as json_file:
#             S2000_TX_RFIC_CHANNEL_MAP = json.load(json_file)
#         with open('S2000_TX_RFIC_PORT_MAP.json') as json_file:
#             S2000_TX_RFIC_PORT_MAP = json.load(json_file)
#
# dict__maps('tx')
# df = pd.read_csv(os.path.join(dirScript, 'inputs', 'Mrk1_S2000_TLM_TX_ArrayGeometry_V20062022_CalInfo.csv'), header=1)
# fcol = np.argmin((meas_frequencies-float(meas_params['f_c']))**2)
# selection = meas_array_gain[:, fcol]
# ports = np.linspace(1,len(selection), num=len(selection))
# plt.figure()
# x = []
# y = []
# a = []
# for i in ports[0:int(len(ports)/3)]:
#     if S2000_TX_RFIC_CHANNEL_MAP[str(int(i))][1] == 'V':
#         portdf = df.iloc[[i]]
#         x.append(float(portdf[' Feed x [mm]']))
#         y.append(float(portdf[' Feed y [mm]']))
#         print(portdf['Lens no.'])
#         a.append(selection[int(i)])
# colSeg = 1
# plt.scatter(x, y, c=a, cmap = cm.get_cmap('jet', colSeg))
# plt.colorbar()
# # ranges
# # plt.clim(cmin, cmax); plt.xlim([xmin, xmax]); plt.ylim([ymin,ymax])
        
    