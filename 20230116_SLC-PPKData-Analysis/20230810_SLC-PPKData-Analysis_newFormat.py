import pandas as pd
import numpy as np
import matplotlib.pyplot as plt; plt.rcParams['font.size'] = 15
import os
plt.close('all')

# load
fileName = 'C:\Scratch\MuliBeam_Data\Tx\pkk_gain_analysis_1p17p5'
# fileName = 'C:\Scratch\MuliBeam_Data\Tx\pkk_gain_analysis_1p17p7'
# fileName = r'C:\Scratch\MuliBeam_Data\Rx\1p17p5\pkk_gain_analysis'
# fileName = r'C:\Scratch\MuliBeam_Data\Rx\1p17p67\pkk_gain_analysis'

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

def plot__gainVstheta(sb_mute, b1_theta, b1_phi, acu, freq, b2_phi):
    global dfPlot, df, x, y, columns

    # load
    dirScript = os.getcwd()
    os.chdir(dirScript)
    df = pd.read_excel(fileName + ".xlsx")
    columns = df.columns.tolist()

    #reduce
    df = df[(df["pb_theta_deg"] == b1_theta)]
    df = df[(df["pb_phi_deg"] == b1_phi)]
    df = df[(df["sb_mute"] == sb_mute)]
    df = df[(df["acu_version"] == acu)]
    df = df[(df["freq_GHz"] == freq)]
    df = df[(df["sb_phi_deg"] == b2_phi)]
    
    
    x = np.array(df['sb_theta_deg'])
    y = np.array(df['Gain_dB'])

sb_mute = 'ON'
labelLog = ['Beam 2 OFF', 'Beam 2 ON']
acu = '1.17.5'
# acu = '1.17.67'
freq = 19.5
freq = 29.5
b1_theta = 0.0
b1_phi = 0.0
b2_phi = 0.0
plt.figure(figsize=([7,6]))
for i in range(2):
    plot__gainVstheta(sb_mute, b1_theta, b1_phi, acu, freq, b2_phi)
    plt.plot(x[::4], y[::4], 's', markeredgecolor='k', markersize=10, label = labelLog[i])
    
    plt.xlabel('Theta [deg]'); plt.ylabel('Beam 1 gain [dB]\n(at req. angle)')
    plt.yticks(np.linspace(0,100,num=101))
    plt.xticks(np.linspace(-100,100,num=21))
    plt.xlim([-10,80]); plt.ylim([35,45]);# plt.ylim([65, 75])
    plt.grid('on')
    plt.legend(loc='upper left')
    plt.title('SW: ' + acu + '\nFreq = ' + str(freq) + ' GHz' + '\nb1: Th=' + str(b1_theta) + ', Phi=' + str(b1_phi) + '\nb2: Th=' + 'X' + ', Phi=' + str(b2_phi), fontsize=15)
    plt.tight_layout()
    plt.savefig('C:\Scratch\MuliBeam_Data\Tx\\' + acu.replace(".", "p"), dpi=400)
    
    
    sb_mute = 'OFF'
    
