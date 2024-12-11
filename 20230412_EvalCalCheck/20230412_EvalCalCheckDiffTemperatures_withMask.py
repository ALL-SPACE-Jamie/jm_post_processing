import os
import csv
import shutil
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm


def find_meas_files(path, file_string, beam_number, ignored_folders):
    """
    Fine all CSV measurement files in a directory, that match the given criteria on their name and subdirectory
    :param path:  Directory containing the measurement files
    :param file_string: A fragment of text which must be in the filename
    :param beam_number:  Beam number which must be in the filename
    :param ignored_folders: Files in these subdirectories should be ignored
    :return:
    """
    meas_files = []
    for root, _directories, file_names in os.walk(path):
        for filename in file_names:
            if (filename.endswith(".csv")
                    and file_string in filename
                    and f"eam{beam_number}" in filename
                    and all(ignored_folder not in root for ignored_folder in ignored_folders)):
                meas_files.append(os.path.join(root, filename))
                print(filename)
    return meas_files


def load_mask_from_file(mask_filename: str) -> np.ndarray:
    """
    :param mask_filename:  Full path and filename of the mask
    :return: Mask data from file
    """
    mask_data = np.genfromtxt(mask_filename, delimiter=',', skip_header=1)
    return mask_data


def get_mask_for_frequency(mask_data, frequency: float,offset: float):
    """
    Use the mask data and frequency to generate the mask gain.
    :param frequency: A frequency in ?Hz
    :param offset: Offset added to the mask gain and mask gain cross.
    :return: The calculated mask gain
    """
    meas_array = mask_data[:, 2:]
    meas_array_frequencies = mask_data[0:int(len(meas_array)/2), 1]
    index = np.argmin((meas_array_frequencies-float(frequency))**2)
    meas_array_t = meas_array[index, :][::2]
    meas_array_b = meas_array[int(len(meas_array)/2)+index, :][::2]
    meas_array_gain = np.zeros(len(meas_array_t))
    meas_array_gain_cross = np.zeros(len(meas_array_t))
    meas_array_gain[::2] = meas_array_t[::2]
    meas_array_gain[1::2] = meas_array_b[1::2]
    meas_array_gain_cross[::2] = meas_array_t[1::2]
    meas_array_gain_cross[1::2] = meas_array_b[::2]
    mask_gain = meas_array_gain*1.0 + offset
    mask_gain_cross = meas_array_gain_cross*1.0 + offset
    for i in range(len(mask_gain)):
        if mask_gain_cross[i] > mask_gain[i]:
            mask_gain[i] = mask_gain_cross[i]*1.0
    mask_gain_stack = np.hstack([mask_gain, mask_gain, mask_gain])
    return mask_gain_stack


def load_meas_files(meas_file_path: str):
    """
    Read the data from a measurement file and return it.
    :param meas_file_path: Full path and filename to the measurement file
    :return: An array of measurements, an array of frequencies and a dictionary of parameters and their values
    """
    meas_params = {}
    meas_frequencies = None
    # meas_info, array and measurement frequencies
    with open(meas_file_path, 'r') as openfile:
        for line in openfile:
            split_line = line.split(",")
            if len(split_line) >= 2:
                param_name = split_line[0]
                if param_name.startswith("# "):
                    param_name = param_name[2:]
                meas_params[param_name] = split_line[1]
                if "barcodes" in param_name:  # this is the last of the parameter names
                    freq_line = openfile.readline()  # the next line is the frequency values
                    meas_frequencies = np.array(freq_line.split(",")[::2]).astype(float)
                    break  # collected all the parameters
        # The rest of the file is measurement readings which can be read straight into an array without
        # closing and reopening the file, as the file object is on the correct line already.
        csv_reader = csv.reader(openfile)
        readings = list(csv_reader)
        meas_array = np.array(readings).astype(float)
    return meas_array, meas_frequencies, meas_params


def plot_gain_v_port(frequency, meas_array, meas_frequencies, meas_params, tlm_type, fig, axs, suptitle,
                     stat_tlm_median_log, barcode_num, dropped_thresh, mask_data):
    """
    Plot gain vs. frequency
    :param frequency:
    :param meas_array:
    :param meas_frequencies:
    :param meas_params:
    :param tlm_type:
    :param fig:
    :param axs:
    :param suptitle:
    :param stat_tlm_median_log:
    :param barcode_num:
    :param dropped_thresh:
    :param mask_data: Mask data for all frequencies
    :return:
    """
    fig.suptitle(suptitle, fontsize=25)
    board_font = '6'
    if float(meas_params['f_c']) == frequency and len(meas_array) > 2:
        print('Plotting')
        # array
        col = int(np.where(meas_frequencies == frequency)[0][0] * 2)
        y = meas_array[:, col]
        y_gain = y * 1.0
        length_y_over_3 = int(len(y) / 3)
        length_y_over_6 = int(len(y) / 6)

        # stats
        stat_tlm_median = np.median(y)
        stat_tlm_median_log.append(stat_tlm_median)
        barcode_num.append(meas_params['barcodes'])
        stat_l1_median = np.median(y[0:length_y_over_3])
        stat_l2_median = np.median(y[length_y_over_3:2 * length_y_over_3])
        stat_l3_median = np.median(y[2 * length_y_over_3:3 * length_y_over_3])
        mask_gain = get_mask_for_frequency(mask_data, frequency, 0.0)
        if tlm_type == 'Tx':
            mask_l1 = mask_gain[:152]
            mask_l2 = mask_gain[152:304]
            mask_l3 = mask_gain[304:456]
        else:
            mask_l1 = mask_gain[:96]
            mask_l2 = mask_gain[96:192]
            mask_l3 = mask_gain[192:288]
        mask_offset = np.median(np.array(stat_tlm_median_log)) - np.median(np.array(mask_gain))
        mask_g_lens1 = mask_l1 + mask_offset
        mask_g_lens2 = mask_l2 + mask_offset
        mask_g_lens3 = mask_l3 + mask_offset
        mask_gain_lim1 = [item - 5 for item in mask_g_lens1]
        mask_gain_lim3 = [item - 5 for item in mask_g_lens2]
        mask_gain_lim5 = [item - 5 for item in mask_g_lens3]
        stat_l1_dropped = (y[0:int(len(y) / 3)] < mask_gain_lim1).sum()
        stat_l1_dropped_list = (y[0:length_y_over_3]) < dropped_thresh
        stat_l2_dropped_list = (y[length_y_over_3:2 * length_y_over_3]) < dropped_thresh
        stat_l3_dropped_list = (y[2 * length_y_over_6:3 * length_y_over_3]) < dropped_thresh

        log = []
        for p, is_dropped in enumerate(stat_l1_dropped_list):
            if is_dropped:
                log.append(p + 1)
        for p, is_dropped in enumerate(stat_l2_dropped_list):
            if is_dropped:
                log.append(1 * length_y_over_3 + p + 1)
        for p, is_dropped in enumerate(stat_l3_dropped_list):
            if is_dropped:
                log.append(2 * length_y_over_3 + p + 1)
        if len(log) > 12:
            log = [str(len(log)) + ' ports dropped']
        stat_l2_dropped = ((y[length_y_over_3:2 * int(len(y) / 3)]) < mask_gain_lim3).sum()
        stat_l3_dropped = ((y[2 * length_y_over_3:3 * length_y_over_3]) < mask_gain_lim5).sum()
        stat_tlm_stat = np.std(y, dtype=np.float64)

        stat_l1_std = np.std(y[0:int(len(y) / 3)])
        stat_l2_std = np.std(y[int(len(y) / 3):2 * int(len(y) / 3)])
        stat_l3_std = np.std(y[2 * int(len(y) / 3):3 * int(len(y) / 3)])

        # plots
        data_set_label = (meas_params['date time'] + '\n' + meas_params['lens type (rx/tx)'] + meas_params['barcodes']
                          + ', SW: ' + meas_params['acu_version'] + '\n ITCC: ' + meas_params['itcc_runner_version'])

        # plot 1
        min_y = -30
        max_y = 60
        axs[0, 0].vlines(length_y_over_3, min_y, max_y, 'k', alpha=0.2)
        axs[0, 0].vlines(2 * length_y_over_3, min_y, max_y, 'k', alpha=0.2)
        axs[0, 0].text(0.8 * length_y_over_6, min_y + 5, 'Lens 1', backgroundcolor='r', fontsize=20)
        axs[0, 0].text(2.8 * length_y_over_6, min_y + 5, 'Lens 2', backgroundcolor='g', fontsize=20)
        axs[0, 0].text(4.8 * length_y_over_6, min_y + 5, 'Lens 3', backgroundcolor='b', fontsize=20)
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
        axs[0, 0].set_xticks([0.5 * length_y_over_3, 1 * length_y_over_3, 1.5 * length_y_over_3,
                              2 * length_y_over_3, 2.5 * length_y_over_3, 3 * length_y_over_3])
        axs[0, 0].set_xlim([1, len(y) + 1])
        axs[0, 0].set_ylim([min_y, max_y])
        axs[0, 0].grid('on')
        axs[0, 1].plot(data_set_label, stat_l1_median, 'rs')
        axs[0, 1].plot(data_set_label, stat_l2_median, 'g^')
        axs[0, 1].plot(data_set_label, stat_l3_median, 'bP')
        if '0267' in meas_params['barcodes']:
            axs[0, 1].plot(data_set_label, stat_tlm_median, 'rX', markersize=10)
        elif 'B2' in meas_params['barcodes']:
            axs[0, 1].plot(data_set_label, stat_tlm_median, 'yX', markersize=10)
        elif 'v3' in meas_params['barcodes']:
            axs[0, 1].plot(data_set_label, stat_tlm_median, 'gX', markersize=10)
        else:
            axs[0, 1].plot(data_set_label, stat_tlm_median, 'kX', markersize=10)
        rounded = round(stat_tlm_median, 1)
        axs[0, 1].text(data_set_label, stat_tlm_median + 5, rounded, fontsize=3)

        with open(r'C:\Measurements\Gain_+_SerialNo.csv', mode='w') as file:
            writer = csv.writer(file)
            writer.writerow(['Serial_Number', 'Median_Gain'])
            for value in barcode_num:
                writer.writerow([value])
            for value in stat_tlm_median_log:
                writer.writerow(['', value])

        axs[0, 1].set_xlabel('board')
        axs[0, 1].set_ylabel('Median [dB]')
        axs[0, 1].tick_params(axis='x', labelrotation=90, labelsize=board_font)
        axs[0, 1].set_ylim([min_y, max_y])
        axs[0, 1].grid('on')
        # plot 3
        axs[1, 1].plot(data_set_label, stat_l1_std, 'rs')
        axs[1, 1].plot(data_set_label, stat_l2_std, 'g^')
        axs[1, 1].plot(data_set_label, stat_l3_std, 'bP')
        axs[1, 1].plot(data_set_label, stat_tlm_stat, 'kX', markersize=10)
        axs[1, 1].set_xlabel('board')
        axs[1, 1].set_ylabel(r'$\sigma$ [dB]')
        axs[1, 1].tick_params(axis='x', labelrotation=90, labelsize=board_font)
        axs[1, 1].set_ylim([0, 20])
        axs[1, 1].grid('on')
        # plot 4
        if stat_l1_dropped + stat_l2_dropped + stat_l3_dropped > 50:
            axs[2, 1].plot(data_set_label, 5.0, 'rX', markersize=30)
        axs[2, 1].plot(data_set_label, stat_l1_dropped, 'rs')
        axs[2, 1].plot(data_set_label, stat_l2_dropped, 'g^')
        axs[2, 1].plot(data_set_label, stat_l3_dropped, 'bP')
        axs[2, 1].set_xlabel('board')
        axs[2, 1].set_ylabel('Number of dropped ports (gain < ' + str(dropped_thresh) + ' dB)')
        axs[2, 1].text(data_set_label, 2.0, log)  # bug
        axs[2, 1].tick_params(axis='x', labelrotation=90, labelsize=board_font)
        axs[2, 1].set_ylim([0, 10])
        axs[2, 1].grid('on')
        # plot 5
        y = meas_array[:, col + 1]
        length_y_over_3 = int(len(y) / 3)
        length_y_over_6 = int(len(y) / 6)
        min_y = -90
        max_y = 360 + 45
        axs[1, 0].vlines(length_y_over_3, min_y, max_y, 'k', alpha=0.2)
        axs[1, 0].vlines(2 * length_y_over_3, min_y, max_y, 'k', alpha=0.2)
        axs[1, 0].text(0.8 * length_y_over_6, min_y + 35, 'Lens 1', backgroundcolor='r', fontsize=20)
        axs[1, 0].text(2.8 * length_y_over_6, min_y + 35, 'Lens 2', backgroundcolor='g', fontsize=20)
        axs[1, 0].text(4.8 * length_y_over_6, min_y + 35, 'Lens 3', backgroundcolor='b', fontsize=20)
        axs[1, 0].plot(np.linspace(1, len(y), num=len(y)), y, 'k', alpha=0.2)
        axs[1, 0].set_xlabel('port')
        axs[1, 0].set_ylabel('Phase [deg]')
        axs[1, 0].set_xlim([1, len(y) + 1])
        axs[1, 0].set_ylim([min_y, max_y])
        axs[1, 0].set_yticks(np.linspace(0, 360, num=int(360 / 45) + 1))
        axs[1, 0].set_xticks([0.5 * length_y_over_3, 1 * length_y_over_3, 1.5 * length_y_over_3,
                              2 * length_y_over_3, 2.5 * length_y_over_3, 3 * length_y_over_3])
        axs[1, 0].grid('on')

        # out
        return y, y_gain, stat_tlm_median, mask_gain
    else:
        return None


def run_eval_cal_check():
    plt.rcParams['font.size'] = 12
    plt.close('all')
    input_folder = r"C:\input\Test_Folder_Calibration"

    # params for notebook?
    temperature = '45'
    measurement_type = "Calibration"  # or 'Evaluation'
    meas_file_path = r"C:\input\Test_Folder_Calibration"
    save_file_name = 'Post_Processed_Data_OP'
    mask_lim_variable = []
    external_folder_name = "Figures"
    meas_file_shift = 0
    dropped_thresh = 0
    exempt_folders = ['Archive', 'combiner']
    file_type = 'OP'

    tlm_type = 'Tx'  # kym read this from test_info file?

    # frequencies to iterate through
    if tlm_type == 'Tx':
        mask_lim_variable = [5]
    if tlm_type == 'Rx':
        mask_lim_variable = [5]
    if measurement_type == 'Evaluation' and tlm_type == 'Tx':
        mask_filepath = os.path.join(input_folder,
                                     r'2023_09_22_Sweep_FF_calibration_data_LensA_Sim_HFSS_ES2iXS_perf_eval_stackup_'
                                     r'Cluster_freq_change_sorted_Edit.csv')
        set_frequencies = [29.5]
        dropped_thresh_list = [dropped_thresh]
    elif measurement_type == 'Calibration' and tlm_type == 'Tx':
        mask_filepath = os.path.join(input_folder,
                                     r'2023_06_07_Sweep_Discrete_7pts_calibration_data_ES2_TX_TLM_Lens1_cal_equ_FR_'
                                     r'Norm_renormalization_of_ports.csv')
        set_frequencies = [27.5, 28.0, 28.5, 29.0, 29.5, 30.0, 30.5, 31.0]
        dropped_thresh_list = [3, 10, 10, 7, 7, 7, 7, 0]
    elif measurement_type == 'Evaluation' and tlm_type == 'Rx':
        mask_filepath = os.path.join(input_folder,
                                     r'2023_10_31_discrete_17700_21200_8_calibration_data_175-0212_sanmina_rel1c_'
                                     r'2023_perf_eval_sorted.csv')
        set_frequencies = [19.2]
        dropped_thresh_list = [0]
    elif measurement_type == 'Calibration' and tlm_type == 'Rx':
        mask_filepath = os.path.join(input_folder,
                                     r'2023_03_17_discrete_17700_21200_8_calibration_data_175-0081_sanmina_rel1c_2023_'
                                     r'03_07_L1L14_48feed_calibration_13mm_dual_pol_probe_2.csv')
        set_frequencies = [17.70]  # [17.70, 18.20, 18.70,19.20, 19.70, 20.20, 20.70, 21.20]
        dropped_thresh_list = [10, 15, 15, 15, 15, 15, 15, 10]
    else:
        raise ValueError(f"Unknown configuration: measurement_type={measurement_type}', tlm_type={tlm_type}")

    y = None
    y_gain = None
    mask_gain = None
    stat_tlm_median = None
    mask_data = load_mask_from_file(mask_filepath)

    # run
    for beam in range(1, 3):
        # Find all meas files for this beam
        meas_files = find_meas_files(meas_file_path, file_type, beam, exempt_folders)

        for f_set_index, f_set in enumerate(set_frequencies):
            dropped_thresh = dropped_thresh_list[f_set_index]
            fig, axs = plt.subplots(3, 2, figsize=(25, 15))
            stat_tlm_median_log = []
            barcode_num = []
            y_gain_log = []
            tlm_log = []
            for meas_file_index in range(len(meas_files) - meas_file_shift):
                # load meas file
                if f"_{temperature}C" in meas_files[meas_file_index]:
                    measurement_array, measurement_frequencies, measurement_params = load_meas_files(
                        meas_files[meas_file_index])

                    # plot
                    if '.' in measurement_params['acu_version']:
                        print('-------------------------------------')
                        print(measurement_params['date time'][1:])
                        print(measurement_params['barcodes'])
                        print('Temperature = ' + measurement_params['Temp. [°C]'])
                        print('-------------------------------------')
                        suptitle = f"{measurement_type}: {f_set} GHz, Beam {beam}, {temperature} degC"
                        plot_data = plot_gain_v_port(f_set, measurement_array, measurement_frequencies,
                                                     measurement_params, tlm_type, fig, axs, suptitle,
                                                     stat_tlm_median_log, barcode_num, dropped_thresh, mask_data)
                        # colate
                        if plot_data is not None:
                            y, y_gain, stat_tlm_median, mask_gain = plot_data
                            y_gain_log.append(y_gain)
                            tlm_log.append(measurement_params['barcodes'])

            # mask
            mask_gain = get_mask_for_frequency(mask_data, f_set, 0.0)
            mask_offset = np.median(np.array(stat_tlm_median_log)) - np.median(np.array(mask_gain))
            axs[0, 0].plot(np.linspace(1, len(mask_gain), num=len(mask_gain)), mask_gain + mask_offset, 'g-', alpha=0.5)
            axs[0, 0].fill_between(
                np.linspace(1, len(mask_gain), num=len(mask_gain)), mask_gain + mask_offset - mask_lim_variable,
                mask_gain + mask_offset + mask_lim_variable, color='green', alpha=0.2)

            # plot histogram
            ymax1 = 25.0
            mean = np.mean(np.array(stat_tlm_median_log))

            axs[2, 0].hist(np.array(stat_tlm_median_log), bins=11)
            axs[2, 0].set_xlabel('TLM median [dB]')
            axs[2, 0].set_ylabel('count')
            axs[2, 0].set_xlim([mean - 5, mean + 5])
            axs[2, 0].set_ylim([0, 25])
            axs[2, 0].axvline(mean, ymin=0.0, ymax=ymax1, color='k')
            axs[2, 0].grid('on')
            variance = np.var(np.array(stat_tlm_median_log))
            sigma = np.sqrt(variance)
            x = np.linspace(-50, 50, 10001)
            axs[2, 0].plot(x, ymax1 * norm.pdf(x, mean, sigma) / (max(norm.pdf(x, mean, sigma))), 'r')
            axs[2, 0].text(mean + 0.1, 10.25, str(round(mean, 2)) + r" dB ($\sigma$ = "
                           + str(round(sigma, 1)) + ')', rotation=90)

            # mask_check
            tlm_numbers = []
            for jj, y_gain in enumerate(y_gain_log):
                delta = y_gain - (mask_gain + mask_offset)
                if max(abs(delta)) > mask_lim_variable:
                    print('TLMs_in_List:', tlm_log[jj])
                    for _ in range(len(tlm_log)):
                        tlm_numbers.append(len(tlm_log))
                        tlm_numbers = list(set(tlm_numbers))
                        axs[0, 1].text(0, stat_tlm_median - 35, 'Total_Number_of_TLMs: ' + str(tlm_numbers))

                    for i in range(len(delta)):
                        if abs(delta[i]) > mask_lim_variable:
                            axs[0, 0].plot(i + 1, y_gain_log[jj][i], 'ro', markersize=1)

            # format
            plt.tight_layout()

            # save
            image_file_name = measurement_type + '_f-set' + str(f_set) + '_b' + str(beam) + '.png'
            new_path = os.path.join(meas_file_path, save_file_name)
            if not os.path.exists(new_path):
                os.makedirs(new_path)
            image_file_path = os.path.join(new_path, image_file_name)
            plt.savefig(image_file_path, dpi=200)

    external_path = os.path.join(meas_file_path, external_folder_name)
    os.makedirs(external_path, exist_ok=True)  # Create external folder if it doesn't yet exist

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


run_eval_cal_check()
