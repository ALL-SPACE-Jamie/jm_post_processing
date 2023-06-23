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

plt.close('all')

# file path
dirScript = os.getcwd()

# parmas
filePath = r'C:\\Scratch\\misc'
txrx = 'tx'
ymin=-20; ymax=30

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


def load__measFiles(filePath):
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
        meas_array_gain = meas_array[:, ::2]
        meas_array_phase = meas_array[:, 1:][:, ::2]
        meas_frequencies = np.array(meas_info[index_start - 1])[::2].astype(float)


def plot__channels(quad, lin, lens):
    global meas_array_plot, rfics
    # make port maps
    ports = np.linspace(1, len(meas_array_gain), num=len(meas_array_gain))
    port2IC = []
    port2chan = []
    port2pol = []
    for i in range(int(len(ports) / 3)):
        for j in range(len(S2000_TX_RFIC_PORT_MAP)):
            forCheck = S2000_TX_RFIC_PORT_MAP[str(j + 1)]
            if int(i + 1) in forCheck:
                port2IC.append(j + 1)
                port2chan.append(S2000_TX_RFIC_CHANNEL_MAP[str(i + 1)][0])
                port2pol.append(S2000_TX_RFIC_CHANNEL_MAP[str(i + 1)][1])

    # make df
    ports = np.reshape(ports[0:int(len(ports) / 3)],
                       (-1, 1)) + 1000.0  # added for panda sort function (to subtract later)
    port2IC = np.array(port2IC)
    port2IC = np.reshape(port2IC, (-1, 1)).astype(float) + 1000.0  # added for panda sort function (to subtract later)
    port2chan = np.array(port2chan)
    port2chan = np.reshape(port2chan, (-1, 1))
    port2pol = np.array(port2pol)
    port2pol = np.reshape(port2pol, (-1, 1))
    meas_array_gain_lens1 = meas_array_gain[
                            (lens - 1) * int(len(meas_array_gain) / 3):lens * int(len(meas_array_gain) / 3), :]
    df_gain_lens1 = np.hstack([ports, port2IC, port2chan, port2pol, meas_array_gain_lens1])
    headers = np.transpose(np.reshape(
        np.hstack([np.array(['port']), np.array(['RFIC']), np.array(['Chan']), np.array(['Pol']), meas_frequencies]),
        (-1, 1)))
    df_gain_lens1 = np.vstack([headers, df_gain_lens1])
    df_gain_lens1 = pd.DataFrame(df_gain_lens1)
    df_gain_lens1.columns = df_gain_lens1.iloc[0]
    df_gain_lens1 = df_gain_lens1.drop(df_gain_lens1.index[0])

    # sort fd
    df_gain_lens1 = df_gain_lens1.sort_values(by=['port'])

    # refine df
    df_gain_lens1 = df_gain_lens1[df_gain_lens1['Pol'] == lin]
    df_gain_lens1 = df_gain_lens1[df_gain_lens1['Chan'] == quad]

    # seperate arrays
    rfics = ((np.array(df_gain_lens1['RFIC']).astype(float) - 1000.0).astype(int)).astype(str)
    ports = np.array(df_gain_lens1['port']).astype(float) - 1000.0
    for i in range(len(rfics)):
        rfics[i] = '(' + rfics[i] + ') ' + str(int(ports[i]))
    meas_array_plot = (np.array(df_gain_lens1)[:, 4:]).astype(float)


def archive__2DPlot():
    # 2D plot
    fig = plt.figure(figsize=(10, 10))
    ax = plt.axes(projection='3d')
    ax.set_box_aspect(aspect=(2, 2, 2))
    x = ports.copy()
    y = meas_frequencies.copy()
    X, Y = np.meshgrid(x, y)
    Z = meas_array_plot.copy()
    Z = np.transpose(Z)
    surf = ax.plot_surface(X, Y, Z, cmap=cm.coolwarm,
                           linewidth=0, antialiased=False)
    ax.set_xticks(x)
    ax.set_xticklabels(rfics, fontsize=7, rotation=45)
    plt.close('all')


## run

def dict__maps(txrx):
    global S2000_TX_RFIC_CHANNEL_MAP, S2000_TX_RFIC_PORT_MAP
    if txrx == 'rx':
        with open('rx_s2000_channel_map.json') as json_file:
            S2000_TX_RFIC_CHANNEL_MAP = json.load(json_file)
        with open('rx_s2000_rfic_map.json') as json_file:
            S2000_TX_RFIC_PORT_MAP = json.load(json_file)
    if txrx == 'tx':
        with open('S2000_TX_RFIC_CHANNEL_MAP.json') as json_file:
            S2000_TX_RFIC_CHANNEL_MAP = json.load(json_file)
        with open('S2000_TX_RFIC_PORT_MAP.json') as json_file:
            S2000_TX_RFIC_PORT_MAP = json.load(json_file)


dict__maps(txrx)

for beamNo in range(2):
    find_measFiles(filePath, 'OP_', beamNo + 1)
    for measFile in measFiles:
        load__measFiles(measFile)
        for k in range(3):
            lens = k + 1
            fig, axs = plt.subplots(4, 2, figsize=(15, 10))
            chanCycle = [0, 0, 1, 1, 2, 2, 3, 3]
            linCycle = ['V', 'H', 'V', 'H', 'V', 'H', 'V', 'H']
            axsRows = [0, 0, 1, 1, 2, 2, 3, 3];
            axsCols = [0, 1, 0, 1, 0, 1, 0, 1]
            for j in range(8):
                plot__channels(str(chanCycle[j]), linCycle[j], lens)
                for i in range(len(rfics)):
                    axs[axsRows[j], axsCols[j]].plot(meas_frequencies, meas_array_plot[i, :], label=rfics[i])
                axs[axsRows[j], axsCols[j]].set_xlabel('Frequency [GHz]');
                axs[axsRows[j], axsCols[j]].set_ylabel('S$_{21}$ [dB]')
                axs[axsRows[j], axsCols[j]].set_ylim([ymin, ymax])
                if txrx == 'rx':
                    axs[axsRows[j], axsCols[j]].set_xlim([17.7, 21.2])
                else:
                    axs[axsRows[j], axsCols[j]].set_xlim([27.5, 31.0])
                axs[axsRows[j], axsCols[j]].set_yticks(np.linspace(ymin,ymax, num=int(50 / 5) + 1))
                axs[axsRows[j], axsCols[j]].grid('on')
                axs[axsRows[j], axsCols[j]].legend(fontsize=8, ncol=5, loc='lower right')
                axs[axsRows[j], axsCols[j]].set_title('C' + str(chanCycle[j]) + '-' + linCycle[j])
            beam = meas_info[[index for index in range(len(meas_info)) if 'Beam' in meas_info[index]][0]][1]
            f_c = meas_info[[index for index in range(len(meas_info)) if '# f_c' in meas_info[index]][0]][1]
            qr = meas_info[[index for index in range(len(meas_info)) if 'barcodes' in meas_info[index]][0]][1]
            power = meas_info[[index for index in range(len(meas_info)) if 'Source power [dBm]' in meas_info[index]][0]][1]
            title = 'Board ' + qr + ', Lens ' + str(lens) + ', Beam' + str(beam) + ', f$_{set}$=' + str(
                f_c) + ' GHz' + ', P=' + power + ' dBm'
            fig.suptitle(title, fontsize=25)
            plt.tight_layout()
            savePath = ""
            for l in range(len(measFile.split('\\')[0:-1])):
                savePath = savePath + '\\' + measFile.split('\\')[0:-1][l]
            savePath = savePath[1:]
            plt.savefig(savePath + '\\' + title + '.png', dpi=400);
            plt.close('all')
print('-----Finished-----')