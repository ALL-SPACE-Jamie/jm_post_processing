# -*- coding: utf-8 -*-
"""
Created on Thu Dec 21 18:49:37 2023

@author: jmitchell
desc: Analysis of a batch of TLMs.
"""
from FileImporter import ImportRFA
from BatchAnalyse import AnalyseBatch

# import files
RFA_obj = ImportRFA(file_path='C:\fff')
test = ImportRFA.testDef(RFA_obj, inVar=6.0)
meas_files = ImportRFA.load_RFA_files(RFA_obj, r'C:\Users\jmitchell\Downloads\rfas\rfas', 'RFA', 1)

# analyse files
Analyse_obj = AnalyseBatch(r'ggg')
Exempt_Folder, f_set_list, droppedThreshList, measFileShift, measType = AnalyseBatch.setup(Analyse_obj, '45', 'Rx', 'Evaluation', 
                                   r'C:\Users\jmitchell\Downloads\Raw_Data', 
                                   r'\Post_Processed_Data', '6', 0, [], 
                                   r'C:\Users\jmitchell\Downloads\rfas\rfas\extFolder', 
                                   0, 0, 'combiner')

Analyse_find_measFiles = AnalyseBatch.find_measFiles(Analyse_obj, r'C:\Users\jmitchell\Downloads\Raw_Data', r'OP_', 1, Exempt_Folder)







import matplotlib.pyplot as plt
measFiles = Analyse_find_measFiles[0]

files = Analyse_find_measFiles[1]








# run
for p in range(2):
    beam = p + 1
    for l in range(len(f_set_list)):
        f_set = f_set_list[l]
        droppedThresh = droppedThreshList[l]

        # find all meas files
        # find_measFiles(filePath, 'OP', beam)

        fig, axs = plt.subplots(3, 2, figsize=(25, 15))
        stat_TLM_median_log = []
        y_gain_log = []
        tlm_log = []
        for k in range(len(measFiles) - measFileShift):
            print(range(len(files)))
            # load meas file
            if '_4' in measFiles[k]:  # if str(temperature) + 'C' in measFiles[k]:
                meas_info, meas_array, meas_frequencies, meas_params = AnalyseBatch.load_measFiles(Analyse_obj, measFiles[k])
                print('-------------------------------------')
                print(meas_params['date time'][1:])
                print(meas_params['barcodes'])
                print('Temperature = ' + meas_params['Temp. [°C]'])
                print('-------------------------------------')

                # plot
                if '.' in meas_params['acu_version']:
                    # plot__gainVpor6t(f_set, measType)
                    Analyse_plot_gainVport = AnalyseBatch.plot__gainVport(f_set, Analyse_setup[4], fig, p, meas_params['Temp. [°C]'], Analyse_load_measFiles[3], meas_array, meas_frequencies)
                    # colate
                    if Analyse_plot_gainVport == True:
                        y_gain_log.append(y_gain)
                        tlm_log.append(meas_params['barcodes'])

        # mask
        import_mask(f_set, mask, 0.0)
        mask_lim = mask_lim_variable
        mask_offset = np.median(np.array(stat_TLM_median_log)) - np.median(np.array(mask_gain))
        axs[0, 0].plot(np.linspace(1, len(mask_gain), num=len(mask_gain)), mask_gain + mask_offset, 'g-', alpha=0.5)
        axs[0, 0].fill_between(np.linspace(1, len(mask_gain), num=len(mask_gain)), mask_gain + mask_offset - mask_lim, mask_gain + mask_offset + mask_lim, color='green', alpha=0.2)


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
        for jj in range(len(y_gain_log)):
         delta = y_gain_log[jj] - (mask_gain + mask_offset)
         if max(abs(delta)) > mask_lim:
                print(tlm_log[jj])
                for i in range(len(delta)):
                    if abs(delta[i]) > mask_lim:
                        axs[0, 0].plot(i + 1, y_gain_log[jj][i], 'ro', markersize=1)
                        #axs[0,0].gcf().gca().add_artist(plt.Circle(i+1, y_gain_log[jj][i], radius = 1, edgecolor='red', facecolor=0.5))
                        #axs[0, 0].text(i+1, y_gain_log[jj][i], str(tlm_log[jj]) + ': port ' + str(i+1), fontsize = 5)


        # format
        plt.tight_layout()

        # save
        fileName = measType + '_f-set' + str(f_set) + '_b' + str(beam) + '.png'
        newPath = filePath + SaveFileName
        if not os.path.exists(newPath):
            os.makedirs(newPath)
        plt.savefig(newPath + '/' + fileName, dpi=200)

external_path = os.path.join(filePath, external_folder_name)
os.makedirs(external_path, exist_ok=True)  # The path of the external folder

for dirpath, dirnames, filenames in os.walk(filePath):
    for file in filenames:
        if 'f-set' in file.lower():
            try:
                file_path = os.path.join(dirpath, file)
                shutil.copy(file_path, external_path)
                print(f"Copied_file_path_to_external_path")
            except shutil.SameFileError as e:
                print(f"Skipped copying file{file}:{e}")
print("Done.")