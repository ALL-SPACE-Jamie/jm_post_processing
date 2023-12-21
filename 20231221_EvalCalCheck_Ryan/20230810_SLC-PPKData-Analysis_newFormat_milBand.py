import pandas as pd
import numpy as np
import matplotlib.pyplot as plt; plt.rcParams['font.size'] = 15
import os
import pip
plt.close('all')

# load
fileName = r'C:/Users/RyanFairclough/Downloads/ppk_data1/ppk_data'
Th_deg=50.0
Ph_deg=0.0
cal_freq=21.2
meas_freq=21.2

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

def plot__gainVstheta(sb_mute, b1_theta, b1_phi, acu, freq, b2_phi, fpath):
    global dfPlot, df, x, y, columns

    # load
    dirScript = os.getcwd()
    os.chdir(dirScript)
    df = pd.read_excel(fileName + ".xlsx")
    columns = df.columns.tolist()

    #reduce
    # df = df[(df["pb_theta_deg"] == b1_theta)]
    df = df[(df["phi_deg"] == 0.0)]
    # df = df[(df["sb_mute"] == sb_mute)]
    df = df[(df["cal_freq_GHz"] == cal_freq)]
    df = df[(df["freq_GHz"] == meas_freq)]
    df = df[(df["entry_type"] == 'gain_at_requested_angle')]
    df = df[(df["fpath_parent"] == fpath)]
    
    
    x = np.array(df['theta_deg'])
    y = np.array(df['Gain_dB'])

sb_mute = 'ON'
labelLog = ['Cal_0dB_1sig_BA_0dB', 'Cal_0dB_2sig_BA_0dB', 'Cal_3dB_1sig_BA_0dB', 'Cal_3dB_2sig_BA_0dB', 'Cal_m3dB_1sig_BA_0dB', 'Cal_m3dB_2sig_BA_0dB']
acu = '1.17.7'
# acu = '1.17.67'
freq = 19.5
freq = 29.5
b1_theta = 0.0
b1_phi = 0.0
b2_phi = 0.0
plt.figure(figsize=([7,6]))
fpathLog = [r'/mnt/nfs/data/groups/measurements/slc3/S2000/DVT/S-Type/RX_TLM-ES2c/QR440-0254-00045/Single_Beam/RHCP/B2/20230812/Cal_0dB_1sig_BA_0dB', r'/mnt/nfs/data/groups/measurements/slc3/S2000/DVT/S-Type/RX_TLM-ES2c/QR440-0254-00045/Single_Beam/RHCP/B2/20230812/Cal_0dB_2sig_BA_0dB', r'/mnt/nfs/data/groups/measurements/slc3/S2000/DVT/S-Type/RX_TLM-ES2c/QR440-0254-00045/Single_Beam/RHCP/B2/20230812/Cal_3dB_1sig_BA_0dB', r'/mnt/nfs/data/groups/measurements/slc3/S2000/DVT/S-Type/RX_TLM-ES2c/QR440-0254-00045/Single_Beam/RHCP/B2/20230812/Cal_3dB_2sig_BA_0dB', r'/mnt/nfs/data/groups/measurements/slc3/S2000/DVT/S-Type/RX_TLM-ES2c/QR440-0254-00045/Single_Beam/RHCP/B2/20230812/Cal_m3dB_1sig_BA_0dB', r'/mnt/nfs/data/groups/measurements/slc3/S2000/DVT/S-Type/RX_TLM-ES2c/QR440-0254-00045/Single_Beam/RHCP/B2/20230812/Cal_m3dB_2sig_BA_0dB' ]
for i in range(len(fpathLog)):
    fpath = fpathLog[i]
    plot__gainVstheta(sb_mute, b1_theta, b1_phi, acu, freq, b2_phi, fpath)
    plt.plot(x, y, 's', markeredgecolor='k', markersize=10, label = labelLog[i])
    plt.xlabel('Theta [deg]'); plt.ylabel('Beam 1 gain [dB]\n(at req. angle)')
    plt.yticks(np.linspace(0,100,num=51))
    plt.xticks(np.linspace(-100,100,num=21))
    plt.xlim([-10,80]); plt.ylim([30,60]);# plt.ylim([65, 75])
    plt.grid('on')
    plt.legend(loc='lower left')
    plt.title('SW: ' + acu + '\nFreq = ' + str(meas_freq) + ' GHz' + '\nb1: Th=' + 'X' + ', Phi=' + str(Ph_deg), fontsize=15)
    plt.tight_layout()
    plt.savefig(r'C:\Users\RyanFairclough\Downloads\ppk_data1'+'\\' + 'Pointing_angle', dpi=400)
    
    
    sb_mute = 'OFF'
    
    
    



def plot__gainVstheta(sb_mute, b1_theta, b1_phi, acu, freq, b2_phi, fpath):
    global dfPlot, df, x, y, columns

    # load
    dirScript = os.getcwd()
    os.chdir(dirScript)
    df = pd.read_excel(fileName + ".xlsx")
    columns = df.columns.tolist()

    #reduce
    # df = df[(df["pb_theta_deg"] == b1_theta)]
    df = df[(df["phi_deg"] == Ph_deg)]
    # df = df[(df["sb_mute"] == sb_mute)]
    df = df[(df["theta_deg"] == Th_deg)]
    df = df[(df["freq_GHz"] == df["cal_freq_GHz"])]
    df = df[(df["entry_type"] == 'gain_at_requested_angle')]
    df = df[(df["fpath_parent"] == fpath)]
    
    
    x = np.array(df['freq_GHz'])
    y = np.array(df['Gain_dB'])

sb_mute = 'ON'
labelLog = ['Cal_0dB_1sig_BA_0dB', 'Cal_0dB_2sig_BA_0dB', 'Cal_3dB_1sig_BA_0dB', 'Cal_3dB_2sig_BA_0dB', 'Cal_m3dB_1sig_BA_0dB', 'Cal_m3dB_2sig_BA_0dB']
acu = '1.17.7'
# acu = '1.17.67'
freq = 19.5
freq = 29.5
b1_theta = 0.0
b1_phi = 0.0
b2_phi = 0.0
plt.figure(figsize=([7,6]))
fpathLog = [r'/mnt/nfs/data/groups/measurements/slc3/S2000/DVT/S-Type/RX_TLM-ES2c/QR440-0254-00045/Single_Beam/RHCP/B2/20230812/Cal_0dB_1sig_BA_0dB', r'/mnt/nfs/data/groups/measurements/slc3/S2000/DVT/S-Type/RX_TLM-ES2c/QR440-0254-00045/Single_Beam/RHCP/B2/20230812/Cal_0dB_2sig_BA_0dB', r'/mnt/nfs/data/groups/measurements/slc3/S2000/DVT/S-Type/RX_TLM-ES2c/QR440-0254-00045/Single_Beam/RHCP/B2/20230812/Cal_3dB_1sig_BA_0dB', r'/mnt/nfs/data/groups/measurements/slc3/S2000/DVT/S-Type/RX_TLM-ES2c/QR440-0254-00045/Single_Beam/RHCP/B2/20230812/Cal_3dB_2sig_BA_0dB', r'/mnt/nfs/data/groups/measurements/slc3/S2000/DVT/S-Type/RX_TLM-ES2c/QR440-0254-00045/Single_Beam/RHCP/B2/20230812/Cal_m3dB_1sig_BA_0dB', r'/mnt/nfs/data/groups/measurements/slc3/S2000/DVT/S-Type/RX_TLM-ES2c/QR440-0254-00045/Single_Beam/RHCP/B2/20230812/Cal_m3dB_2sig_BA_0dB' ]
for i in range(len(fpathLog)):
    fpath = fpathLog[i]
    plot__gainVstheta(sb_mute, b1_theta, b1_phi, acu, freq, b2_phi, fpath)
    plt.plot(x, y, 's', markeredgecolor='k', markersize=10, label = labelLog[i])
    plt.xlabel('freq [GHz]'); plt.ylabel('Beam 1 gain [dB]\n(at req. angle)')
    plt.yticks(np.linspace(0,100,num=21))
    #plt.xticks(np.linspace(-100,100,num=21))
    plt.xlim([20.0,21.5]); plt.ylim([30,80]);# plt.ylim([65, 75])
    plt.grid('on')
    plt.legend(loc='lower left')
    plt.title('SW: ' + acu + '\nFreq = ' + ' X' + '\nb2: Th=' + str(Th_deg) + ', Phi=' + str(Ph_deg), fontsize=15)
    plt.tight_layout()
    plt.savefig(r'C:\Users\RyanFairclough\Downloads\ppk_data1' + 'Frequency_comparison', dpi=400)
    
    
    sb_mute = 'OFF'
    
