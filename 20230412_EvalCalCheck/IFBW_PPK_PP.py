import pandas as pd
import numpy as np
import matplotlib.pyplot as plt; plt.rcParams['font.size'] = 15
import os
import seaborn as sns
import pip
plt.close('all')

# load
fileName = r'C:\Users\RyanFairclough\Downloads\1_20_15_ppk\Raw_Data\ppk_data1'
savePath=r'C:\Users\RyanFairclough\Downloads\1_20_15_ppk\Raw_Data'
Th_deg_list=[0.0, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0]
Ph_deg=0.0

TLM_Type='Rx'

if TLM_Type=='Rx':
    cal_freq_list = [19.2]#[17.7, 18.2, 18.7, 19.2, 19.7, 20.2, 20.7, 21.2]
    meas_freq_list = [19.2]#[17.7, 18.2, 18.7, 19.2, 19.7, 20.2, 20.7, 21.2]#[20.2, 20.7, 21.2]#
    ifbw_min= 500
    ifbw_max= 5000
    Theta_deg = 40
    f_min=17.2
    f_max=21.7
    y_min_scan=-5
    y_max_scan=90
    y_min_scan_xpd = 0
    y_max_scan_xpd = 30
elif TLM_Type=='Tx':
    cal_freq_list=[27.5, 28.0, 28.5, 29.0, 29.5, 30.0, 30.5, 31.0]
    meas_freq_list=[27.5, 28.0, 28.5, 29.0, 29.5, 30.0, 30.5, 31.0]
    f_min = 27.0
    f_max = 31.5
    y_min_scan =20
    y_max_scan =80
    y_min_scan_xpd = 0
    y_max_scan_xpd = 30

labelLog = ['QR00045_I-Type']#, 'QR00011_I-Type',
fpathLog = [r'C:\Users\ITAdmin\Documents\S2000\I-type\Rx_TLM_I-Type\1p20p15_SW_Test\1p20p15']

dirScript = os.getcwd()
os.chdir(dirScript)
dfFull = pd.read_excel(fileName + ".xlsx")
markerList=['s', 'o', '^', 'D', 'X', 'p', '*', 'H']
colourMap = [['b','orange','g','r','purple','brown','magenta','grey'],
             ['c', 'peru', 'darkgreen', 'darksalmon', 'plum', 'chocolate', 'hotpink', 'k'],
             ['cornflowerblue', 'tan', 'greenyellow', 'darkred', 'blueviolet', 'rosybrown', 'mediumvioletred', 'darkslategrey'],
             ['deepskyblue', 'gold', 'olivedrab', 'crimson', 'indigo', 'sienna', 'orchid', 'silver']]

def plot_gain_vs_IFBW (fpath, cal_freq, meas_freq):
    global dfPlot, df, x, y, columns, acu, xpd_theta, theta_mispoint, phi_offset

    # load
    dirScript = os.getcwd()
    os.chdir(dirScript)
    df = pd.read_excel(fileName + ".xlsx")
    columns = df.columns.tolist()

    #reduce

    df = df[(df["phi_deg"] == 0)]
    df = df[(df["cal_freq_GHz"] == cal_freq)]
    df = df[(df["freq_GHz"] == meas_freq)]
    df = df[(df["entry_type"] == 'gain_at_requested_angle')]
    df = df[(df["fpath_parent"] == fpath)]
    df = df[(df["theta_deg"] == 40)]
    df = df[(df["lens_enabled"] == 'l1e_l2e_l3e')]
    acu='1.20.15'#np.array(df['acu_version'])[0]
    print(acu)

    x = np.array(df['ifbw_Hz'])
    y = np.array(df['Gain_dB'])
    xpd_theta = np.array(df['xpd_dB'])
    theta_mispoint = np.array(df['theta_deg_offset'])
    phi_offset = np.array(df['phi_deg_offset'])
    print(y)


def plot_Xpol_Vs_IFBW (fpath, cal_freq, meas_freq, Th_deg):
    global dfPlot, df, x, y, columns, acu, xpd_theta

    dirScript = os.getcwd()
    os.chdir(dirScript)
    df = pd.read_excel(fileName + ".xlsx")
    columns = df.columns.tolist()

    df = df[(df["phi_deg"] == Ph_deg)]
    df = df[(df["theta_deg"] == Theta_deg)]
    df = df[(df["freq_GHz"] == df["cal_freq_GHz"])]
    df = df[(df["entry_type"] == 'gain_at_requested_angle')]
    df = df[(df["fpath_parent"] == fpath)]

    phi_meas_freq = np.array(df['pa_phi_deg'])
    print(phi_meas_freq)
    x = np.array(df['ifbw_Hz'])
    y = np.array(df['xpd_dB'])
    print(y)

def plot_mispoint_Vs_IFBW (fpath, cal_freq, meas_freq, Th_deg):
    global dfPlot, df, x, y, columns, acu, xpd_theta, theta_mispoint

    dirScript = os.getcwd()
    os.chdir(dirScript)
    df = pd.read_excel(fileName + ".xlsx")
    columns = df.columns.tolist()

    df = df[(df["phi_deg"] == Ph_deg)]
    df = df[(df["theta_deg"] == Th_deg)]
    df = df[(df["freq_GHz"] == df["cal_freq_GHz"])]
    df = df[(df["entry_type"] == 'gain_at_requested_angle')]
    df = df[(df["fpath_parent"] == fpath)]


    x = np.array(df['ifbw_Hz'])

    print('xxxx',y)


for k in range(len(cal_freq_list)):
    plt.figure(figsize=([7, 6]))

    for i in range(len(fpathLog)):

        fpath = fpathLog[i]
        plot_gain_vs_IFBW(fpath, cal_freq_list[k], meas_freq_list[k])
        #df = pd.DataFrame(data={'Gain': y, 'IFBW': x})
        #box_plot = sns.boxplot(x=x, y=y, data=df, showfliers=False, width=0.2, whis=2)
        plt.plot(x, y, markerList[i], markerfacecolor= colourMap[0][i], markeredgecolor='k', markersize=10, label='Gain ' + labelLog[i])
        plt.plot(x, y - xpd_theta, markerList[i], markerfacecolor=colourMap[2][i], markeredgecolor='k', markersize=10, label='XP ' + labelLog[i])
        plt.plot(x, theta_mispoint, markerList[i], markerfacecolor=colourMap[3][i], markeredgecolor='k', markersize=10, label='theta_mispoint ' + labelLog[i])
        axhline_red = plt.axhline(y=y[0], color="red", linestyle='--', label='Reference Gain')
        axhline_blue = plt.axhline(y=y[0] - xpd_theta[0], color="blue", linestyle='--', label='Reference Gain - XP')
        axhline_green = plt.axhline(y=theta_mispoint, color="green", linestyle='--', label='Theta_mispoint')
        plt.text(x, theta_mispoint+3, theta_mispoint, fontsize =10)
        plt.text(x, y +3, y, fontsize =10)
        plt.text(x, y-xpd_theta + 3, y-xpd_theta, fontsize = 10)
        plt.xlabel('IFBW [Hz]', fontsize=10);
        plt.ylabel('Gain [dB]', fontsize=10)
        plt.yticks(np.linspace(0, 100, num=21), fontsize=10)
        plt.xticks(np.linspace(500, 5000, num=10), fontsize=7)
        plt.xlim([ifbw_min, ifbw_max])
        plt.ylim([y_min_scan, y_max_scan]);  # plt.ylim([65, 75])
        plt.grid('on')
        plt.legend(loc='lower center', fontsize=10)
        handles, labels = plt.gca().get_legend_handles_labels()
        handles.extend([axhline_red, axhline_blue])
        plt.legend(handles, labels, loc='lower center', fontsize=10)
        plt.title('LHCP Gain & Xpol vs IFBW'+'\nSW: ' + acu ,fontsize=15)
        plt.tight_layout()
        plt.savefig(savePath + '\\' + 'Gain_XP_Pointing_angle_Phi_' + str(Ph_deg) + 'Freq_' + str(meas_freq_list[k]) + 'GHz.png',dpi=400)
    plt.close('all')

#for p in range(len(cal_freq_list)):
    #plt.figure(figsize=([7, 6]))

    #for p in range(len(fpathLog)):

        #fpath = fpathLog[i]
        #plot_Xpol_Vs_IFBW(fpath, cal_freq_list[k], meas_freq_list[k], Th_deg_list[k])
        #plt.plot(x, y, markerList[i], markerfacecolor= colourMap[0][i], markeredgecolor='k', markersize=10, label='Gain ' + labelLog[i])
        #plt.xlabel('IFBW [Hz]', fontsize =10)
        #plt.ylabel('Xpol', fontsize =10)
        #plt.yticks(np.linspace(0, 100, num =21), fontsize =10)
        #plt.xlim([ifbw_min,ifbw_max])
        #plt.ylim([0, 40]);  # plt.ylim([65, 75])
        #plt.grid('on')
        #plt.legend(loc='lower left', fontsize=10)
        #plt.title('Xpol vs IFBW'+'\nSW: ' + acu ,fontsize=15)
        #plt.tight_layout()
        #plt.savefig(savePath + '\\' + 'Gain_XP_Pointing_angle_Phi_' + str(Ph_deg) + 'Freq_' + str(meas_freq_list[k]) + 'GHz.png',dpi=400)
    #plt.close('all')


