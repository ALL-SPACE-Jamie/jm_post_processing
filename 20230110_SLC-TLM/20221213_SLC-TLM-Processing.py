import pandas as pd
import numpy as np
import matplotlib.pyplot as plt; plt.close(); plt.rcParams['font.size'] = 18
import os
plt.close('all')
plt.figure(figsize=(9,7))

fileName = 'exampleData'

# load
dirScript = os.getcwd()
os.chdir(dirScript)
df = pd.read_excel(fileName + ".xlsx")

#reduce
df = df[(df["lens_enabled"] == 'l1e_l2e_l3e')]
df = df[(df["pa_phi_deg"] == 0)]
df = df[(df["cal_freq_GHz"] == 19.2)]
df = df[(df["freq_GHz"] == 19.2)]
df = df[(df["active_cal"] == 'S2000_RX_QR00003_LUT2dB_v3.tar')]
df = df[(df["beam_no"] == 1)]
df = df[(df["beam_no"] == 1)]
df = df[(df["group_name"] == 'LUT_2dB_8pa')]
# plot1
dfPlot = df[(df["entry_type"] == 'gain_at_peak')]
x = dfPlot['pa_theta_deg']
y = dfPlot['Gain_dB']
plt.plot(x,y,'ks',markersize=10,label='Peak')
# plot2
dfPlot = df[(df["entry_type"] == 'gain_at_requested_angle')]
x = dfPlot['pa_theta_deg']
y = dfPlot['Gain_dB']
plt.plot(x,y,'b^',markersize=10,label='Requested angle')
# format
plt.xlabel('Theta [deg]'); plt.ylabel('Gain [dB]')
plt.xlim([0,70]);plt.ylim([40,80])
plt.title('19.2 GHz')
plt.grid()
plt.legend(loc='lower right')

## SET 1 ##
plt.figure(figsize=(9,7))
# load
dirScript = os.getcwd()
os.chdir(dirScript)
df = pd.read_excel(fileName + ".xlsx")
#reduce
df = df[(df["lens_enabled"] == 'l1e_l2e_l3e')]
df = df[(df["pa_phi_deg"] == 0)]
df = df[(df["cal_freq_GHz"] == 19.2)]
df = df[(df["freq_GHz"] == 19.2)]
df = df[(df["active_cal"] == 'S2000_RX_QR00003_LUT2dB_v3.tar')]
df = df[(df["beam_no"] == 1)]
df = df[(df["group_name"] == 'LUT_2dB_8pa')]
# plot1
dfPlot = df[(df["entry_type"] == 'gain_at_peak')]
thetaMeas = np.array(dfPlot['theta_deg'])
thetaAsk = np.array(dfPlot['pa_theta_deg'])
print(thetaMeas); print(thetaAsk)
for i in range(len(thetaMeas)):
     if np.abs(thetaMeas[i] - thetaAsk[i]) > abs(thetaMeas[i])*1.5:
        thetaMeas[i] = thetaMeas[i]*-1.0
print(thetaMeas); print(thetaAsk)
thetaDiff = thetaMeas-thetaAsk
phiMeas = np.array(dfPlot['phi_deg'])
phiAsk = np.array(dfPlot['pa_phi_deg'])
print(phiMeas); print(phiAsk)
for i in range(len(phiMeas)):
    if phiMeas[i] > 90:
        phiMeas[i] = phiMeas[i] - 180
    if np.array(dfPlot['pa_theta_deg'])[i] == 0:
        phiMeas[i] = -100
print(phiMeas); print(phiAsk)
phiDiff = (phiMeas-phiAsk)
x = dfPlot['pa_theta_deg']
y = thetaDiff
plt.plot(x,y,'ks',markersize=10,label='Theta deviation')
# plot2
x = dfPlot['pa_theta_deg']
y = phiDiff
plt.plot(x,y,'b^',markersize=10,label='Phi deviation')
# format
plt.xlabel('Theta [deg]'); plt.ylabel('Deviation [deg]')
plt.xlim([0,70]);plt.ylim([-20,20])
plt.title('19.2 GHz')
plt.grid()
plt.legend(loc='upper left')

## All lenses ##
plt.figure(figsize=(9,7))
# load
lensSetMap = ['l1e_l2d_l3d','l1d_l2e_l3d', 'l1d_l2d_l3e','l1e_l2e_l3e']
lensSetMapLabels = ['l1','l2','l3','TLM']
lensSetMapCols = ['r','g','b','m','o']
for lens_set in range(4):
    # load
    dirScript = os.getcwd()
    os.chdir(dirScript)
    df = pd.read_excel(fileName + ".xlsx")
    #reduce
    df = df[(df["lens_enabled"] == lensSetMap[lens_set])]
    df = df[(df["pa_phi_deg"] == 0)]
    df = df[(df["cal_freq_GHz"] == 19.2)]
    df = df[(df["freq_GHz"] == 19.2)]
    df = df[(df["active_cal"] == 'S2000_RX_QR00003_LUT2dB_v3.tar')]
    df = df[(df["beam_no"] == 1)]
    df = df[(df["beam_no"] == 1)]
    df = df[(df["group_name"] == 'LUT_2dB_8pa')]
    # plot1
    dfPlot = df[(df["entry_type"] == 'gain_at_peak')]
    x = dfPlot['pa_theta_deg']
    y = dfPlot['Gain_dB']
    plt.plot(x,y,(lensSetMapCols[lens_set]+'s'),markeredgecolor='k',markersize=10,label=lensSetMapLabels[lens_set]+': peak')
    # plot1
    dfPlot = df[(df["entry_type"] == 'gain_at_requested_angle')]
    x = dfPlot['pa_theta_deg']
    y = dfPlot['Gain_dB']
    plt.plot(x,y,(lensSetMapCols[lens_set]+'X'),markeredgecolor='k',markersize=10,label=lensSetMapLabels[lens_set]+': requested')
    # format
    plt.xlabel('Theta [deg]'); plt.ylabel('Gain [dB]')
    plt.xlim([0,70]);plt.ylim([0,100])
    plt.title('19.2 GHz')
    plt.grid('on',which='both')
    plt.legend(loc='upper center',ncol=4,fontsize=10)
