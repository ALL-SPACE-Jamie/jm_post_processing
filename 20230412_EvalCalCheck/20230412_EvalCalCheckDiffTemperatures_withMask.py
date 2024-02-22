import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
import os
import csv
import time
import shutil


plt.rcParams['font.size'] = 12
plt.close('all')
input_folder = r"C:\input\Test_Folder_Calibration"
#input_folder = os.getcwd()

# params for notebook?
temperature = '45'
Type = '0267'
#measType = 'Evaluation' #or 'Evaluation'
measType = "Calibration"
#meas_file_path = r'C:\Users\RyanFairclough\Downloads\All_P-type_Evals'
meas_file_path = r"C:\input\Test_Folder_Calibration"
save_file_name = '\Post_Processed_Data_OP'
BoardFont = '6'
mask_lim_variable = []
external_folder_name = "Figures"
meas_file_shift = 0
droppedThresh = 0
Exempt_Folder = 'Archive'
Exempt_Folder2 = 'combiner'
file_type = 'OP'

tlmType = 'Tx'  # kym read this from test_info file

# frequencies to iterate through
if tlmType == 'Tx':
    mask_lim_variable = [5]
if tlmType == 'Rx':
    mask_lim_variable = [5]
if measType == 'Evaluation' and tlmType == 'Tx':
    f_set_list = [29.5]
    droppedThreshList = [droppedThresh]
elif measType == 'Calibration' and tlmType == 'Tx':
    f_set_list = [27.5, 28.0, 28.5, 29.0, 29.5, 30.0, 30.5, 31.0]
    droppedThreshList = [3, 10, 10, 7, 7, 7, 7, 0]
elif measType == 'Evaluation' and tlmType == 'Rx':
    f_set_list = [19.2]
    droppedThreshList = [0]
elif measType == 'Calibration' and tlmType == 'Rx':
    f_set_list = [17.70]#[17.70, 18.20, 18.70,19.20, 19.70, 20.20, 20.70, 21.20]
    droppedThreshList = [10, 15, 15, 15, 15, 15, 15, 10]
if measType == 'Calibration' and tlmType == 'Tx':
    mask = os.path.join(input_folder,r'2023_06_07_Sweep_Discrete_7pts_calibration_data_ES2_TX_TLM_Lens1_cal_equ_FR_'
                                     r'Norm_renormalization_of_ports.csv')
elif measType == 'Calibration' and tlmType == 'Rx':
    mask = os.path.join(input_folder,r'2023_03_17_discrete_17700_21200_8_calibration_data_175-0081_sanmina_rel1c_2023_'
                                     r'03_07_L1L14_48feed_calibration_13mm_dual_pol_probe_2.csv')
elif measType == 'Evaluation' and tlmType == 'Tx':
    mask = os.path.join(input_folder, r'2023_09_22_Sweep_FF_calibration_data_LensA_Sim_HFSS_ES2iXS_perf_eval_stackup_'
                                      r'Cluster_freq_change_sorted_Edit.csv')
elif measType == 'Evaluation' and tlmType == 'Rx':
    mask = os.path.join(input_folder, r'2023_10_31_discrete_17700_21200_8_calibration_data_175-0212_sanmina_rel1c_'
                                      r'2023_perf_eval_sorted.csv')


def find_meas_files(path, file_string, beam):
    meas_files = []
    for root, _directories, filenames in os.walk(path):
        for filename in filenames:
            if (filename.endswith(".csv")
                    and file_string in filename
                    and 'eam' + str(beam) in filename
                    and Exempt_Folder not in root
                    and Exempt_Folder2 not in root):
                meas_files.append(os.path.join(root, filename))
    return meas_files


def import_mask(f_set, mask, offset):
    meas_array = np.genfromtxt(mask, delimiter=',', skip_header=1)[:,2:]
    meas_array_frequencies = np.genfromtxt(mask, delimiter=',', skip_header=1)[0:int(len(meas_array)/2),1]
    index = np.argmin((meas_array_frequencies-float(f_set))**2)
    meas_array_t = meas_array[index,:][::2]
    meas_array_b = meas_array[int(len(meas_array)/2)+index,:][::2]
    meas_array_gain = np.zeros(len(meas_array_t))
    meas_array_gain_cross = np.zeros(len(meas_array_t))
    for i in range(int(len(meas_array_t)/2)):
        meas_array_gain[2*i] = meas_array_t[2*i]
        meas_array_gain[2*i+1] = meas_array_b[2*i+1]
        meas_array_gain_cross[2*i] = meas_array_t[2*i+1]
        meas_array_gain_cross[2*i+1] = meas_array_b[2*i]
    meas_array_t = meas_array[index,:][1:][::2]
    meas_array_b = meas_array[int(len(meas_array)/2)+index,:][1:][::2]
    meas_array_phase = np.zeros(len(meas_array_t))
    for i in range(int(len(meas_array_t)/2)):
        meas_array_phase[2*i] = meas_array_t[2*i]
        meas_array_phase[2*i+1] = meas_array_b[2*i+1]
    mask_gain = meas_array_gain*1.0 + offset
    mask_gain_cross = meas_array_gain_cross*1.0 + offset
    for i in range(len(mask_gain)):
        if mask_gain_cross[i] > mask_gain[i]:
            mask_gain[i] = mask_gain_cross[i]*1.0
    mask_phase = meas_array_phase*1.0
    mask_gain_hstack = np.hstack([mask_gain, mask_gain, mask_gain])
    mask_phase = np.hstack([mask_phase, mask_phase, mask_phase])
    return mask_gain_hstack

def load_meas_files(meas_file_path):
    meas_params = {}
    meas_info = []
    # meas_info, array and measurement frequencies
    with open(meas_file_path, 'r') as file:
        filecontent = csv.reader(file, delimiter=',')
        time.sleep(0.10)
        for row in filecontent:
            meas_info.append(row)
        index_start = [index for index in range(len(meas_info)) if 'barcodes' in meas_info[index]][0] + 2
        meas_info = meas_info[0:index_start]

        meas_array = np.genfromtxt(meas_file_path, delimiter=',', skip_header=index_start)
        meas_frequencies = np.array(meas_info[index_start - 1])[::2].astype(float)


    for i in range(len(meas_info) - 1):
        if len(meas_info[i]) > 1:
            param_name = meas_info[i][0]

            if param_name[0:2] == '# ':
                param_name = param_name[2:]
            meas_params[param_name] = meas_info[i][1]
    return meas_array, meas_frequencies, meas_params


def plot_gain_v_port(f_set, measType, meas_array, meas_frequencies, meas_params):
    fig.suptitle(measType + ': ' + str(f_set) + ' GHz, Beam ' + str(beam) + ', ' + str(temperature) + ' degC',
                 fontsize=25)
    if float(meas_params['f_c']) == f_set and len(meas_array) > 2:
        print('Plotting')
        # array
        col = int(np.where(meas_frequencies == f_set)[0][0] * 2)
        y = meas_array[:, col]
        y_gain = y * 1.0

        # stats
        stat_TLM_median = np.median(y)
        stat_TLM_median_log.append(stat_TLM_median)
        barcode_num.append(meas_params['barcodes'])
        stat_l1_median = np.median(y[0:int(len(y) / 3)])
        stat_l2_median = np.median(y[int(len(y) / 3):2 * int(len(y) / 3)])
        stat_l3_median = np.median(y[2 * int(len(y) / 3):3 * int(len(y) / 3)])
        mask_gain = import_mask(f_set, mask, 0.0)
        if tlmType == 'Tx':
            mask_l1 = mask_gain[:152]
            mask_l2 = mask_gain[152:304]
            mask_l3 = mask_gain[304:456]
        else:
            mask_l1 = mask_gain[:96]
            mask_l2 = mask_gain[96:192]
            mask_l3 = mask_gain[192:288]
        mask_offset = np.median(np.array(stat_TLM_median_log)) - np.median(np.array(mask_gain))
        mask_G_lens1 = mask_l1 + mask_offset
        mask_G_lens2 = mask_l2 + mask_offset
        mask_G_lens3 = mask_l3 + mask_offset
        mask_gain_lim1 = [item -5 for item in mask_G_lens1]
        mask_gain_lim3 = [item -5 for item in mask_G_lens2]
        mask_gain_lim5 = [item -5 for item in mask_G_lens3]
        stat_l1_dropped = (y[0:int(len(y) / 3)] < mask_gain_lim1).sum()
        stat_l1_dropped_list = ((y[0:int(len(y) / 3)]) < droppedThresh)
        stat_l2_dropped_list = ((y[int(len(y) / 3):2 * int(len(y) / 3)]) < droppedThresh)
        stat_l3_dropped_list = ((y[2 * int(len(y) / 3):3 * int(len(y) / 3)]) < droppedThresh)

        log = []
        for p in range(len(stat_l1_dropped_list)):
            if stat_l1_dropped_list[p]:
                log.append(p + 1)
        for p in range(len(stat_l2_dropped_list)):
            if stat_l2_dropped_list[p]:
                log.append(1 * int(len(y) / 3) + p + 1)
        for p in range(len(stat_l3_dropped_list)):
            if stat_l3_dropped_list[p]:
                log.append(2 * int(len(y) / 3) + p + 1)
        if len(log) > 12:
            log = [str(len(log)) + ' ports dropped']
        stat_l2_dropped = ((y[int(len(y) / 3):2 * int(len(y) / 3)]) < mask_gain_lim3).sum()
        stat_l3_dropped = ((y[2 * int(len(y) / 3):3 * int(len(y) / 3)]) < mask_gain_lim5).sum()
        stat_TLM_std = np.std(y, dtype=np.float64)  ##

        stat_l1_std = np.std(y[0:int(len(y) / 3)])
        stat_l2_std = np.std(y[int(len(y) / 3):2 * int(len(y) / 3)])
        stat_l3_std = np.std(y[2 * int(len(y) / 3):3 * int(len(y) / 3)])

        # plots
        data_set_label = (meas_params['date time'] + '\n' + meas_params['lens type (rx/tx)'] + meas_params['barcodes']
                          + ', SW: ' + meas_params['acu_version'] + '\n ITCC: ' + meas_params['itcc_runner_version'])

        # plot 1
        minY = -30
        maxY = 60
        axs[0, 0].vlines(int(len(y) / 3), minY, maxY, 'k', alpha=0.2)
        axs[0, 0].vlines(2 * int(len(y) / 3), minY, maxY, 'k', alpha=0.2)
        axs[0, 0].text(0.8 * int(len(y) / 6), minY + 5, 'Lens 1', backgroundcolor='r', fontsize=20)
        axs[0, 0].text(2.8 * int(len(y) / 6), minY + 5, 'Lens 2', backgroundcolor='g', fontsize=20)
        axs[0, 0].text(4.8 * int(len(y) / 6), minY + 5, 'Lens 3', backgroundcolor='b', fontsize=20)
        if '0267' in meas_params['barcodes']:
            axs[0, 0].plot(np.linspace(1, len(y), num=len(y)), y, 'r', alpha=0.2)
        elif 'B2' in meas_params['barcodes']:
            axs[0, 0].plot(np.linspace(1, len(y), num=len(y)), y, 'y', alpha=0.2)
        elif 'v3' in meas_params['barcodes']:
            axs[0, 0].plot(np.linspace(1, len(y), num=len(y)), y, 'g', alpha=0.2)
        else:
            axs[0, 0].plot(np.linspace(1, len(y), num=len(y)), y, 'k', alpha=0.2)
        axs[0, 0].set_xlabel('port')
        axs[0, 0].set_ylabel('S$_{21}$ [dB]')
        axs[0, 0].set_xticks([0.5 * int(len(y) / 3), 1 * int(len(y) / 3), 1.5 * int(len(y) / 3),
                              2 * int(len(y) / 3), 2.5 * int(len(y) / 3), 3 * int(len(y) / 3)])
        axs[0, 0].set_xlim([1, len(y) + 1])
        axs[0, 0].set_ylim([minY, maxY])
        axs[0, 0].grid('on')
        axs[0, 1].plot(data_set_label, stat_l1_median, 'rs')
        axs[0, 1].plot(data_set_label, stat_l2_median, 'g^')
        axs[0, 1].plot(data_set_label, stat_l3_median, 'bP')
        if '0267' in meas_params['barcodes']:
            axs[0, 1].plot(data_set_label, stat_TLM_median, 'rX', markersize=10)
        elif 'B2' in meas_params['barcodes']:
            axs[0, 1].plot(data_set_label, stat_TLM_median, 'yX', markersize=10)
        elif 'v3' in meas_params['barcodes']:
            axs[0, 1].plot(data_set_label, stat_TLM_median, 'gX', markersize=10)
        else:
            axs[0, 1].plot(data_set_label, stat_TLM_median, 'kX', markersize=10)
        rounded = round(stat_TLM_median,1)
        axs[0, 1].text(data_set_label,stat_TLM_median + 5, rounded, fontsize=3 )

        with open(r'C:\Measurements\Gain_+_SerialNo.csv', mode='w') as file:
            writer = csv.writer(file)
            writer.writerow(['Serial_Number', 'Median_Gain'])
            for value in barcode_num:
                writer.writerow([value])
            for value in stat_TLM_median_log:
                writer.writerow(['', value])

        axs[0, 1].set_xlabel('board')
        axs[0, 1].set_ylabel('Median [dB]')
        axs[0, 1].tick_params(axis='x', labelrotation=90, labelsize=BoardFont)
        axs[0, 1].set_ylim([minY, maxY])
        axs[0, 1].grid('on')
        # plot 3
        axs[1, 1].plot(data_set_label, stat_l1_std, 'rs')
        axs[1, 1].plot(data_set_label, stat_l2_std, 'g^')
        axs[1, 1].plot(data_set_label, stat_l3_std, 'bP')
        axs[1, 1].plot(data_set_label, stat_TLM_std, 'kX', markersize=10)
        axs[1, 1].set_xlabel('board')
        axs[1, 1].set_ylabel('$\sigma$ [dB]')
        axs[1, 1].tick_params(axis='x', labelrotation=90, labelsize=BoardFont)
        axs[1, 1].set_ylim([0, 20])
        axs[1, 1].grid('on')
        # plot 4
        if stat_l1_dropped + stat_l2_dropped + stat_l3_dropped > 50:
            axs[2, 1].plot(data_set_label, 5.0, 'rX', markersize=30)
        axs[2, 1].plot(data_set_label, stat_l1_dropped, 'rs')
        axs[2, 1].plot(data_set_label, stat_l2_dropped, 'g^')
        axs[2, 1].plot(data_set_label, stat_l3_dropped, 'bP')
        axs[2, 1].set_xlabel('board')
        axs[2, 1].set_ylabel('Number of dropped ports (gain < ' + str(droppedThresh) + ' dB)')
        axs[2, 1].text(data_set_label, 2.0, log)  # bug
        axs[2, 1].tick_params(axis='x', labelrotation=90, labelsize=BoardFont)
        axs[2, 1].set_ylim([0, 10])
        axs[2, 1].grid('on')
        # plot 5
        y = meas_array[:, col + 1]
        minY = -90
        maxY = 360 + 45
        axs[1, 0].vlines(int(len(y) / 3), minY, maxY, 'k', alpha=0.2)
        axs[1, 0].vlines(2 * int(len(y) / 3), minY, maxY, 'k', alpha=0.2)
        axs[1, 0].text(0.8 * int(len(y) / 6), minY + 35, 'Lens 1', backgroundcolor='r', fontsize=20)
        axs[1, 0].text(2.8 * int(len(y) / 6), minY + 35, 'Lens 2', backgroundcolor='g', fontsize=20)
        axs[1, 0].text(4.8 * int(len(y) / 6), minY + 35, 'Lens 3', backgroundcolor='b', fontsize=20)
        axs[1, 0].plot(np.linspace(1, len(y), num=len(y)), y, 'k', alpha=0.2)
        axs[1, 0].set_xlabel('port')
        axs[1, 0].set_ylabel('Phase [deg]')
        axs[1, 0].set_xlim([1, len(y) + 1])
        axs[1, 0].set_ylim([minY, maxY])
        axs[1, 0].set_yticks(np.linspace(0, 360, num=int(360 / 45) + 1))
        axs[1, 0].set_xticks([0.5 * int(len(y) / 3), 1 * int(len(y) / 3), 1.5 * int(len(y) / 3), 2 * int(len(y) / 3),2.5 * int(len(y) / 3), 3 * int(len(y) / 3)])
        axs[1, 0].grid('on')

        # out
        return y, stat_TLM_median, y_gain, mask_gain
    else:
        return None


all_barcodes =[]
y = None
y_gain = None
mask_gain = None
stat_TLM_median = None

# run
for beam in range(1, 3):
    for l in range(len(f_set_list)):
        f_set = f_set_list[l]
        droppedThresh = droppedThreshList[l]

        # find all meas files
        meas_files = find_meas_files(meas_file_path, file_type, beam)

        fig, axs = plt.subplots(3, 2, figsize=(25, 15))
        stat_TLM_median_log = []
        barcode_num =[]
        y_gain_log = []
        tlm_log = []
        for k in range(len(meas_files) - meas_file_shift):
            # load meas file
            if f"_{temperature}C" in meas_files[k]:
                print(f"***kym meas file k = {meas_files[k]}, temp = {temperature}")
                meas_array, meas_frequencies, meas_params =  load_meas_files(meas_files[k])
                print('-------------------------------------')
                print(meas_params['date time'][1:])
                print(meas_params['barcodes'])
                print('Temperature = ' + meas_params['Temp. [°C]'])
                print('-------------------------------------')

                # plot
                if '.' in meas_params['acu_version']:
                    plot_data = plot_gain_v_port(f_set, measType, meas_array, meas_frequencies, meas_params)
                    # colate
                    if plot_data is not None:
                        y, stat_TLM_median, y_gain, mask_gain = plot_data
                        y_gain_log.append(y_gain)
                        tlm_log.append(meas_params['barcodes'])
                        all_barcodes.append(meas_params['barcodes'])#
                        list(set(all_barcodes))
                        all_barcodes.sort()
                        print(all_barcodes)

        # mask
        mask_gain = import_mask(f_set, mask, 0.0)
        mask_offset = np.median(np.array(stat_TLM_median_log)) - np.median(np.array(mask_gain))
        axs[0, 0].plot(np.linspace(1, len(mask_gain), num=len(mask_gain)), mask_gain + mask_offset, 'g-', alpha=0.5)
        axs[0, 0].fill_between(
            np.linspace(1, len(mask_gain), num=len(mask_gain)), mask_gain + mask_offset - mask_lim_variable,
            mask_gain + mask_offset + mask_lim_variable, color='green', alpha=0.2)

        # plot histogram
        ymax1 = 25.0
        mean = np.mean(np.array(stat_TLM_median_log))

        axs[2, 0].hist(np.array(stat_TLM_median_log), bins=11)
        axs[2, 0].set_xlabel('TLM median [dB]')
        axs[2, 0].set_ylabel('count')
        axs[2, 0].set_xlim([mean - 5, mean + 5])
        axs[2, 0].set_ylim([0, 25])
        axs[2, 0].axvline(mean, ymin=0.0, ymax=ymax1, color='k')
        axs[2, 0].grid('on')
        variance = np.var(np.array(stat_TLM_median_log))
        sigma = np.sqrt(variance)
        x = np.linspace(-50, 50, 10001)
        axs[2, 0].plot(x, ymax1 * norm.pdf(x, mean, sigma) / (max(norm.pdf(x, mean, sigma))), 'r')
        axs[2, 0].text(mean + 0.1, 10.25, str(round(mean, 2)) + ' dB ($\sigma$ = ' + str(round(sigma, 1)) + ')',rotation=90)

        # mask_check
        tlm_numbers = []
        for jj in range(len(y_gain_log)):
         delta = y_gain_log[jj] - (mask_gain + mask_offset)
         if max(abs(delta)) > mask_lim_variable:
                print('TLMs_in_List:',tlm_log[jj])
                for k in range(len(tlm_log)):
                    tlm_numbers.append(len(tlm_log))
                    tlm_numbers = list(set(tlm_numbers))
                    axs[0,1].text(0, stat_TLM_median - 35, 'Total_Number_of_TLMs: ' + str(tlm_numbers))

                for i in range(len(delta)):
                    if abs(delta[i]) > mask_lim_variable:
                        axs[0, 0].plot(i + 1, y_gain_log[jj][i], 'ro', markersize=1)

        # format
        plt.tight_layout()

        # save
        image_file_name = measType + '_f-set' + str(f_set) + '_b' + str(beam) + '.png'
        newPath = meas_file_path + save_file_name
        if not os.path.exists(newPath):
            os.makedirs(newPath)
        image_file_path = os.path.join(newPath, image_file_name)
        plt.savefig(image_file_path, dpi=200)

external_path = os.path.join(meas_file_path, external_folder_name)
os.makedirs(external_path, exist_ok=True)  # The path of the external folder

for dirpath, _dirnames, filenames in os.walk(meas_file_path):
    for file in filenames:
        if 'f-set' in file.lower():
            try:
                file_path = os.path.join(dirpath, file)
                shutil.copy(file_path, external_path)
                print(f"Copied {file_path} to {external_path}")
            except shutil.SameFileError as e:
                print(f"Skipped copying file: {e}")
print("Done.")