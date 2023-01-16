import pandas as pd
import numpy as np
import matplotlib.pyplot as plt; plt.rcParams['font.size'] = 18
import os
plt.close('all')

# load
fileName = '20230109_Rx-CRcal_ppk_data'
dirScript = os.getcwd()
os.chdir(dirScript)
dfFull = pd.read_excel(fileName + ".xlsx")

## Defs ##

def thetaphi_to_azel(theta, phi):
    global az, el
    
    theta = theta*np.pi/180.0
    phi = phi*np.pi/180.0
    
    sin_el = np.sin(phi) * np.sin(theta)
    tan_az = np.cos(phi) * np.tan(theta)
    el = np.arcsin(sin_el) * 180.0/np.pi
    az = np.arctan(tan_az) * 180.0/np.pi
     
    return az

def plot__gainVstheta(lensSet, phiAng, activeCal, beamNo, freqMeas, RFICFreq, fileName, varPlot, ylims, makeFig, col1, col2, adLabel):
    if makeFig == True:
        plt.figure(figsize=(9,7))

    # load
    dirScript = os.getcwd()
    os.chdir(dirScript)
    df = pd.read_excel(fileName + ".xlsx")

    #reduce
    df = df[(df["lens_enabled"] == lensSet)]
    df = df[(df["pa_phi_deg"] == phiAng)]
    df = df[(df["cal_freq_GHz"] == RFICFreq)]
    df = df[(df["freq_GHz"] == freqMeas)]
    df = df[(df["active_cal"] == activeCal)]
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
    
def plot__devVsTheta(lensSet, phiAng, activeCal, beamNo, freqMeas, RFICFreq, fileName):
    plt.figure(figsize=(9,7))

    # load
    dirScript = os.getcwd()
    os.chdir(dirScript)
    df = pd.read_excel(fileName + ".xlsx")

    # reduce
    df = df[(df["lens_enabled"] == lensSet)]
    df = df[(df["pa_phi_deg"] == phiAng)]
    df = df[(df["cal_freq_GHz"] == RFICFreq)]
    df = df[(df["freq_GHz"] == freqMeas)]
    df = df[(df["active_cal"] == activeCal)]
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
    
## Run
# Params
calSet = 'S2000_Rx_TLM_QR00003_CalRig_v1.tar'
fileName = fileName
RFICFreq = 19.2
# run
freqLog = [19.2]
for i in range(len(freqLog)):
    freqMeas = freqLog[i]    
    # Gain
    plot__gainVstheta('l1e_l2e_l3e', 0, calSet, 1, freqMeas, RFICFreq, fileName, 'Gain_dB', [20,80], True, 'k', 'b', '')
    plt.savefig('./figures/gainVstheta' + '_freqMeas=' + str(freqMeas) + 'GHz' + '_freqRFIC=' + str(RFICFreq) + 'GHz' + '.png')
    # XPD
    plot__gainVstheta('l1e_l2e_l3e', 0, calSet, 1, freqMeas, RFICFreq, fileName, 'xpd_dB', [0,30], True, 'k', 'b', '')
    plt.savefig('./figures/xpdVstheta' + '_freqMeas=' + str(freqMeas) + 'GHz' + '_freqRFIC=' + str(RFICFreq) + 'GHz' + '.png')
    
    # Angle deviation
    plot__devVsTheta('l1e_l2e_l3e', 0, calSet, 1, freqMeas, RFICFreq, fileName)
    plt.savefig('./figures/devVstheta' + '_freqMeas=' + str(freqMeas) + 'GHz' + '_freqRFIC=' + str(RFICFreq) + 'GHz' + '.png')
    
    # Gain for all lenses
    plt.figure(figsize=(9,7))
    plot__gainVstheta('l1e_l2d_l3d', 0, calSet, 1, freqMeas, RFICFreq, fileName, 'Gain_dB', [20,80], False, 'r', 'r', 'l1 ')
    plot__gainVstheta('l1d_l2e_l3d', 0, calSet, 1, freqMeas, RFICFreq, fileName, 'Gain_dB', [20,80], False, 'g', 'g', 'l2 ')
    plot__gainVstheta('l1d_l2d_l3e', 0, calSet, 1, freqMeas, RFICFreq, fileName, 'Gain_dB', [20,80], False, 'b', 'b', 'l3 ')
    plot__gainVstheta('l1e_l2e_l3e', 0, calSet, 1, freqMeas, RFICFreq, fileName, 'Gain_dB', [20,80], False, 'm', 'm', 'TLM ')
    plt.legend(ncol=2, fontsize=10)
    plt.savefig('./figures/gainVsthetaAllLenses' + '_freqMeas=' + str(freqMeas) + 'GHz' + '_freqRFIC=' + str(RFICFreq) + 'GHz' + '.png')
