import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import csv
import pickle
import warnings; warnings.filterwarnings("ignore", category=pd.errors.ParserWarning)
import scipy.stats as stats
import datetime

# set-up
setUp = {}
setUp['filePath'] = r'C:\scratch\20240925'
setUp['pathCreate'] = ['figures', 'figuresBAD', 'files', 'pickles', 'overviews']
setUp['filePath_forInterp'] = setUp['filePath'] + r'\_data_forInterp'
setUp['picklePath'] = setUp['filePath'] + r'\pickles'
setUp['fileOutPath'] = setUp['filePath'] + r'\files'

# create directories
for subDirectory in setUp['pathCreate']:
    directory = setUp['filePath'] + '\\' + subDirectory
    print(directory)
    if not os.path.exists(directory):
        os.makedirs(directory)

# definitions
def find__measFiles(filePath, fileString):
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

def find__fileDetails(filePath):
    global meas_array_gain, meas_array_phase, df_meas, meas_frequencies, meas_array
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

    # col = np.argmin((meas_frequencies-float(df_entry['f_c']))**2)
    col = np.argmin((meas_frequencies - float(df_entry['f_c'].iloc[0]))**2)
    meas_array_gain_col = meas_array_gain[:,col]
    meas_array_phase_col = meas_array_phase[:,col]
    df_entry.at[[0], 'meas_frequencies'] = np.array2string(meas_frequencies, separator=',')[1:-1]
    df_entry.at[[0], 'meas_array_gain_col'] = np.array2string(meas_array_gain_col, separator=',')[1:-1]
    df_entry.at[[0], 'meas_array_phase_col'] = np.array2string(meas_array_phase_col, separator=',')[1:-1]
        
    return df_entry

def board_gradient_calculator(board, df, freq, FoM, beam):
    global df_board_frequency, chisq_log, x, y, temperature_evolution, gain_evolution, df_for_eval, df_board_frequency, df_board, df_board_frequency_beam
    df_board = df[df['barcodes']==board]
    df_board_frequency = df_board[df_board['f_c']==freq]
    df_board_frequency_beam = df_board_frequency[df_board_frequency['Beam']==str(beam)]
    df_for_eval = df_board_frequency_beam.copy()
    
    # temperature measurement points
    gain_evolution = np.zeros_like(np.fromstring(df_for_eval['meas_array_gain_col'].iloc[0], dtype=float, sep=','))
    phase_evolution = np.zeros_like(np.fromstring(df_for_eval['meas_array_phase_col'].iloc[0], dtype=float, sep=','))
    temperature_evolution = np.zeros_like(np.fromstring(df_for_eval['rfic temperature'].iloc[0], dtype=float, sep=','))
    for idx in range(len(df_for_eval)):
        gain = np.fromstring(df_for_eval['meas_array_gain_col'].iloc[idx], dtype=float, sep=',')
        phase = np.fromstring(df_for_eval['meas_array_phase_col'].iloc[idx], dtype=float, sep=',')
        temperature = np.fromstring(df_for_eval['rfic temperature'].iloc[idx], dtype=float, sep=',')
        
        gain_evolution = np.vstack([gain_evolution, gain])
        phase_evolution = np.vstack([phase_evolution, phase])
        temperature_evolution = np.vstack([temperature_evolution, temperature])
        
    gain_evolution = gain_evolution[1:,:]
    phase_evolution = phase_evolution[1:,:]
    temperature_evolution = temperature_evolution[1:,:]
    
    # port measurement gradients
    # fig_port_fits, ax_port_fits = plt.subplots(nrows=1, ncols=1, figsize=(12, 7))
    linear_fits = []
    chisq_log = []
    quad_fits = []
    x_to_interp = np.linspace(45-30,45+30,num=50)
    for port in range(len(temperature)):
    
        x = temperature_evolution[:,port]
        
        # fix for temperature readings of 0.0
        if min(x) == 0.0:
            for idx in range(len(x)):
                if x[idx] == 0.0:
                    x[idx] = np.median(temperature_evolution[idx,:])
                    
        if FoM == 'gain':
            y = gain_evolution[:,port]
            FoM_unit = 'dB'
        if FoM == 'phase':
            y = phase_evolution[:,port]
            FoM_unit = 'deg'
            y_median = np.median(y)
            for idx in range(len(y)):
                if abs(y[idx] - y_median) > 180.0:
                    if y[idx] - y_median < 0:
                        y[idx] = y[idx] + 360.0
                    else:
                        y[idx] = y[idx] - 360.0
        
        # Linear fit
        linear_fit = np.polyfit(x, y, 1)
        linear_fit_fn = np.poly1d(linear_fit)
        
        # Quadratic fit
        quadratic_fit = np.polyfit(x, y, 2)
        quadratic_fit_fn = np.poly1d(quadratic_fit)
        
        # Plotting the data and the fits
        # if port < 4:
        #     ax_port_fits.plot(x, y, 'bo', label='Data points')
        #     ax_port_fits.plot(x_to_interp, linear_fit_fn(x_to_interp), 'r-', label='Linear fit')
        #     ax_port_fits.plot(x_to_interp, quadratic_fit_fn(x_to_interp), 'g--', label='Quadratic fit')
        #     ax_port_fits.set_xlabel('Temperature [degC]')
        #     ax_port_fits.set_ylabel(f'$\Delta$ {FoM} [{FoM_unit}]')
        #     fig_port_fits.suptitle(f'{rx_tx}\n{FoM} gradient (T), beam{beam}')
        #     ax_port_fits.grid('on')
        
        # normalise to 45 degrees
        y = y - linear_fit_fn(np.array(45))
    
        # Linear fit norm
        linear_fit = np.polyfit(x, y, 1)
        linear_fits.append(linear_fit)
        linear_fit_fn = np.poly1d(linear_fit)
        
        # Quadratic fit norm
        quadratic_fit = np.polyfit(x, y, 2)
        quadratic_fit_fn = np.poly1d(quadratic_fit)
        quad_fits.append(quadratic_fit)
        
        # fit validity
        #perform Chi-Square Goodness of Fit Test
        observed = y
        expected = quadratic_fit_fn(x)
        chisq_log.append(list(stats.chisquare(f_obs=observed, f_exp=expected)))
    
    df_linear_fits = pd.DataFrame(linear_fits, columns = [f'{board}_m', f'{board}_c'])
    df_linear_fits_chisq = pd.DataFrame(chisq_log, columns = [f'{board}_chisqm', f'{board}_chisqp'])
    df_linear_fits = pd.concat([df_linear_fits, df_linear_fits_chisq], axis=1)

    return df_linear_fits

def board_gadients_cycle(boards, df, freq, FoM, beam):
    global m_av, c_av
    df_linear_fits_boards = pd.DataFrame()

    for board in boards:
        df_linear_fits = board_gradient_calculator(board, df, freq, FoM, beam)
        df_linear_fits_boards = pd.concat([df_linear_fits_boards, df_linear_fits], axis=1)
    m_av = np.median(np.array(df_linear_fits_boards)[:, ::4], axis=1)
    c_av = np.median(np.array(df_linear_fits_boards)[:, 1::4], axis=1)
    chi_sqm_av = np.median(np.array(df_linear_fits_boards)[:, 2::4], axis=1)
    chi_sqp_av = np.median(np.array(df_linear_fits_boards)[:, 3::4], axis=1)

    df_linear_fits_boards['m_av'] = m_av
    df_linear_fits_boards['c_av'] = c_av
    df_linear_fits_boards['chisqm_av'] = chi_sqm_av
    df_linear_fits_boards['chisqp_av'] = chi_sqp_av
    
    for port in range(len(df_linear_fits_boards)):
        x_to_interp = np.linspace(45-30,45+30,num=50)
        linear_fit_fn = np.poly1d(np.array([df_linear_fits_boards['m_av'][port], df_linear_fits_boards['c_av'][port]]))
        y = linear_fit_fn(x_to_interp)
    
    return df_linear_fits_boards


# code
dict_gradients = {}

for rx_tx in ['tx', 'rx']:
    for FoM in ['gain', 'phase']:
        for beam in [1,2]:
    
            # rx tx
            if rx_tx == 'rx':
                setUp['filePath_forGradGen'] = r'C:\Users\jmitchell\OneDrive - ALL.SPACE\RF Testing\6 Investigations\20241005_P-Type_TermperatureInterpolation\Gradient_Generation\Rx_2024'
                freq_list = ['17.7', '18.2', '18.7', '19.2', '19.7', '20.2', '20.7', '21.2']
                # freq_list = ['17.7', '18.2']
            if rx_tx == 'tx':
                freq_list = ['27.5', '28', '28.5', '29', '29.5', '30', '30.5', '31.0']
                setUp['filePath_forGradGen'] = r'C:\Users\jmitchell\OneDrive - ALL.SPACE\RF Testing\6 Investigations\20241005_P-Type_TermperatureInterpolation\Gradient_Generation\Tx' ###########################################
                # freq_list = ['27.5', '28']
                
            # find the meas files
            meas_files = find__measFiles(setUp['filePath_forGradGen'], 'SEC')
            log = []
            
            # initialise plots
            fig_hist, ax_hist = plt.subplots(nrows=2, ncols=2, figsize=(12, 7))
            
            # gain or phase
            if FoM == 'gain':
                grad_unit = 'dB/degC'
                grad_lim = [-0.3,0.0]
                bin_width = 0.01
                count_lim = [0,200]
            if FoM == 'phase':
                grad_unit = 'deg/degC'
                grad_lim = [-1.0,1.0]
                bin_width = 0.05
                count_lim = [0,200]
            
            # cycle through frequencies
            grad_log = []
            for freq in freq_list:
            
                # create a df and add in all measurement parameters and arrays
                # (arrays as strings because pandas is not great for this)
                df = pd.DataFrame()
                for meas_file in meas_files:
                    df_entry = find__fileDetails(meas_file)
                    df = pd.concat([df, df_entry])
                
                # cycle through boards for a fixed frequency and beam
                # create a dataframe for m and c values
                boards = set(list(df['barcodes']))
                df_linear_fits_boards = board_gadients_cycle(boards, df, freq, FoM, beam)
                grad_log.append(np.median(df_linear_fits_boards['m_av']))
                
                # histogram
                data = df_linear_fits_boards['m_av'].copy()
                bins = np.arange(min(data), max(data) + bin_width, bin_width)
                ax_hist[0,0].hist(data, label=f'{freq}', alpha=0.75, bins=bins)
                log.append(np.median(df_linear_fits_boards['m_av']))
                
                # port grads
                ax_hist[1,0].plot(data, 'o', label=f'{freq}', alpha=0.7)
                
                # chisq
                ax_hist[1,1].plot(df_linear_fits_boards['chisqp_av'], 'o', label=f'{freq}', alpha=0.7)
                
            # histogram
            ax_hist[0,1].plot(list(map(float, freq_list)), grad_log, 'o-')
            ax_hist[0,0].set_xlabel(grad_unit)
            ax_hist[0,0].set_xlim(grad_lim)
            ax_hist[0,0].set_ylim(count_lim)
            ax_hist[1,0].set_ylim(grad_lim)
            ax_hist[1,0].set_ylabel(grad_unit)
            ax_hist[1,0].set_xlabel('port')
            ax_hist[1,1].set_xlabel('port')
            ax_hist[1,1].set_ylabel('Chi Sq p-val')
            
            ax_hist[0,0].set_ylabel('count')
            fig_hist.suptitle(f'{rx_tx}\n{FoM} gradient (T), beam{beam}')
            ax_hist[0,1].set_xlabel('frequency [GHz]')
            ax_hist[0,1].set_ylabel(grad_unit)
            ax_hist[0,1].set_ylim(grad_lim)
            ax_hist[0,0].legend()
            ax_hist[1,0].legend()
            ax_hist[1,1].legend()
            ax_hist[0,0].grid('on')
            ax_hist[0,1].grid('on')
            ax_hist[1,0].grid('on')
            ax_hist[1,1].grid('on')
            fig_hist.tight_layout()
            
            # save the figure
            fig_hist.savefig(f'{rx_tx}_{FoM}gradient(T)_beam{beam}.png', dpi=400)
            
            # append to a dictionary
            dict_gradients[f'{rx_tx}_{FoM}_beam{beam}'] = df_linear_fits_boards.copy()

# save pickle
today = str(datetime.datetime.today())[0:19].replace(':','-').replace(' ', '_')
with open(f'{today}_gradients.pkl', 'wb') as file:
    pickle.dump(dict_gradients, file)
    
# # import pickle
# with open(r'C:\GitHub\jm_post_processing\20230610_TLM-TemperatureInterpolation\2024-10-03_17-42-19_gradients.pkl', 'rb') as file:
#     loaded_dict = pickle.load(file)
            