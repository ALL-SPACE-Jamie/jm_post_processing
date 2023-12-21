import pandas as pd
import numpy as np
import matplotlib.pyplot as plt;
plt.rcParams['font.size'] = 12
from scipy.stats import norm
import os
import glob
import copy
import csv
import json
import time
from pylab import *
colMap = ['r','g','b','k','m','c','r','g','b','k','m','c','r','g','b','k','m','c','r','g','b','k','m','c','r','g','b','k','m','c','r','g','b','k','m','c','r','g','b','k','m','c']

plt.close('all')

# file path
dirScript = os.getcwd()

# parmas
filePath = r'C:\Users\jmitchell\Downloads\tar_sample_meas'

# definitions
def find_measFiles(path, fileString):
    global measFiles, files
    files = []
    for root, directories, file in os.walk(path):
        for file in file:
            if (file.endswith(".csv")) == True:
                files.append(os.path.join(root, file))
    measFiles = []
    for i in range(len(files)):
        if fileString in files[i]  and 'rchive' not in files[i]:
            measFiles.append(files[i])

def plot_GainVsFreq(measFile):
    global df, freq, gain
    dfFull = pd.read_csv(measFile)
    df = dfFull.copy()

    # df
    print('\nLoaded df')
    df = df[(df["freq_GHz"] > 0.1)]; print('freq_GHz, len = ' + str(len(df)))
    df = df[(df["phi_deg"] == 0)]; print('phi_deg, len = ' + str(len(df)))
    df = df[(df["theta_deg"] == 0)]; print('theta_deg, len = ' + str(len(df)))
    df = df[(df["pol_angle_deg"] == 0)]; print('pol_angle_deg, len = ' + str(len(df)))
    # df = df[(df["active_cal"] == X)]; print('active_cal, len = ' + str(len(df)))
    # df = df[(df["acu_version"] == X)]; print('acu_version, len = ' + str(len(df)))
    # df = df[(df["combiners_common_setting"] == X)]; print('combiners_common_setting, len = ' + str(len(df)))
    # df = df[(df["comment"] == X)]; print('comment, len = ' + str(len(df)))
    # df = df[(df["datalogger_channels"] == X)]; print('datalogger_channels, len = ' + str(len(df)))
    # df = df[(df["datalogger_device"] == X)]; print('datalogger_device, len = ' + str(len(df)))
    # df = df[(df["datetime_start"] == X)]; print('datetime_start, len = ' + str(len(df)))
    # df = df[(df["datetime_stop"] == X)]; print('datetime_stop, len = ' + str(len(df)))
    # df = df[(df["er_id"] == X)]; print('er_id, len = ' + str(len(df)))
    # df = df[(df["ifbw_Hz"] == X)]; print('ifbw_Hz, len = ' + str(len(df)))
    # df = df[(df["itcc_runner_version"] == X)]; print('itcc_runner_version, len = ' + str(len(df)))
    # df = df[(df["phi_deg_offset"] == X)]; print('phi_deg_offset, len = ' + str(len(df)))
    # df = df[(df["pointing"] == X)]; print('pointing, len = ' + str(len(df)))
    # df = df[(df["pol_probe"] == X)]; print('pol_probe, len = ' + str(len(df)))
    # df = df[(df["port_sw"] == X)]; print('port_sw, len = ' + str(len(df)))
    # df = df[(df["primary_axis"] == X)]; print('primary_axis, len = ' + str(len(df)))
    # df = df[(df["run"] == X)]; print('run, len = ' + str(len(df)))
    # df = df[(df["setup_name"] == X)]; print('setup_name, len = ' + str(len(df)))
    # df = df[(df["source_power_dB"] == X)]; print('source_power_dB, len = ' + str(len(df)))
    # df = df[(df["temp_C"] == X)]; print('temp_C, len = ' + str(len(df)))
    # df = df[(df["theta_deg_offset"] == X)]; print('theta_deg_offset, len = ' + str(len(df)))
    # df = df[(df["vna_active_calset"] == X)]; print('vna_active_calset, len = ' + str(len(df)))
    # df = df[(df["vna_error_correction_S12"] == X)]; print('vna_error_correction_S12, len = ' + str(len(df)))
    # df = df[(df["vna_error_correction_S13"] == X)]; print('vna_error_correction_S13, len = ' + str(len(df)))
    # df = df[(df["vna_model"] == X)]; print('vna_model, len = ' + str(len(df)))
    # df = df[(df["vna_sweep_time_s"] == X)]; print('vna_sweep_time_s, len = ' + str(len(df)))
    # df = df[(df["fpath_hash"] == X)]; print('fpath_hash, len = ' + str(len(df)))
    # df = df[(df["fpath_name"] == X)]; print('fpath_name, len = ' + str(len(df)))
    # df = df[(df["fpath_parent"] == X)]; print('fpath_parent, len = ' + str(len(df)))
    # df = df[(df["cal_name"] == X)]; print('cal_name, len = ' + str(len(df)))
    # df = df[(df["losses"] == X)]; print('losses, len = ' + str(len(df)))
    # df = df[(df["port_name"] == X)]; print('port_name, len = ' + str(len(df)))
    # df = df[(df["measurement_type"] == X)]; print('measurement_type, len = ' + str(len(df)))
    # df = df[(df["datetime"] == X)]; print('datetime, len = ' + str(len(df)))
    # df = df[(df["meas_name"] == X)]; print('meas_name, len = ' + str(len(df)))
    df = df[(df["beam_no"] == 1)]; print('beam_no, len = ' + str(len(df)))
    # df = df[(df["pa_theta_deg"] == X)]; print('pa_theta_deg, len = ' + str(len(df)))
    # df = df[(df["pa_phi_deg"] == X)]; print('pa_phi_deg, len = ' + str(len(df)))
    df = df[(df["lens_enabled"] == 'l1e_l2e_l3e')]; print('lens_enabled, len = ' + str(len(df)))
    df = df[(df["cal_freq_GHz"] > 0.1)]; print('cal_freq_GHz, len = ' + str(len(df)))
    # df = df[(df["apply_calibration"] == X)]; print('apply_calibration, len = ' + str(len(df)))
    # df = df[(df["apply_phase_correction"] == X)]; print('apply_phase_correction, len = ' + str(len(df)))
    # df = df[(df["cal_method"] == X)]; print('cal_method, len = ' + str(len(df)))
    # df = df[(df["spherical_coordinate_system"] == X)]; print('spherical_coordinate_system, len = ' + str(len(df)))
    df = df[(df["pol"] == 'lhcp')]; print('pol, len = ' + str(len(df)))
    # df = df[(df["pol_basis"] == X)]; print('pol_basis, len = ' + str(len(df)))
    # df = df[(df["eField"] == X)]; print('eField, len = ' + str(len(df)))
    df = df[(df["Gain_dB"] > 0)]; print('Gain_dB, len = ' + str(len(df)))
    df = df[(df["phase_deg"] > 0)]; print('phase_deg, len = ' + str(len(df)))
    


    # params
    if len(df) > 0:
        freq = np.array(df['freq_GHz'])
        gain = np.array(df['Gain_dB'])
        plt.plot(freq, gain)

find_measFiles(filePath, 'LTR')
plt.figure()
for measFile in measFiles:
    plot_GainVsFreq(measFile)















keys = list(df.keys())
# for key in keys:
#     print('df = df[(df[\"' + key + '\"] == X)]; print(\'' + str(key) + ', len = \' + ' + 'str(len(df))' + ')')
