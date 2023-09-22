# imports
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np
import pandas as pd
from pylab import *
import os
plt.close('all')

# import geometry files
df_geom = pd.read_csv(r'20221019_TLMCalInputs\MK1_RX_TLM_RFIC_Patch_Feed_mapping.csv', skiprows=[0])
df_geom_IC = pd.read_csv(r'20221019_TLMCalInputs\Mrk1_S2000_RX_ArrayGeometry_V20062022.csv')

# patch positions
x = np.array(df_geom[' Feed x [mm]']); y = np.array(df_geom[' Feed y [mm]'])

def import_OP_files(FOM, frequency_GHz, meas_filename_beam1, meas_filename_beam2):
    global meas_data_beams, meas_info
    # import measurements
    head_info_len = 25
    
    meas_data_dict = {}
    meas_info = {}
    # arrays beam 1
    meas_data_dict['beam1'] = np.genfromtxt(r'20221019_TLMCalInputs' + meas_filename_beam1, delimiter=',', dtype=float, skip_header=head_info_len, filling_values = 0)
    meas_info['beam1'] = np.genfromtxt(r'20221019_TLMCalInputs' + meas_filename_beam1, delimiter=',', dtype=str, skip_header=1, skip_footer=len(meas_data_dict['beam1']), filling_values = 0)
    meas_data_dict['beam1_frequencies'] = np.genfromtxt(r'20221019_TLMCalInputs' + meas_filename_beam1, delimiter=',', dtype=float, skip_header=head_info_len-1, skip_footer=len(meas_data_dict['beam1']), filling_values = 0)
    
    # arrays beam 2
    meas_data_dict['beam2'] = np.genfromtxt(r'20221019_TLMCalInputs' + meas_filename_beam2, delimiter=',', dtype=float, skip_header=head_info_len,filling_values = 0)
    meas_info['beam2'] = np.genfromtxt(r'20221019_TLMCalInputs' + meas_filename_beam2, delimiter=',', dtype=str, skip_header=1, skip_footer=len(meas_data_dict['beam2']), filling_values = 0)
    meas_data_dict['beam2_frequencies'] = np.genfromtxt(r'20221019_TLMCalInputs' + meas_filename_beam2, delimiter=',', dtype=float, skip_header=head_info_len-1, skip_footer=len(meas_data_dict['beam2']), filling_values = 0)
    
    # remove zeros on frequency list (and check the frequency lists are the same between beams 1 and 2)
    if np.array_equal(meas_data_dict['beam1_frequencies'],meas_data_dict['beam2_frequencies']) == True:
        meas_frequencies = meas_data_dict['beam1_frequencies'][meas_data_dict['beam1_frequencies'] != 0]
    
    # split up files into beams and polarisations for a given frequency
    meas_data_beams = {}
    
    for beam in range(2):
        if beam == 0:
            meas_data = meas_data_dict['beam1']*1.0
        else:
            meas_data = meas_data_dict['beam2']*1.0
        
        # split into amplitude and phase
        if FOM == 'amp [dB]':
            meas_data_FOM = meas_data[:,0::2]
        if FOM == 'phase [deg]':
            meas_data_FOM = meas_data[:,1::2]
        meas_data_beams['beam'+str(beam+1)] = meas_data_FOM*1.0
        
        # split into odd and even
        meas_data_beams['beam'+str(beam+1)+'_odd_fullRange'] = meas_data_FOM[::2]
        meas_data_beams['beam'+str(beam+1)+'_even_fullRange'] = meas_data_FOM[1::2,:]
    
        # split into frequency
        f_loc = np.argmin(np.abs(meas_frequencies-frequency_GHz))
        frequency_GHz = meas_frequencies[f_loc]
        meas_data_beams['beam'+str(beam+1)+'_odd'] = meas_data_beams['beam'+str(beam+1)+'_odd_fullRange'][:,f_loc:f_loc+1]
        meas_data_beams['beam'+str(beam+1)+'_even'] = meas_data_beams['beam'+str(beam+1)+'_even_fullRange'][:,f_loc:f_loc+1]

def plot__TLM_IC_Links():
    for k in range(3):
        df_geom_lens = df_geom[(df_geom["Lens no."] == k+1)]
        for i in range(int(len(df_geom_IC)/4)):
            IC_patch_numbers = np.array(df_geom_IC[(df_geom_IC["RFIC Number"] == (i+1))]['Patch Number'])
            xarray = []; yarray = []
            for j in range(4):
                xarray.append(np.array(df_geom_lens[(df_geom_lens[' Feed no.'] == (IC_patch_numbers[j]))][' Feed x [mm]']))
                yarray.append(np.array(df_geom_lens[(df_geom_lens[' Feed no.'] == (IC_patch_numbers[j]))][' Feed y [mm]']))
            plt.plot(xarray,yarray,'k-',alpha=.3)
        
def plot__TLM_Visual(xmin, xmax, cmin, cmax, ymin, ymax, colSeg, IC_links):
    dataSet_cycle = ['beam1_odd', 'beam1_even', 'beam2_odd', 'beam2_even']
    for i in range(4):
        a = meas_data_beams[dataSet_cycle[i]]
        # plot
        plt.subplot(2, 2, i+1)
        plt.scatter(x, y, c=a, cmap = cm.get_cmap('jet', colSeg))
        plt.colorbar()
        # ranges
        plt.clim(cmin, cmax); plt.xlim([xmin, xmax]); plt.ylim([ymin,ymax])
        # labels
        plt.xlabel('x [mm]'); plt.ylabel('y [mm]')
        plt.text(0,50, FOM + ' = ' + str(np.round(np.mean(a),1)) + ' $\pm$ ' 
                 + str(np.round(np.std(a),1)), bbox={'facecolor':'none','edgecolor':'black'})
        # title
        plt.title(FOM + ', ' + dataSet_cycle[i][0:5] + ', ' 
                  +  str(frequency_GHz) + ' GHz, ' + dataSet_cycle[i][6:] + ' ports')
        # IC layouts
        if IC_links == True:
            plot__TLM_IC_Links() # definition
        # info table
        if dataSet_cycle[i][6:] == 'even':
            meas_info_str = '----- Measurement Information BEAM ' + dataSet_cycle[i][4:5] + '-----\n'
            for j in range(len(meas_info['beam1'])):
                meas_info_str = meas_info_str + meas_info[dataSet_cycle[i][0:5]][j,0] + ': ' + meas_info[dataSet_cycle[i][0:5]][j,1] + '\n'
            plt.text(100,-50,meas_info_str)
        # layout
        plt.tight_layout(h_pad=2, w_pad=4)
        # save
        plt.savefig('_figures/VisFile_' + FOM + '_' + str(frequency_GHz) + meas_info['beam1'][0][1][0:10] + '.png', dpi=500) ######################

##### Run #####
path = os.path.join(os.getcwd(),'20221019_TLMCalInputs')
items = [f for f in os.listdir(path) if os.path.isfile( os.path.join(path, f) )]
beam1_fileNames = []
beam2_fileNames = []
for i in range(len(items)):
    if 'Beam1' in items[i]:
        beam1_fileNames.append('\\' + items[i])
    if 'Beam2' in items[i]:
        beam2_fileNames.append('\\' + items[i])

# inputs
meas_filename_beam1 = r'\OP_230607-19_19_11-None_QR00006-ES2c_TSW_1p14p491_CCG24_PCG24-CGNone_None_biasNone_p-40_rx_Beam1_HV_17.7_21.2_GHz_both_21.2_GHz_45C.csv'
meas_filename_beam2 = r'\OP_230607-19_19_11-None_QR00006-ES2c_TSW_1p14p491_CCG24_PCG24-CGNone_None_biasNone_p-40_rx_Beam2_HV_17.7_21.2_GHz_both_21.2_GHz_45C.csv'
FOM = 'amp [dB]'
frequency_GHz = 21.2

# plot
plt.figure(figsize=(17,9))
import_OP_files(FOM, frequency_GHz, meas_filename_beam1, meas_filename_beam2)
plot__TLM_Visual(-60, 60, -40, -5, -60, 60, 7, True)
    
# meas_filename_beam1 = beam1_fileNames[l]
# meas_filename_beam2 = beam2_fileNames[l]

# # plot loop frequencies
# freqList = np.linspace(27.5, 31.0, num=8)
# freqList = [29.5]
# for plotLoop in range(len(freqList)):
#     frequency_GHz = freqList[plotLoop]*1.0
#     plt.figure(figsize=(17,9))
#     import_OP_files(FOM, frequency_GHz, meas_filename_beam1, meas_filename_beam2)
#     plot__TLM_Visual(-60, 60, -40, -5, -60, 60, 7, True)