%% Opens all .mat files from a given directory and finds the ones with the
%% same names in the second directory and compares
close all

% define file paths
file_path_1 = 'C:\scratch\20240520\2_1_2_v0';
file_path_2 = 'C:\scratch\20240520\2_1_2_v1';

% find files in file paths
cd(file_path_1);
files_1 = dir('**/*.mat');
cd(file_path_2);
files_2 = dir('**/*.mat');

% loop through files in first folder and find the files in the second
% folder
for idx_1 = (1:length(files_1))
    name_1 = files_1(idx_1).name(1:26);
    for idx_2 = (1:length(files_2))
        name_2 = files_2(idx_2).name;
        if contains(name_2, name_1) == true
            files_1(idx_1).comp = files_2(idx_2).name;
            files_1(idx_1).comp_folder = files_2(idx_2).folder;
        end
    end
end

% loop through and compare
for idx = (1:length(files_1))
    if length(files_1(idx).comp) > 0
        tc_compare(append(files_1(idx).folder, '\', files_1(idx).name), append(files_1(idx).comp_folder, '\', files_1(idx).comp));
    end
end


%% Functions %%

%% comparison_structure
%% function for comparing the TC structures
function [TC_1, TC_2] = tc_compare(TC_1_fpath, TC_2_fpath)

% load the TC structures
TC_1 = load(TC_1_fpath);
TC_2 = load(TC_2_fpath);
comparison_str = append(TC_1.TC.T.SW_Versions.data.x3, '(', datestr(TC_1.TC.Exe_StartTime), ') | ', TC_2.TC.T.SW_Versions.data.x3, '(', datestr(TC_2.TC.Exe_StartTime), ')')

% intialise
figure
plot_count = 1;

% compare
txrxb1b2_fields = fieldnames(TC_1.TC.TestArray);
for txrxb1b2_idx = 1:length(txrxb1b2_fields)
    val_list_attn = [];
    val_list_phase = [];
    entry = 1;
    for tlm = 1:18
        for ang = 1:length(TC_1.TC.TestArray.Tx_B1(1).AP_at_MP)
            for lens = 1:3
                for patch = 1:4
                    TC_1_val = TC_1.TC.TestArray.(txrxb1b2_fields{txrxb1b2_idx})(tlm).AP_at_MP(ang).Lens(lens).Patch(patch).Port;
                    TC_2_val = TC_2.TC.TestArray.(txrxb1b2_fields{txrxb1b2_idx})(tlm).AP_at_MP(ang).Lens(lens).Patch(patch).Port;
    
                    tf = isequaln(TC_2,TC_1);
    
                    TC_1_Phase = cell2mat({TC_1_val.Phase});
                    TC_2_Phase = cell2mat({TC_2_val.Phase});
                    TC_1_Attn = cell2mat({TC_1_val.Attn});
                    TC_2_Attn = cell2mat({TC_2_val.Attn});
    
                    Phase_diff = TC_1_Phase - TC_2_Phase;
                    Attn_diff = TC_1_Attn - TC_2_Attn;
    
                    val_list_attn(entry) = Attn_diff(1);
                    val_list_attn(entry+1) = Attn_diff(2);
                    val_list_phase(entry) = Phase_diff(1);
                    val_list_phase(entry+1) = Phase_diff(2);
                    entry = entry+2;
                end
            end
        end
        test = 'test3'
    end
    
    txrxb1b2 = string(txrxb1b2_fields{txrxb1b2_idx})
    
    % gain diff plot
    subplot(2,4,plot_count)
    spread = max(val_list_attn) - min(val_list_attn);
    if spread == 0
        bar_col = 'green';
    else
        bar_col = 'red';
    end
    histogram(val_list_attn, 'FaceColor', bar_col)
    perc = round(100*sum(val_list_attn(:)==0)/length(val_list_attn),2)
    xlabel('Attn diff');
    ylabel('count');
    %set(gca,'YScale','log');
    %ylim([0.1 1000000]);
    title(append(TC_1.TC.UUT.TestDescription, ': ', datestr(TC_1.TC.Exe_StartTime), newline, 'SW-', TC_1.TC.T.SW_Versions.data.x3, newline, TC_2.TC.UUT.TestDescription, ': ', datestr(TC_2.TC.Exe_StartTime), newline, 'SW-', TC_2.TC.T.SW_Versions.data.x3, newline, txrxb1b2, newline, 'N = ', num2str(length(val_list_attn)), ', ', num2str(perc), '%'), 'Interpreter', 'none');
    
    % phase diff plot
    subplot(2,4,plot_count+4)
    spread = max(val_list_phase) - min(val_list_phase);
    if spread == 0
        bar_col = 'green';
    else
        bar_col = 'red';
    end
    histogram(val_list_phase, 'FaceColor', bar_col)
    perc = round(100*sum(val_list_phase(:)==0)/length(val_list_phase),2)
    xlabel('Phase diff');
    ylabel('count');
    %set(gca,'YScale','log');
    %ylim([0.1 1000000]);
    title(append(TC_1.TC.UUT.TestDescription, ': ', datestr(TC_1.TC.Exe_StartTime), newline, 'SW-', TC_1.TC.T.SW_Versions.data.x3, newline, TC_2.TC.UUT.TestDescription, ': ', datestr(TC_2.TC.Exe_StartTime), newline, 'SW-', TC_2.TC.T.SW_Versions.data.x3, newline, txrxb1b2, newline, 'N = ', num2str(length(val_list_attn)), ', ', num2str(perc), '%'), 'Interpreter', 'none');
      
    plot_count = plot_count + 1;

end

end