import numpy as np
import os
import csv
import matplotlib.pyplot as plt
plt.close('all')
font = {'family' : 'normal',
'size' : 18}
plt.rc('font', **font)
colMap = []
for i in range(1000):
    colMap.append('r')
    colMap.append('g')
    colMap.append('b')
    colMap.append('c')
    colMap.append('m')
    colMap.append('y')
    colMap.append('r')
    colMap.append('g')
    colMap.append('b')
    colMap.append('c')
    colMap.append('m')
    colMap.append('y')

# definitions

def find__csvfiles(path, filterSTR, filterSTR2):
    global filesCSV
    files = []
    for root, directories, file in os.walk(path):
    	for file in file:
    		if(file.endswith(".csv")):
    			files.append(os.path.join(root,file))
    filesCSV = []
    for i in range(len(files)):
        if filterSTR in files[i] and filterSTR2 in files[i]:
            filesCSV.append(files[i])
            
def load__CSV(filePath):
    global meas_array, meas_info
    meas_info = []
    with open(filePath, 'r')as file:
        filecontent = csv.reader(file, delimiter=',')
        for row in filecontent:
            meas_info.append(row)
        meas_info = meas_info[6]
        meas_array = np.genfromtxt(filePath, delimiter=',', skip_header=7, skip_footer=1)
            
def plot__CCG(l, r, CCG, PaCGlog):
    find__csvfiles(r'C:\codeRun\KeysightVNAFiles', Lens, CCG)
    for j in range(len(filesCSV)):
        load__CSV(filesCSV[j])
        f = meas_array[:,0]/1.0e9
        amp = meas_array[:,1]
        PaCG = float(filesCSV[j].split('\\')[-1].split('.')[0].split('_')[4][3:])
        PaCG_loc = np.argmin((np.array(PaCGlog)-PaCG)**2)
        colPlot = colLog[PaCG_loc]
        axs[l, r].plot(f, amp, colPlot)
        maxLoc = np.argmax(amp)
        axs[l, r].plot(f[maxLoc], amp[maxLoc], colPlot+'v', markersize=10, label = filesCSV[j].split('\\')[-1].split('.')[0])
        axs[l, r].text(f[maxLoc]+0.05, amp[maxLoc], str(round(f[maxLoc],2)) + ' GHz')
        axs[l, r].set(xlabel='Freq [GHz]', ylabel='S$_{21}$ [dB]')
        axs[l, r].set(ylim=[-50, 80], xlim = [17.5, 21.5])
        axs[l, r].grid('on')
        axs[l, r].legend(fontsize=15)
        axs[l, r].set_title(CCG)
        
PaCGlog = [12,24,36,48]
colLog = ['r','g','c','m']

fig, axs = plt.subplots(2, 2, figsize=(15,10))
Lens = 'L1'
plot__CCG(0, 0, 'CCG12', PaCGlog)
plot__CCG(0, 1, 'CCG24', PaCGlog)
plot__CCG(1, 0, 'CCG36', PaCGlog)
plot__CCG(1, 1, 'CCG48', PaCGlog)
fig.suptitle('LENS: ' + Lens, fontsize=30)

fig, axs = plt.subplots(2, 2, figsize=(15,10))
Lens = 'L2'
plot__CCG(0, 0, 'CCG12', PaCGlog)
plot__CCG(0, 1, 'CCG24', PaCGlog)
plot__CCG(1, 0, 'CCG36', PaCGlog)
plot__CCG(1, 1, 'CCG48', PaCGlog)
fig.suptitle('LENS: ' + Lens, fontsize=30)

fig, axs = plt.subplots(2, 2, figsize=(15,10))
Lens = 'L3'
plot__CCG(0, 0, 'CCG12', PaCGlog)
plot__CCG(0, 1, 'CCG24', PaCGlog)
plot__CCG(1, 0, 'CCG36', PaCGlog)
plot__CCG(1, 1, 'CCG48', PaCGlog)
fig.suptitle('LENS: ' + Lens, fontsize=30)