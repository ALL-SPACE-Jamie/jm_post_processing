%% Opens all .mat files from a given directory and finds the ones with the
%% same names in the second directory and compares
close all

% define file paths
file_path_1 = 'C:\scratch\20240620\R251';
file_path_2 = 'C:\scratch\20240620\C251';

% find files in file paths
cd(file_path_1);
files_1 = dir('**/*.mat');
cd(file_path_2);
files_2 = dir('**/*.mat');

% set-up lists
phase_average = [];
gain_average = [];
count_log = [];

% loop through and compare
for idx = (1:length(files_2))
    tc_compare(append(files_1.folder, '\', files_1.name), append(files_2(idx).folder, '\', files_2(idx).name));
    phase_average(idx) = phase_mean;
    gain_average(idx) = gain_mean;
    count_log(idx) = count;
end


%% Functions %%

%% comparison_structure
%% function for comparing the TC structures
function [TC_1, TC_2] = tc_compare(TC_1_fpath, TC_2_fpath)

% load the TC structures
TC_1 = load(TC_1_fpath);
TC_2 = load(TC_2_fpath);
comparison_str = append(TC_1.TC.T.SW_Versions.data.x3, '(', datestr(TC_1.TC.Exe_StartTime), ') | ', TC_2.TC.T.SW_Versions.data.x3, '(', datestr(TC_2.TC.Exe_StartTime), ')');

% intialise
figure
plot_count = 1;

% compare
txrxb1b2_fields = fieldnames(TC_1.TC.TestArray);
perc_log_gain = [];
perc_log_phase = [];
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
    
                    %tf = isequaln(TC_2,TC_1);
    
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
    end
    
    txrxb1b2 = string(txrxb1b2_fields{txrxb1b2_idx});
    
    % gain diff plot
    subplot(2,4,plot_count)
    spread = max(val_list_attn) - min(val_list_attn);
    if spread == 0
        bar_col = 'green';
    else
        bar_col = 'red';
    end
    histogram(val_list_attn, 'FaceColor', bar_col)
    perc = round(100*sum(val_list_attn(:)==0)/length(val_list_attn),2);
    perc_log_gain = [perc_log_gain, perc];
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
    perc = round(100*sum(val_list_phase(:)==0)/length(val_list_phase),2);
    perc_log_phase = [perc_log_phase, perc];
    xlabel('Phase diff');
    ylabel('count');
    %set(gca,'YScale','log');
    %ylim([0.1 1000000]);
    title(append(TC_1.TC.UUT.TestDescription, ': ', datestr(TC_1.TC.Exe_StartTime), newline, 'SW-', TC_1.TC.T.SW_Versions.data.x3, newline, TC_2.TC.UUT.TestDescription, ': ', datestr(TC_2.TC.Exe_StartTime), newline, 'SW-', TC_2.TC.T.SW_Versions.data.x3, newline, txrxb1b2, newline, 'N = ', num2str(length(val_list_attn)), ', ', num2str(perc), '%'), 'Interpreter', 'none');
      
    plot_count = plot_count + 1;

end

% report
phase_mean = mean(perc_log_phase);
gain_mean = mean(perc_log_gain);
count = TC_2.TC.Options.pause_before_AP;
assignin('base', 'phase_mean', phase_mean);
assignin('base', 'gain_mean', gain_mean);
assignin('base', 'count', count);

end

% figure
% plot(count_log, gain_average, 'o-', 'DisplayName', 'gain'); hold on
% plot(count_log, phase_average, '^-', 'DisplayName', 'phase');
% xlabel('pause [s]');
% ylabel('average similarity');
% xlim([0 1])
% ylim([99.8 100.2])
% legend


