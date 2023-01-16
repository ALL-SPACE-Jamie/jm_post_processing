import pandas as pd
import numpy as np
import matplotlib.pyplot as plt; plt.rcParams['font.size'] = 18
import os
import glob
import csv
plt.close('all')

HFSS_offset = 5.0
col = 30

# load
fileName = '2022_12_13_discrete_17700_21200_8_calibration_data_L1L6_48feed_v10_L6_89_10RX_BS2_calibration_13mm_dual_pol_probe_rotated'
dirScript = os.getcwd()
os.chdir(dirScript)
dfFull = pd.read_csv(fileName + ".csv")

# reduce
df = pd.read_csv(fileName + ".csv")
df = df[(df["Freq [GHz]"] == 17.7)]
mask = np.transpose(np.array(df))[2:]
maskSingle = np.transpose(np.array(df))[2:]
for i in range(2):
    mask = np.vstack((mask,maskSingle))
maskAmp = mask[::2]
maskPhase = mask[1:][::2]
maskAmpMax = []
for val in maskAmp: maskAmpMax.append(max(val))
maskPhaseSelected = []
for i in range(len(maskPhase)):
    if maskAmp[i,0] == maskAmpMax[i]:
        maskPhaseSelected.append(maskPhase[i,0])
    else:
        maskPhaseSelected.append(maskPhase[i,1])
        
# load files
os.chdir(os.path.join(dirScript, 'iteration_1'))
fileLog = glob.glob('*OP_*Beam1*.csv')
temp = np.genfromtxt(fileLog[0],skip_header = 22)
csvFile = []
with open(fileLog[0],'r')as file:
    filecontent=csv.reader(file,delimiter=',')
    for row in filecontent:
        csvFile.append(row)
measData = np.array(csvFile[22:]).astype(float)
gainMeas = measData[:,col]
phaseMeas = measData[:,col+1]

# gain plot iteration 1
plt.figure(figsize=(9,7))
plt.plot(gainMeas,'ks',label='meas')
plt.plot(np.array(maskAmpMax)+HFSS_offset,'b^',label='mask')
# format
plt.xlabel('Port'); plt.ylabel('Gain [dB]')
plt.xlim([0,300]);plt.ylim([-40,10])
plt.grid()
plt.legend(loc='lower right')

# load files
os.chdir(os.path.join(dirScript, 'iteration_2'))
fileLog = glob.glob('*OP_*Beam1*.csv')
temp = np.genfromtxt(fileLog[0],skip_header = 22)
csvFile = []
with open(fileLog[0],'r')as file:
    filecontent=csv.reader(file,delimiter=',')
    for row in filecontent:
        csvFile.append(row)
measData = np.array(csvFile[22:]).astype(float)
gainMeas = measData[:,col]
phaseMeas = measData[:,col+1]

# gain plot iteration 2
plt.figure(figsize=(9,7))
plt.plot(gainMeas,'ks',label='meas corrected')
plt.plot(np.array(maskAmpMax)+HFSS_offset,'b^',label='mask')
# format
plt.xlabel('Port'); plt.ylabel('Gain [dB]')
plt.xlim([0,300]);plt.ylim([-40,10])
plt.grid()
plt.legend(loc='lower right')

# load files
os.chdir(os.path.join(dirScript, 'iteration_1'))
fileLog = glob.glob('*OP_*Beam1*.csv')
temp = np.genfromtxt(fileLog[0],skip_header = 22)
csvFile = []
with open(fileLog[0],'r')as file:
    filecontent=csv.reader(file,delimiter=',')
    for row in filecontent:
        csvFile.append(row)
measData = np.array(csvFile[22:]).astype(float)
gainMeas = measData[:,col]
phaseMeas = measData[:,col+1]

# phase plot iteration 1
plt.figure(figsize=(9,7))
plt.plot(phaseMeas-180.0,'ks',label='meas')
plt.plot(maskPhaseSelected,'b^',label='mask')
# format
plt.xlabel('Port'); plt.ylabel('Phase [deg]')
plt.xlim([0,300]);plt.ylim([-180,180])
plt.grid()
plt.legend(loc='lower right')

# load files
os.chdir(os.path.join(dirScript, 'iteration_2'))
fileLog = glob.glob('*OP_*Beam1*.csv')
temp = np.genfromtxt(fileLog[0],skip_header = 22)
csvFile = []
with open(fileLog[0],'r')as file:
    filecontent=csv.reader(file,delimiter=',')
    for row in filecontent:
        csvFile.append(row)
measData = np.array(csvFile[22:]).astype(float)
gainMeas = measData[:,col]
phaseMeas = measData[:,col+1]

# phase plot iteration 2
plt.figure(figsize=(9,7))
plt.plot(phaseMeas-180.0,'ks',label='meas corrected')
plt.plot(maskPhaseSelected,'b^',label='mask')
# format
plt.xlabel('Port'); plt.ylabel('Phase [deg]')
plt.xlim([0,300]);plt.ylim([-180,180])
plt.grid()
plt.legend(loc='lower right')


