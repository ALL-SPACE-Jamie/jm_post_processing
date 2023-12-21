import pandas as pd
import numpy as np
import matplotlib.pyplot as plt;
plt.rcParams['font.size'] = 12
import matplotlib.backends.backend_pdf
from matplotlib import cm, colors
from scipy.stats import norm
import os
import glob
import copy
import csv
import json
import time
from pylab import *
import seaborn as sns
from matplotlib.markers import MarkerStyle
plt.close('all')

# file path
dirScript = os.getcwd()

# parameters
file_path = r'C:\Users\jmitchell\OneDrive - ALL.SPACE\I-Type\Tx_TLM_I-Type\TLM_Calibration_Measurements\Batch_7\Raw_Data'
file_type = 'RFA'
number_ports = 288
number_ports = 456
gain_phase = 'phase'
freq_list = [17.7, 18.2, 18.7, 19.2, 19.7, 20.2, 20.7, 21.2]
freq_list = [27.5, 28.0, 28.5, 29.0, 29.5, 30.0, 30.5, 31.0]
median_shift = True
data_plot = False

# hard coded inputs
map_tlm = np.genfromtxt(r'C:\Users\jmitchell\Documents\GitHub\Post-Processing\20230601_TLM-Comparison\Mrk1_S2000_TLM_TX_ArrayGeometry_V20062022_CalInfo.csv', skip_header=2, dtype=float, delimiter=',')

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
        if fileString in files[i] and 'eam' + str(beam) in files[i] and 'rchive' not in files[i]:
            measFiles.append(files[i])

def load__measFiles(file_path):
    global meas_info, meas_params, meas_array, meas_frequencies, meas_array_gain, meas_array_phase, paramName, i
    if os.path.getsize(file_path) > 2000:
        meas_params = {}
        meas_info = []
    
        # meas_info, array and measurement frequencies
        with open(file_path, 'r') as file:
            filecontent = csv.reader(file, delimiter=',')
            for row in filecontent:
                meas_info.append(row)
            index_start = [index for index in range(len(meas_info)) if 'barcodes' in meas_info[index]][0] + 2
            meas_info = meas_info[0:index_start]
            meas_array = np.genfromtxt(file_path, delimiter=',', skip_header=index_start)
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

def plot_phaseDrift(deltaNew, title, cmin, cmax, cstp, f_set):
    global Z, Y, x, y, rot
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

    
    print(meas_frequencies-f_set)
    col = np.argmin((meas_frequencies-f_set)**2)
    Z = deltaNew[:]#-np.mean(deltaNew)
    Z = Z[1:][::2]
    Y=3e8/(f_set*1e9)
    # Z = 1000.0*Z/360.0*Y
    
    ### issue here with rotation and colmap
    cseg = int((cmax-cmin)/cstp)
    for j in range(len(x)):
        m = MarkerStyle("s")
        m._transform.rotate_deg(float(rot[j])); print((rot[j]))
        plt.scatter(x[j], y[j], c=Z[j], marker=m, s=150, edgecolors='black', vmin=cmin, vmax=cmax, cmap = cm.get_cmap('jet', cseg))
    plt.colorbar()

    plt.clim(cmin, cmax)
    plt.xlabel('X [mm]'); plt.ylabel('Y [mm]')
    plt.title(title)
    plt.xlim([-75,75])
    plt.tight_layout()
    stop

def plot_spread_boxplot(file_type: str, number_ports: int, gain_phase: str, freq_list, median_shift: bool, data_plot: bool, file_path: str, plot_type: str):
    global forPlot
    # set up
    failed_port_dict = {}
    failed_port_dict[f'beam1'] = {}
    failed_port_dict[f'beam2'] = {}
    
    # creat blank pdf
    pdf = matplotlib.backends.backend_pdf.PdfPages(f"I3_{gain_phase}_BatchSpread_RFA-medianShifted{median_shift}.pdf")
    
    # loop through frequencies and beams
    for f_set in freq_list:
        for beam in [1, 2]:
            find_measFiles(file_path, file_type, 1)
            meas_array_gain_boards = np.zeros([number_ports, 0])
            meas_array_phase_boards = np.zeros([number_ports, 0])
            boards = []
            
            # collate port values for all boards and store in array
            for tlm in range(len(measFiles)):
                load__measFiles(measFiles[tlm])
                if meas_params['f_c'] == str(f_set):
                    col = np.argmin((meas_frequencies-f_set)**2)
                    gain_col = meas_array_gain[:, col]
                    phase_col = meas_array_phase[:, col]
                    meas_array_gain_boards = np.hstack((meas_array_gain_boards, gain_col.reshape((number_ports,1))))
                    meas_array_phase_boards = np.hstack((meas_array_phase_boards, phase_col.reshape((number_ports,1))))
                    boards.append(meas_params['barcodes'])
            
            # transpose the array undo some phase wrapping if applicable)
            if gain_phase == 'gain':
                meas_array_boards = np.transpose(meas_array_gain_boards)*1.0
            if gain_phase == 'phase':
                meas_array_boards = np.transpose(meas_array_phase_boards)*1.0
                for i in range(np.shape(meas_array_boards)[1]):
                    col = meas_array_boards[:,i]*1.0
                    if np.subtract(*np.percentile(col, [75, 25])) > 180.0:
                        for j in range(len(col)):
                            if col[j] < 180.0:
                                col[j] = col[j] + 360.0
                        meas_array_boards[:,i] = col*1.0
            
            # shift the data by the median if required
            if median_shift == True:
                for i in range(np.shape(meas_array_boards)[1]):
                    forNorm = meas_array_boards[:,i]*1.0
                    meas_array_boards[:,i] = forNorm-np.median(forNorm)
                    
            # make the array into a dataframe
            meas_array_boards = pd.DataFrame(data=meas_array_boards, columns=list(range(1,number_ports+1)))
            
            # make a figure
            fig = plt.figure(figsize=(20,10))
            ax = plt.subplot(111)
            
            # plot
            df = meas_array_boards
            if plot_type == 'box':
                sns.boxplot(data=df, color='b')
                if data_plot == True:
                    sns.stripplot(data=df, color='b', dodge=True)
            if plot_type == '2D':
                forPlot = np.array(np.std(meas_array_boards, axis=0, ddof=1))
                forPlot = np.subtract(*np.percentile(meas_array_boards, [75, 25], axis=0))
                plot_phaseDrift(forPlot, 'Phase (arb.) [dB]', 10.0, 40.0, 0.5, float(meas_params['f_c']))
                
            
            # quantify failures
            failed_ports = []
            for key in df.keys():
                check = np.array(df[key])
                if gain_phase == 'gain':
                    if np.subtract(*np.percentile(check, [75, 25])) > 10.0 or np.median(check) < np.median(np.array(df)) - 10.0:
                        if np.subtract(*np.percentile(check, [75, 25])) > 10.0 and np.median(check) < np.median(np.array(df)) - 10.0:
                            maker_size = 10.0
                        plt.axvline(float(key) -1.0, color = 'r', linestyle = '--')
                        failed_ports.append(str(key))
                if gain_phase == 'phase':
                    if np.subtract(*np.percentile(check, [75, 25])) > 60.0:
                        plt.axvline(float(key) -1.0, color = 'r', linestyle = '--')
                        failed_ports.append(str(key))
            failed_port_dict[f'beam{beam}'][str(f_set)] = failed_ports
                    
            # label failed ports on stat graph
            plt.text(.01, .98, 'Failed ports: ' + str(failed_ports), ha='left', va='top', transform=ax.transAxes, bbox=dict(facecolor='white', edgecolor='black'))
                
            # plot formatting
            if plot_type == 'box':
                if gain_phase == 'gain':
                    plt.ylim([-10,10])
                    if median_shift == False:
                        plt.ylim([0,50])
                if gain_phase == 'phase':
                    plt.ylim([-180,180])
                    if median_shift == False:
                        plt.ylim([0,360+180])
                plt.xlim([-1,number_ports-1])
                plt.xlabel('port')
                plt.xticks(list(np.linspace(1,number_ports+1, num = int(number_ports/4)+1)),rotation=90, fontsize=8)
                plt.grid(axis = "x", which='minor', alpha=0.5)
                plt.minorticks_on()
                plt.grid(which='major')
                plt.ylabel(f'{gain_phase} deviation from batch')
            plt.title(f'{gain_phase}: {file_type}, beam = {beam}, f_set = {(f_set)} GHz')
            plt.tight_layout()
    
            # save figure to pdf
            pdf.savefig(fig)
            # plt.close('all')
    
    # global failed ports plot
    fig,ax=plt.subplots(figsize=(20,10))
    colMap = ['rx', 'b+']
    count = 0
    for key in failed_port_dict.keys():
        print(key)
        for key2 in failed_port_dict[key].keys():
            print(f'{key2} GHz')
            print(failed_port_dict[key][key2])
            array = np.array(failed_port_dict[key][key2]).astype(float)
            plt.plot(array*0.0+float(key2), array, colMap[count])
            for port in array:
                plt.text(float(key2) + 0.1, port, str(int(port)) + '(' + str(int(mod(int(port),number_ports/3))) + ')')
        count=count+1
    plt.grid('on')
    plt.xlabel('freq [GHz]')
    plt.ylabel('port')
    plt.ylim([0,number_ports])
    minorLocator = MultipleLocator(2)
    ax.yaxis.set_minor_locator(minorLocator)
    plt.grid(which='minor')
    plt.title(f'Ports with high {gain_phase} correction spread between TLMs')
    plt.tight_layout()
    pdf.savefig(fig)
    
    # close pdf
    pdf.close()
    
# run
# plot_spread_boxplot(file_type, number_ports, 'gain', freq_list, False, data_plot, file_path, 'box')
plot_spread_boxplot(file_type, number_ports, 'phase', freq_list, True, data_plot, file_path, '2D')