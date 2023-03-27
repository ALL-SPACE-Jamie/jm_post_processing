import pandas as pd
import numpy as np
import matplotlib.pyplot as plt; plt.rcParams['font.size'] = 12
colMap = ['r', 'g', 'b', 'c', 'm', 'k']
import matplotlib.backends.backend_pdf
from scipy.stats import norm
import os
import glob
import copy
import csv
import json
import time
plt.close('all')

# file path
dirScript = os.getcwd()

# definitions
def find__measFiles(path, fileString):
    global measFiles, files
    files = []
    for root, directories, file in os.walk(path):
    	for file in file:
    		if(file.endswith(".csv")):
    			files.append(os.path.join(root,file))
    measFiles = []
    for i in range(len(files)):
        if fileString in files[i]:
            measFiles.append(files[i])
            
def load__measFiles(filePath):
    global meas_info, meas_array, meas_frequencies, meas_params, rf_paths
    meas_params = {}
    meas_info = []
    # meas_info, array and measurement frequencies
    with open(filePath, 'r') as file:
        filecontent = csv.reader(file, delimiter=',')
        time.sleep(0.01)
        for row in filecontent:
            meas_info.append(row)
        index_start = [index for index in range(len(meas_info)) if 'rf_path' in meas_info[index]][0]+2
        meas_frequencies = np.array(meas_info[index_start-2][2:][::4]).astype(float)
        meas_array = np.genfromtxt(filePath, delimiter=',', skip_header=index_start-1)[:,4:][:,::4]
        rf_paths = np.genfromtxt(filePath, dtype=str, delimiter=',', skip_header=index_start-1)[:,0]
         
## Run
find__measFiles(r'C:\codeRun\_PCS-Rig\_data\pcs24_dataset', '') ## !HARD-CODED! ##

# open a blank pdf 
pdf = matplotlib.backends.backend_pdf.PdfPages("output.pdf")

# loop through measurement files
for j in range(len(measFiles)):
    load__measFiles(measFiles[j])
    fig = plt.figure()
    ax = plt.subplot(111)
    # loop through traces
    for i in range(len(rf_paths)):
        plt.plot(meas_frequencies, meas_array[i,:], colMap[i], linewidth=2.0, label=rf_paths[i])
        # plot format
        plt.title(measFiles[j].split('\\')[-1][0:-4], fontsize=10)
        plt.grid(b=True, which='major', color='k', linestyle='-')
        plt.grid(b=True, which='minor', color='k', linestyle=':', alpha=0.5)
        plt.minorticks_on()
        plt.legend(loc='lower right')
        plt.ylim([-100,50])
        plt.xlim([min(meas_frequencies), max(meas_frequencies)])
        plt.xlabel('Frequency [GHz]'); plt.ylabel('Amplitude [dB]')
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.05, box.width, box.height * 0.95])
        ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.5), fancybox=True, shadow=True, ncol=2, fontsize=10)
    # save figure to pdf
    pdf.savefig(fig)
# close pdf
pdf.close()




    
    
    
    