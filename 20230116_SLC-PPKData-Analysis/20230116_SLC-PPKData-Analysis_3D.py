import pandas as pd
import numpy as np
import matplotlib.pyplot as plt; plt.rcParams['font.size'] = 18
import os
plt.close('all')

# load
fileName = 'ppk_data_CCG36_PCG36'
dirScript = os.getcwd()
dirScript = r'G:\measurements\reports\Feb2023\slc3\Rx_Thermal\QR00038\Debug\Power_Mode2'
os.chdir(dirScript)
dfFull = pd.read_excel(fileName + ".xlsx")

## Defs ##

def thetaphi_to_azel(theta, phi):
    global az, el, tan_az
    
    theta = theta*np.pi/180.0
    phi = phi*np.pi/180.0
    
    sin_el = np.sin(phi) * np.sin(theta)
    tan_az = np.cos(phi) * np.tan(theta)
    el = np.arcsin(sin_el) * 180.0/np.pi
    az = np.arctan(tan_az) * 180.0/np.pi

def plot__gainVstheta(lensSet, phiAng, beamNo, freqMeas, RFICFreq, fileName, varPlot, ylims, makeFig, col1, col2, adLabel):
    global dfPlot
    if makeFig == True:
        plt.figure(figsize=(9,7))

    # load
    os.chdir(dirScript)
    df = pd.read_excel(fileName + ".xlsx")

    #reduce
    df = df[(df["lens_enabled"] == lensSet)]
    # df = df[(df["pa_phi_deg"] == phiAng)]
    df = df[(df["cal_freq_GHz"] == RFICFreq)]
    df = df[(df["freq_GHz"] == freqMeas)]
    # df = df[(df["active_cal"] == activeCal)]
    df = df[(df["beam_no"] == beamNo)]

    # plot1
    dfPlot = df[(df["entry_type"] == 'gain_at_peak')]
    x = dfPlot['pa_theta_deg']
    y = dfPlot[varPlot]
    plt.plot(x,y, col1+'s',markeredgecolor='k',markersize=10,label=adLabel + 'Peak')

    # plot2
    dfPlot = df[(df["entry_type"] == 'gain_at_requested_angle')]
    x = dfPlot['pa_theta_deg']
    y = dfPlot[varPlot]
    plt.plot(x,y, col2+'^',markeredgecolor='k',markersize=10,label=adLabel + 'Requested angle')

    # format
    plt.xlabel('Theta [deg]'); plt.ylabel(varPlot)
    plt.xlim([0,70]);plt.ylim(ylims)
    plt.title(str(freqMeas) + ' GHz')
    plt.grid('on')
    plt.legend(loc='lower right')
    
def plot__devVsTheta(lensSet, phiAng, beamNo, freqMeas, RFICFreq, fileName):
    plt.figure(figsize=(9,7))

    # load
    os.chdir(dirScript)
    df = pd.read_excel(fileName + ".xlsx")

    # reduce
    df = df[(df["lens_enabled"] == lensSet)]
    df = df[(df["pa_phi_deg"] == phiAng)]
    df = df[(df["cal_freq_GHz"] == RFICFreq)]
    df = df[(df["freq_GHz"] == freqMeas)]
    # df = df[(df["active_cal"] == activeCal)]
    df = df[(df["beam_no"] == beamNo)]
    dfPlot = df[(df["entry_type"] == 'gain_at_peak')]
    
    # theta / phi deviations
    thetaMeas = np.array(dfPlot['theta_deg'])
    thetaAsk = np.array(dfPlot['pa_theta_deg'])
    phiMeas = np.array(dfPlot['phi_deg'])
    phiAsk = np.array(dfPlot['pa_phi_deg'])
    
    # fix the flipped theta angle
    for i in range(len(thetaMeas)):
         if np.abs(thetaMeas[i] - thetaAsk[i]) > abs(thetaMeas[i])*1.5:
            thetaMeas[i] = thetaMeas[i]*-1.0
    thetaDiff = thetaMeas-thetaAsk
    
    # wrap
    for i in range(len(phiMeas)):
        if phiMeas[i] > 90:
            phiMeas[i] = phiMeas[i] - 180
    phiDiff = (phiMeas-phiAsk)
    
    # convert theta / phi to az / el
    thetaphi_to_azel(thetaMeas, phiMeas); azMeas = az*1.0; elMeas = el*1.0
    thetaphi_to_azel(thetaAsk, phiAsk); azAsk = az*1.0; elAsk = el*1.0

    # calculate differences
    azDiff = azMeas-azAsk
    elDiff = elMeas-elAsk

    # plot1
    x = dfPlot['pa_theta_deg']
    y = azDiff
    plt.plot(x,y,'ks',markeredgecolor='k',markersize=10,label='Azmuth deviation')
    
    # plot2
    x = dfPlot['pa_theta_deg']
    y = elDiff
    plt.plot(x,y,'b^',markeredgecolor='k',markersize=10,label='Elevation deviation')
    
    # format
    plt.xlabel('Theta [deg]'); plt.ylabel('Deviation [deg]')
    plt.xlim([0,70]);plt.ylim([-20,20])
    plt.title(str(freqMeas) + ' GHz')
    plt.grid()
    plt.legend(loc='upper left')
   
fileName = fileName
RFICFreq = 19.95
freqLog = [20.0]
freqMeas = freqLog[0] 
phiAng = 242.8
lensType = 'l1d_l2e_l3d'
plot__gainVstheta(lensType, 0.0, 1, freqMeas, RFICFreq, fileName, 'Gain_dB', [20,80], True, 'k', 'b', '')

phiLog = np.array(dfPlot['phi_deg'])
thetaLog = np.array(dfPlot['theta_deg'])
thetaphi_to_azel(thetaLog, phiLog)
gainLog = np.array(dfPlot['Gain_dB'])

x = thetaLog
y = phiLog
# x = el*np.cos(az)
# y = el*np.sin(az)
plt.figure(figsize=(12.5,10))
v = np.linspace(50, 80, 1001, endpoint=True)
cntr = plt.tricontourf(x, y, gainLog, v, cmap=plt.cm.jet)
cbar = plt.colorbar(cntr)
cbar.set_ticks(np.arange(50,85,5))
plt.xlim([-75,75]); plt.ylim(-75,75)

for i in range(len(x)):
    plt.plot(x[i],y[i],'ko')
    
plt.xlabel('az [deg]'); plt.ylabel('el [deg]')
plt.title('S$_{21}$ [dB], f_set = ' + str(RFICFreq) + ' GHz, f_meas = ' + str(freqMeas) + ' GHz, ' + lensType)
plt.show()
plt.tight_layout()