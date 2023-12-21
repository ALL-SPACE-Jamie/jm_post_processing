import pandas as pd
import numpy as np
import matplotlib.pyplot as plt; plt.rcParams['font.size'] = 15
import os
plt.close('all')

# load
fileName = r'C:\Users\jmitchell\Downloads\ppk_data'
dirScript = os.getcwd()
os.chdir(dirScript)
df = pd.read_excel(fileName + ".xlsx")
columns = df.columns.tolist()

# defs
def thetaphi_to_azel(theta, phi):
    theta = theta*np.pi/180.0
    phi = phi*np.pi/180.0
    
    sin_el = np.sin(phi) * np.sin(theta)
    tan_az = np.cos(phi) * np.tan(theta)
    el = np.arcsin(sin_el) * 180.0/np.pi
    az = np.arctan(tan_az) * 180.0/np.pi
     
    return az, el

# find columns that differ
def find_moving_keys(df):
    for key in list(df.keys()):
        col = df[key]
        col = list(dict.fromkeys(col))
        if len(col) > 1:
            print(key)
            
def reduce_df_theta_sweep(df, phi_angle, freq_meas, gain_type, freq_range):
    global df1, df2
    df = df[(df["pa_phi_deg"] == phi_angle)]
    df = df[(df["cal_freq_GHz"] == freq_meas)]
    df = df[(df["entry_type"] == gain_type)]
    df = df[(df["freq_GHz"] <= freq_meas+freq_range)]
    df = df[(df["freq_GHz"] >= freq_meas-freq_range)]
    
    find_moving_keys(df)
    
    return df

# plot gain
plt.figure(figsize=(10,5))
for freq_set in list(np.linspace(27.5, 31.0, 8)):
    df_f = reduce_df_theta_sweep(df, 0, freq_set, 'gain_at_peak', 0.25)
    
    freq = np.array(df_f['freq_GHz'])
    theta= np.array(df_f['pa_theta_deg'])
    gain = np.array(df_f['Gain_dB'])
    xdata = theta
    ydata = freq
    zdata = gain
    
    plt.tricontourf(xdata, ydata, zdata, levels=np.arange(20, 75.1, 0.1), cmap='jet')
    plt.plot(xdata, ydata, 'k.', alpha = 0.5)
    
cbar = plt.colorbar()
cbar.set_ticks(np.arange(20,80,5))
plt.xlabel('theta [deg]')
plt.ylabel('frequency [GHz]')
plt.title('Gain at Peak [dB]\n' + 'f_set = ' + str(freq_set) + ' GHz')
plt.xlim([0, 70]); plt.ylim([27.5, 31.0])
plt.tight_layout()
plt.show()

meas_freq_list = list(dict.fromkeys(df['freq_GHz']))[::5]

plt.savefig('Gain' + '.png')
    
# plot xpd
plt.figure(figsize=(10,5))
for freq_set in list(np.linspace(27.5, 31.0, 8)):
    df_f = reduce_df_theta_sweep(df, 0, freq_set, 'gain_at_peak', 0.25)
    
    freq = np.array(df_f['freq_GHz'])
    theta= np.array(df_f['pa_theta_deg'])
    gain = np.array(df_f['xpd_dB'])
    xdata = theta
    ydata = freq
    zdata = gain
    
    plt.tricontourf(xdata, ydata, zdata, levels=np.arange(5, 35.1, 0.1), cmap='jet')
    plt.plot(xdata, ydata, 'k.', alpha = 0.5)
cbar = plt.colorbar()
cbar.set_ticks(np.arange(5,40,5))
    
plt.xlabel('theta [deg]')
plt.ylabel('frequency [GHz]')
plt.title('XPD [dB]\n' + 'f_set = ' + str(freq_set) + ' GHz')
plt.xlim([0, 70]); plt.ylim([27.5, 31.0])
plt.tight_layout()
plt.show()

meas_freq_list = list(dict.fromkeys(df['freq_GHz']))[::5]

plt.savefig('XPD' + '.png')
    
# plot offset
plt.figure(figsize=(10,5))
for freq_set in list(np.linspace(27.5, 31.0, 8)):
    df_1 = reduce_df_theta_sweep(df, 0, freq_set, 'gain_at_peak', 0.25)
    freq = np.array(df_1['freq_GHz'])
    theta= np.array(df_1['pa_theta_deg'])
    gain1 = np.array(df_1['theta_deg'])
    
    df_2 = reduce_df_theta_sweep(df, 0, freq_set, 'gain_at_requested_angle', 0.25)
    gain2 = np.array(df_2['theta_deg'])
    
    xdata = theta
    ydata = freq
    zdata = gain1-gain2
    
    plt.tricontourf(xdata, ydata, zdata, levels=np.arange(-3, 3.1, 0.1), cmap='jet')
    plt.plot(xdata, ydata, 'k.', alpha = 0.5)
cbar = plt.colorbar()
cbar.set_ticks(np.arange(-3,3.5,0.5))    
    
plt.xlabel('theta [deg]')
plt.ylabel('frequency [GHz]')
plt.title('Theta offset [deg]\n' + 'f_set = ' + str(freq_set) + ' GHz')
plt.xlim([0, 70]); plt.ylim([27.5, 31.0])
plt.tight_layout()
plt.show()

meas_freq_list = list(dict.fromkeys(df['freq_GHz']))[::5]

plt.savefig('PointDiff' + '.png')