# -*- coding: utf-8 -*-
"""
Created on Fri Feb 27 18:50:16 2026

@author: jmitchell
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt; plt.close('all')

# parameters
freq = 27.5
beam = 1
array_start = 4
second_df = False
df_path = r"C:\scratch\20260408\gain_table.csv"
df2_path = r"C:\scratch\20260227\Sanmina-Gen2\dataframes\gain_table.csv"

# load df
df = pd.read_csv(df_path)
if second_df:
    df2 = pd.read_csv(df2_path)
    df = pd.concat([df, df2], axis=0, ignore_index=True)
df_sorted = df.iloc[0:0]
df_sorted.insert(4, 'dists',  [])
df_sorted.insert(5, 'rank',  [])
df_sorted.insert(6, 'furthest',  [])    
    
# create dictionary of stats
stats = {}

# compute ranks
for beam in [1,2]:
    stats[f'beam{beam}'] = {}
    for freq in np.linspace(27.5, 31.0, num=8):
        stats[f'beam{beam}'][f'freq{freq}'] = {}
        
        # trim for set point
        df_beam = df[df['beam']==beam]
        df_beam_freq = df_beam[np.isclose(df_beam['frequency'], freq)]
        df_beam_freq = df_beam_freq.drop_duplicates(subset='qr', keep='last')
        gain_array = df_beam_freq.iloc[:, array_start:].to_numpy()
        gain_av = np.median(gain_array, axis=0)
        gain_std = np.std(gain_array, axis=0)
        stats[f'beam{beam}'][f'freq{freq}']['av'] = gain_av
        stats[f'beam{beam}'][f'freq{freq}']['std'] = gain_std
        
        # compute distances (Euclidean)
        dists = np.linalg.norm(gain_array - gain_av, axis=1)
        order = np.argsort(dists)
        rank_idx = np.empty_like(order)
        rank_idx[order] = np.arange(len(order))
        port_deltas_upper = (gain_av+3*gain_std) - gain_array
        port_deltas_lower = gain_array - (gain_av-3*gain_std)
        port_delta_furthest = np.minimum(port_deltas_lower, port_deltas_upper)
        port_delta_furthest = np.min(port_delta_furthest, axis=1)
        
        # add dists
        df_beam_freq['dists'] = dists
        cols = list(df_beam_freq.columns)
        cols.insert(array_start, cols.pop(cols.index('dists')))
        df_beam_freq = df_beam_freq[cols]
        
        # add rank
        df_beam_freq['rank'] = rank_idx
        cols = list(df_beam_freq.columns)
        cols.insert(array_start+1, cols.pop(cols.index('rank')))
        df_beam_freq = df_beam_freq[cols]
        
        # add furthest
        df_beam_freq['furthest'] = port_delta_furthest
        cols = list(df_beam_freq.columns)
        cols.insert(array_start+2, cols.pop(cols.index('furthest')))
        df_beam_freq = df_beam_freq[cols]
        
        # array of gains
        gain_array_sorted = df_beam_freq.iloc[:, array_start+3:].to_numpy()

        # output df
        df_sorted = pd.concat([df_sorted, df_beam_freq], axis=0, ignore_index=True)

# # remove dodgy boards
# for idx in range(len(df_sorted)):
#     if df_sorted.iloc[idx]['furthest'] < 0.0:
#         df_sorted.loc[df_sorted.index[idx], 'rank'] += 1.0e12

# average ranks and establish order
mean_ranks = df_sorted.groupby('qr')['rank'].mean()
mean_ranks = mean_ranks.sort_values(ascending=True)
qr_order = mean_ranks.index.tolist()
if second_df:
    qr_second = list(dict.fromkeys((list(df2['qr']))))
    qr_second = [qr for qr in qr_order if qr in qr_second]

# plot tlms
fig, axs = plt.subplots(nrows=2, ncols=8, figsize=(40, 15))
fig.subplots_adjust(hspace=0.3)
devs = {}
devs[f'beam{beam}'] = {}
for beam in [1,2]:
    beam_index = beam-1
    freq_col = 0
    devs[f'beam{beam}'] = {}
    for freq in np.linspace(27.5, 31.0, num=8):
        devs[f'beam{beam}'][f'freq{freq}'] = []
        for qr in qr_order:
        # for qr in qr_second[-20:]: #####
            df_sorted_qr = df_sorted[df_sorted['qr']==qr]
            df_sorted_qr_beam = df_sorted_qr[df_sorted_qr['beam']==beam]
            df_sorted_qr_beam_freq = df_sorted_qr_beam[df_sorted_qr_beam['frequency']==freq]
            gain_array = df_sorted_qr_beam_freq.iloc[:, array_start+3:].to_numpy()
            devs[f'beam{beam}'][f'freq{freq}'].append(np.linalg.norm(gain_array[0,:] - np.array(stats[f'beam{beam}'][f'freq{freq}']['av'])))
            axs[beam_index, freq_col].plot(gain_array[0,:], 'ko-', alpha=0.2)
        ports = np.linspace(1, len(gain_av), num=len(gain_av))
        axs[beam_index, freq_col].plot(ports, stats[f'beam{beam}'][f'freq{freq}']['av'], 'r-')
        axs[beam_index, freq_col].plot(ports, stats[f'beam{beam}'][f'freq{freq}']['av']+3*stats[f'beam{beam}'][f'freq{freq}']['std'], 'b-')
        axs[beam_index, freq_col].plot(ports, stats[f'beam{beam}'][f'freq{freq}']['av']-3*stats[f'beam{beam}'][f'freq{freq}']['std'], 'b-')
        axs[beam_index, freq_col].set_ylim([-20,20])
        axs[beam_index, freq_col].set_xlim([min(ports), max(ports)])
        tick_positions = [1, max(ports)/3, 2*max(ports)/3, max(ports)]
        axs[beam_index, freq_col].set_xticks(tick_positions)
        axs[beam_index, freq_col].set_xlabel('port')
        axs[beam_index, freq_col].set_ylabel('dB')
        axs[beam_index, freq_col].set_title(f'beam {beam}, {freq} GHz')
        freq_col += 1
fig.tight_layout()

# plot devs
plt.figure(figsize=(12,4))
markers = ['o','s']

inner1 = devs['beam1']
arrs1 = np.stack(list(inner1.values()))
innerN = devs['beam2']
arrsN = np.stack(list(innerN.values()))
arrsN = np.vstack([arrs1, arrsN])
avgN = np.linalg.norm(arrsN, axis=0)
       
plt.plot(np.array(mean_ranks), 'ko-')
plt.ylabel('Euclidean')
plt.ylim([0,1000])
plt.xlim([0,400])
plt.xlabel('board')
plt.grid('on')

# output
np.savetxt("output.csv", qr_order, fmt="%s", delimiter=",")
