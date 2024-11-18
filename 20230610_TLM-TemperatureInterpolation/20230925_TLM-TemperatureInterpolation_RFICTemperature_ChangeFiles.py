import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import csv
import pickle
import warnings; warnings.filterwarnings("ignore", category=pd.errors.ParserWarning)
import scipy.stats as stats
import datetime

# definitions
def find_measFiles(filePath, fileString):
    files = []
    for root, directories, file in os.walk(filePath):
        for file in file:
            if (file.endswith(".csv")) == True:
                files.append(os.path.join(root, file))
    measFiles = []
    sizeLog = []
    for i in range(len(files)):
        if fileString in files[i]:
            if os.path.getsize(files[i]) > 1000:
                measFiles.append(files[i])
    return measFiles

def find_fileDetails(filePath):
    meas_params = {}
    meas_info = []

    # meas_info, array and measurement frequencies
    with open(filePath, 'r') as file:
        filecontent = csv.reader(file, delimiter=',')
        for row in filecontent:
            meas_info.append(row)
        index_start = [index for index in range(
            len(meas_info)) if 'barcodes' in meas_info[index]][0] + 2
        meas_info = meas_info[0:index_start]
        meas_array = np.genfromtxt(filePath, delimiter=',', skip_header=index_start)
        meas_array_gain = meas_array[:, ::2]
        meas_array_phase = meas_array[:, 1:][:, ::2]
        meas_frequencies = np.array(meas_info[index_start - 1])[::2].astype(float)

    # meas_params
    for i in range(len(meas_info) - 1):
        if len(meas_info[i]) > 1:
            paramName = meas_info[i][0]
            if paramName[0:2] == '# ':
                paramName = paramName[2:]
            meas_params[paramName] = meas_info[i][1]
            if meas_params[paramName][0] == ' ':
                meas_params[paramName] = meas_params[paramName][1:]
                
    return meas_params, meas_info,meas_array, meas_array_gain, meas_array_phase, meas_frequencies
                
def find_fileDetails_SEC(filePath):
    meas_params = {}
    meas_info = []

    # meas_info, array and measurement frequencies
    with open(filePath, 'r') as file:
        filecontent = csv.reader(file, delimiter=',')
        for row in filecontent:
            meas_info.append(row)
        index_start = [index for index in range(
            len(meas_info)) if 'barcodes' in meas_info[index]][0] + 2
        meas_info = meas_info[0:index_start]
        df_meas = pd.read_csv(filePath, skiprows=index_start-1, encoding='latin-1', index_col=False)
        meas_array = np.genfromtxt(filePath, delimiter=',', skip_header=index_start)[:,38:]
        meas_array_gain = meas_array[:, ::2]
        meas_array_phase = meas_array[:, 1:][:, ::2]
        meas_frequencies = np.array(meas_info[index_start - 1])[38:][::2].astype(float)

    # meas_params
    for i in range(len(meas_info) - 1):
        if len(meas_info[i]) > 1:
            paramName = meas_info[i][0]
            if paramName[0:2] == '# ':
                paramName = paramName[2:]
            meas_params[paramName] = meas_info[i][1]
            if meas_params[paramName][0] == ' ':
                meas_params[paramName] = meas_params[paramName][1:]
                
    # entry dict
    meas_params_sec = meas_params.copy()
    for meas_param in meas_params.keys():
        meas_params[meas_param] = list([meas_params[meas_param]])

    df_entry = pd.DataFrame(meas_params)
    df_entry.at[[0], 'ports'] = np.array2string(np.array(df_meas['port']), separator=',')[1:-1]
    df_entry.at[[0], 'lens'] = np.array2string(np.array(df_meas[' lens']), separator=',')[1:-1]
    df_entry.at[[0], 'rfic'] = np.array2string(np.array(df_meas[' rfic']), separator=',')[1:-1]
    df_entry.at[[0], 'channel'] = np.array2string(np.array(df_meas[' channel']), separator=',')[1:-1]
    df_entry.at[[0], 'rfic temperature'] = np.array2string(np.array(df_meas[' rfic temperature']), separator=',')[1:-1]
    df_entry.at[[0], 'combiner_temperature'] = np.array2string(np.array(df_meas[' combiner temperature']), separator=',')[1:-1]
    df_entry.at[[0], 'plate tem 1'] = np.array2string(np.array(df_meas[' plate tem 1']), separator=',')[1:-1]
    df_entry.at[[0], 'plate tem 2'] = np.array2string(np.array(df_meas[' plate tem 2']), separator=',')[1:-1]
    df_entry.at[[0], 'ambient temperature'] = np.array2string(np.array(df_meas[' ambient temperature']), separator=',')[1:-1]
    df_entry.at[[0], 'average rfic temperature'] = np.array2string(np.array(df_meas[' avg_rfic_tem']), separator=',')[1:-1]

    rfic_temperatures = np.array(df_meas[' rfic temperature']).copy()
    
    return rfic_temperatures, meas_params_sec

def phase_wrap(arr):
    arr[arr < 0.0] += 360.0
    arr[arr > 360.0] -= 360.0
    return arr


##### CODE #####

# working directory
file_path = r'C:\Users\jmitchell\OneDrive - ALL.SPACE\RF Testing\6 Investigations\20241005_P-Type_TermperatureInterpolation\TxTLM_00733'

# import pickle
with open(r'C:\Users\jmitchell\OneDrive - ALL.SPACE\RF Testing\6 Investigations\20241005_P-Type_TermperatureInterpolation\Gradient_Generation\2024-10-07_17-57-25_gradients.pkl', 'rb') as file:
    grads = pickle.load(file)
    
# import rfa files
rfa_files = find_measFiles(file_path + r'\rfa_files_for_interpolation', 'RFA')
# rfa_files = rfa_files[0:4]
sec_files = find_measFiles(file_path + r'\rfa_files_for_interpolation', 'SEC')

# open the rfas and create a list of sec files ordered in the same fashion
sec_files_ordered = {}
for rfa_file in rfa_files:
    meas_params, meas_info,meas_array, meas_array_gain, meas_array_phase, meas_frequencies = find_fileDetails(rfa_file)
    sec_files_for_comp = []
    for sec_file in sec_files:
        beam = meas_params['Beam']
        freq_set = meas_params['f_c']
        if 'QR'+meas_params['barcodes'] in sec_file and f'Beam{beam}' in sec_file:
            rfic_temperatures, meas_params_sec = find_fileDetails_SEC(sec_file)
            if float(meas_params['f_c']) == float(meas_params_sec['f_c']) and float(meas_params['Temp. [°C]']) == float(meas_params_sec['Temp. [°C]']):
                sec_files_for_comp.append(sec_file)
    if len(sec_files_for_comp) == 1:
        sec_files_ordered[rfa_file] = sec_files_for_comp[0]
    else:
        print('Number of SEC files that correspond to the RFA does not equal 1!')
        stop

# open the rfas and edit the tables to 45 degrees
for temperature in [25.0, 45.0, 65.0]:
    temperature_int = int(temperature)
    for rfa_file in rfa_files:
        meas_params, meas_info,meas_array, meas_array_gain, meas_array_phase, meas_frequencies = find_fileDetails(rfa_file)
        rfic_temperatures, meas_params_sec = find_fileDetails_SEC(sec_files_ordered[rfa_file])
        rfic_temperature_deltas = rfic_temperatures - temperature
        gain_deltas = rfic_temperature_deltas*grads[meas_params['lens type (rx/tx)'] + '_gain_beam' + meas_params['Beam']]['m_av']
        gain_deltas = np.tile(np.array(gain_deltas)[:, np.newaxis], meas_array_gain.shape[1])
        phase_deltas = rfic_temperature_deltas*grads[meas_params['lens type (rx/tx)'] + '_phase_beam' + meas_params['Beam']]['m_av']
        phase_deltas = np.tile(np.array(phase_deltas)[:, np.newaxis], meas_array_phase.shape[1])
        meas_array_gain_corrected = meas_array_gain - gain_deltas
        meas_array_gain_corrected[meas_array_gain_corrected < 0.0] = 0.0
        meas_array_phase_corrected = meas_array_phase + phase_deltas
        meas_array_phase_corrected_wrapped = phase_wrap(meas_array_phase_corrected.copy())
        meas_array_corrected = np.stack((meas_array_gain_corrected, meas_array_phase_corrected_wrapped), axis=2)
        meas_array_corrected = meas_array_corrected.reshape(meas_array.shape[0], meas_array.shape[1])
        meas_array_corrected_list = meas_info.copy()      
        temperature_index = [index for index in range(len(meas_array_corrected_list)) if 'Temp. [°C]' in meas_array_corrected_list[index]][0]
        meas_array_corrected_list[temperature_index][1] = str(temperature_int)
        for k in range(len(meas_array_corrected)):
            meas_array_corrected_list.append(list(meas_array_corrected[k, :]))
               
        # write new file
        file_path_save = file_path + r'\rfa_files_interpolated'
        if not os.path.exists(file_path_save):
            os.makedirs(file_path_save)   
        file_path_save_fname = file_path_save + '\\' + rfa_file.split('\\')[-1].replace('_45C_', f'_{temperature_int}C_interp_')
        file = open(file_path_save_fname, 'w+', newline='')
        with file:
            write = csv.writer(file)
            write.writerows(meas_array_corrected_list)

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    