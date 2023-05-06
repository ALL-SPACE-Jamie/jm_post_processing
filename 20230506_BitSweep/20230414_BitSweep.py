import pandas as pd
import numpy as np
import matplotlib.pyplot as plt; plt.rcParams['font.size'] = 12
from scipy.stats import norm
import os
import glob
import copy
import csv
import json
import time
import matplotlib.colors as colors
from pylab import *
plt.close('all')

# file path
dirScript = os.getcwd()

# parmas

def find_measFiles(path, fileString):
    global measFiles, files
    files = []
    for root, directories, file in os.walk(path):
        for file in file:
            if (file.endswith(".csv"))==True:
                files.append(os.path.join(root,file))
    measFiles = []
    for i in range(len(files)):
        if fileString in files[i]:
            measFiles.append(files[i])
            
def load__measFiles(filePath):
    global meas_info, meas_array, meas_frequencies, meas_params, rfic_common_gain, attenuation_bits, phase_bits, meas_gain, meas_phase, fileName, f_s, beam
    meas_params = {}
    meas_info = []
    
    # meas_info, array and measurement frequencies
    with open(filePath, 'r') as file:
        filecontent = csv.reader(file, delimiter=',')
        time.sleep(0.10)
        for row in filecontent:
            meas_info.append(row)
            
        # info
        index_start = [index for index in range(len(meas_info)) if 'barcodes' in meas_info[index]][0]+2
        meas_info = meas_info[0:index_start]
        beam = meas_info[[index for index in range(len(meas_info)) if 'Beam' in meas_info[index]][0]][1]
        f_s = meas_info[[index for index in range(len(meas_info)) if 'f_s' in meas_info[index]][0]][1]
        
        # arrays
        rfic_common_gain = np.genfromtxt(filePath, delimiter=',', skip_header=index_start)[:,0]
        attenuation_bits = np.genfromtxt(filePath, delimiter=',', skip_header=index_start)[:,1]
        phase_bits = np.genfromtxt(filePath, delimiter=',', skip_header=index_start)[:,2]
        meas_array = np.genfromtxt(filePath, delimiter=',', skip_header=index_start)[:,3:]
        meas_gain = meas_array[:,::2]
        meas_phase = meas_array[:,1:][:,::2]
        meas_frequencies = np.array(meas_info[index_start-1][3:])[::2].astype(float)
        
        # file name
        fileName = filePath.split('\\')[-1]
        
def plot__2D(meas_array, f_s, GainOrPhase, common_gain, freqCol, beam):
    global common_gain_indexes, teamp, gain
    
    # hard-coded parameters
    bitList = [0, 16, 32, 48, 64, 80, 96, 112, 128]
    
    # set up figure
    fig = plt.subplots(figsize=(7,20))
    
    # set up 2D subplot
    ax = plt.subplot(3,1,1)
    
    # find indexes for common gain selection
    common_gain_indexes = np.where(rfic_common_gain == common_gain)[0]
    
    # format 3 arrays
    X = phase_bits[min(common_gain_indexes):max(common_gain_indexes)]
    Y = attenuation_bits[min(common_gain_indexes):max(common_gain_indexes)]
    if GainOrPhase == 'Gain':
        Z = meas_gain[:,freqCol][min(common_gain_indexes):max(common_gain_indexes)]
        unit = 'dB'
    if GainOrPhase == 'Phase':
        Z = meas_phase[:,freqCol][min(common_gain_indexes):max(common_gain_indexes)]
        unit = 'deg'
    
    # plot limits
    if GainOrPhase == 'Gain':
        vmin=-30; vmax=30; vstep = 10001
    if GainOrPhase == 'Phase':
        vmin=0; vmax=360; vstep = 10001
    levels = np.linspace(vmin, vmax, num=1001)
    ticks = np.linspace(vmin,vmax,num=5)
    
    # plot
    t = plt.tricontourf(X, Y, Z, cmap = cm.get_cmap('jet'), levels = levels)
    plt.colorbar(t,ticks=ticks, shrink=0.9, orientation="horizontal", pad = 0.15)
    
    # v & h lines
    for i in range(len(bitList)):
        plt.axvline(x = bitList[i], color='k', linestyle='--', alpha=0.3)
        plt.axhline(y = bitList[i], color='k', linestyle='--', alpha=0.3)

    # format plot
    plt.xlabel('Phase [bits]')
    plt.ylabel('Att [bits]')
    plt.xticks(np.linspace(0,128,num=int(128/16)+1))
    plt.xlim([0,128])
    plt.yticks(np.linspace(0,128,num=int(128/16)+1))
    plt.ylim([0,128])
    
    # secondary axes
    ax2 = ax.twiny(); ax3 = ax.twinx()
    ax2.set_xticks(np.linspace(0,360,num=9))
    ax3.set_yticks(np.linspace(0,0.25*128,num=9))
    ax2.set_xlabel('Phase [deg]')
    ax3.set_ylabel('Att [dB]')
    
    # title
    portInfoLoc = np.where(np.array(fileName.split('_')) == 'PORT')[0][0]
    lensInfoLoc = np.where(np.array(fileName.split('_')) == 'LENS')[0][0]
    plt.title(GainOrPhase + ' [' + unit + ']\nFrequency set = ' + f_s + 'GHz\nFrequency meas = ' + str(meas_frequencies[freqCol]) + 'GHz\nBeam ' + str(beam) + ', Lens ' + fileName.split('_')[lensInfoLoc+1] + ', Port ' + fileName.split('_')[portInfoLoc+1] + ', PaCG = ' + str(common_gain) + ' bits\n')

    # 1D plots
    for i in range(len(bitList)):
        
        # orthoganality
        x = X.copy()
        # find indexes for fixed plots
        gain_bits_indexes = np.where(Y.copy() == float(bitList[i]))[0]
        array = (Z.copy()[gain_bits_indexes])
        plt.subplot(3, 1, 2)
        if GainOrPhase == 'Gain':
            plt.plot(x[gain_bits_indexes], array-np.mean(array), 'o-', label = 'Att bits = ' + str(bitList[i]))
        if GainOrPhase == 'Phase':
            # wrap phase
            forPlot = array
            for j in range(len(forPlot)):
                for k in range(len(forPlot)-1):
                    if abs(forPlot[k+1] - forPlot[k]) > 180:
                        forPlot[k] = forPlot[k] -360.0
            for j in range(len(forPlot)):
                forPlotMean = np.mean(forPlot)
                if forPlotMean < -90.0:
                    forPlot = forPlot + 180.0
                if forPlotMean > 90.0:
                    forPlot = forPlot - 180.0
            # end wrap phase
            plt.plot(x[gain_bits_indexes], forPlot, 'o-', label = 'Att bits = ' + str(bitList[i]))
        # format
        plt.grid(b=True, which='major', color='k', linestyle='-')
        plt.grid(b=True, which='minor', color='k', linestyle=':', alpha=0.5)
        plt.minorticks_on()
        plt.legend(loc='lower center', ncol = 3, fontsize=10)
        if GainOrPhase == 'Gain':
            plt.xticks(np.linspace(0,128,num=int(128/16)+1))
            plt.xlim([0,128])
            plt.yticks(np.linspace(-50,50,num=int(100/1)+1))
            plt.ylim([-10,10])
            plt.xlabel('Phase [bits]');plt.ylabel('$\Delta$ Gain [dB]')
        if GainOrPhase == 'Phase':
            plt.xticks(np.linspace(0,128,num=int(128/16)+1))
            plt.xlim([0,128])
            plt.yticks(np.linspace(-360,360,num=int(720/45)+1))
            plt.ylim([-360,360])
            plt.xlabel('Phase [bits]');plt.ylabel('Phase [deg]')
        
        # linearity
        x = Y.copy()
        # find indexes for fixed plots
        phase_bits_indexes = np.where(X.copy() == float(bitList[i]))[0]
        array = (Z.copy()[phase_bits_indexes])
        plt.subplot(3, 1, 3)
        if GainOrPhase == 'Gain':
            plt.plot(x[phase_bits_indexes], array, 'o-', label = 'Att bits = ' + str(bitList[i]))
        if GainOrPhase == 'Phase':
            # wrap phase
            forPlot = array-np.mean(array)
            for j in range(len(forPlot)):
                for k in range(len(forPlot)-1):
                    if abs(forPlot[k+1] - forPlot[k]) > 180:
                        forPlot[k+1] = forPlot[k+1] -360.0
            for j in range(len(forPlot)):
                forPlotMean = np.mean(forPlot)
                if forPlotMean < -90.0:
                    forPlot = forPlot + 180.0
                if forPlotMean > 90.0:
                    forPlot = forPlot - 180.0
            # end wrap phase
            forPlot = forPlot-np.mean(forPlot)
            plt.plot(x[phase_bits_indexes], forPlot, 'o-', label = 'Att bits = ' + str(bitList[i]))
        # format
        plt.grid(b=True, which='major', color='k', linestyle='-')
        plt.grid(b=True, which='minor', color='k', linestyle=':', alpha=0.5)
        plt.minorticks_on()
        plt.legend(loc='lower center', ncol = 3, fontsize=10)
        if GainOrPhase == 'Gain':
            plt.xticks(np.linspace(0,128,num=int(128/16)+1))
            plt.xlim([0,128])
            plt.yticks(np.linspace(-50,50,num=int(100/5)+1))
            plt.ylim([-30,30])
            plt.xlabel('Att [bits]');plt.ylabel('Gain [dB]')
            plt.savefig(fileName + str(str(meas_frequencies[freqCol])) + '_Gain.png', dpi=400)
        if GainOrPhase == 'Phase':
            plt.xticks(np.linspace(0,128,num=int(128/16)+1))
            plt.xlim([0,128])
            plt.yticks(np.linspace(-360,360,num=int(720/45)+1))
            plt.ylim([-360,360])
            plt.xlabel('Att [bits]'); plt.ylabel(r'$\Delta$ Phase [deg]')
            plt.savefig(fileName + str(str(meas_frequencies[freqCol])) + '_Phase.png', dpi=400)

# run            
find_measFiles(r'C:\codeRun\_____results\bitSweep\example', 'SWEEP')
count = 0
for measFile in measFiles:
    load__measFiles(measFile)
    for freqCol in range(len(meas_frequencies)):
        plot__2D(meas_array, f_s, 'Gain', 32, freqCol, beam)
        plot__2D(meas_array, f_s, 'Phase', 32, freqCol, beam)
        plt.close('all')
        count = count + 1
        print(count)
        stop