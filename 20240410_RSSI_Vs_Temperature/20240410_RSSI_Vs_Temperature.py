# -*- coding: utf-8 -*-
"""
Created on Mon Dec 18 16:40:42 2023

@author: jmitchell
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt;
plt.rcParams['font.size'] = 12
import matplotlib.backends.backend_pdf
from matplotlib import cm, colors
from scipy.stats import norm
import os
import glob
import copy
import csv
import json
import time
from pylab import *
import seaborn as sns
from matplotlib.markers import MarkerStyle
from datetime import datetime, time
import scipy.interpolate as interp
plt.close('all')

        
def rssi_vs_temperature(file_path_temperature, file_path_rssi, label):  
    # global rssi, temperature_average_interp
    file_path =file_path_temperature 
    temperature_data = pd.read_csv(file_path).replace(r' °C', '', regex=True)
    temperature_time = temperature_data['Time']
    time_format = '%Y-%m-%d %H:%M:%S'
    temperature_time = [datetime.strptime(time_str, time_format) for time_str in temperature_time]
    temperature_values = np.array(temperature_data)[:,1:].astype(float)
    temperature_average = list(np.nanmedian(temperature_values[:,0:6], axis=1))
    
    file_path = file_path_rssi
    rssi_data = pd.read_csv(file_path)
    rssi = list(rssi_data['RSSI-BEAM1-50ms'])[int(len(rssi_data)/5):][::1000] # PLAYING WITH THIS
    rssi_time = list(rssi_data['Time'])[int(len(rssi_data)/5):][::1000] # PLAYING WITH THIS
    rssi_time = [datetime.strptime(time_str, time_format) for time_str in rssi_time]
    
    temperature_average_interp = list(np.array(rssi)*0.0)
    for idx in range(len(rssi_time)):
        rssi_time_val = rssi_time[idx]
        new_time_array = temperature_time.copy()
        for j in range(len(new_time_array)):
            new_time_array[j] = abs(new_time_array[j] - rssi_time_val)
        loc = np.argmin(new_time_array); print(loc)
        temperature_average_interp[idx] = temperature_average[loc]
    
    return temperature_average_interp, rssi
    
    
    
plt.figure()
temperature_init, rssi_init = rssi_vs_temperature(r'C:\Scratch\20240410\Temprature -Terminal IP--_172.16.8.250-data-as-joinbyfield-2024-04-10 15_53_54.csv', 
                          r'C:\Scratch\20240410\RSSI with 50ms--Terminal IP--_172.16.8.250-data-2024-04-10 15_46_47.csv', 
                          'init')
temperature_corrected, rssi_corrected = rssi_vs_temperature(r'C:\Scratch\20240410\Temprature -Terminal IP--_172.16.8.250-data-as-joinbyfield-2024-04-10 15_51_59.csv', 
                          r'C:\Scratch\20240410\RSSI with 50ms--Terminal IP--_172.16.8.250-data-2024-04-10 15_49_48.csv', 
                          'compensated')

plt.figure(figsize=(7,4))
# init
locs =(np.nonzero(np.array(rssi_init) > 4))
rssi_init = np.array(rssi_init)[locs]
temperature_init = np.array(temperature_init)[locs]
plt.plot(temperature_init, rssi_init, 'o', label='init')
plt.plot(np.unique(temperature_init), np.poly1d(np.polyfit(temperature_init, rssi_init, 2))(np.unique(temperature_init)))
# corrected
locs =(np.nonzero(np.array(rssi_corrected) > 4))
rssi_corrected = np.array(rssi_corrected)[locs]
temperature_corrected = np.array(temperature_corrected)[locs]
plt.plot(temperature_corrected, rssi_corrected, 'o', label='corrected')
plt.plot(np.unique(temperature_corrected), np.poly1d(np.polyfit(temperature_corrected, rssi_corrected, 2))(np.unique(temperature_corrected)))
# format
plt.xlim([35,75])
plt.ylim([0,15])
plt.xlabel('temperature [degC]')
plt.ylabel('rssi')
plt.grid('on')
plt.legend()
plt.savefig('rssi_vs_temperature_inwork.pdf')

# gradients
plt.figure(figsize=(7,4))
y_init = np.poly1d(np.polyfit(temperature_init, rssi_init, 2))(np.unique(temperature_init))
val_at_55_init = y_init[np.argmin((np.unique(temperature_init)-55)**2)]
plt.plot(np.unique(temperature_init), y_init-val_at_55_init, label='init')

y_corrected = np.poly1d(np.polyfit(temperature_corrected, rssi_corrected, 2))(np.unique(temperature_corrected))
val_at_55_corrected = y_corrected[np.argmin((np.unique(temperature_corrected)-55)**2)]
plt.plot(np.unique(temperature_corrected), y_corrected-val_at_55_corrected, label='corrected')

plt.xlim([35,75])
plt.ylim([-5,5])
plt.xlabel('temperature [degC]')
plt.ylabel('rssi gradient normalised to 55 degrees')
plt.grid('on')
plt.legend()
plt.savefig('rssi_vs_temperature_inwork_normalised_trends.pdf')