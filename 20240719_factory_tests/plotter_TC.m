%% Script for plotting TCs

% loop through rails
for rail = [7] % rail = 7 % 5, 6, 7 = C, B, A
    lens = 1
    close all
    clearvars -except rail lens
    temp = false
    error_flag = false
    % params
    terminal = "I15"

    % make a figure
    figure
    
    % directories you have the mat files
    d_log = {append('C:\getAP\', terminal, '\Cal\T2T_PS\APData_Check\analysis\')
        }
    
    % loop though sets of measurements as the files are too big for struc
    errors = cell(1,1000);
    error_count = 0
    for d = [d_log(1)]% d_log(2) d_log(3) d_log(4) d_log(5) d_log(6) d_log(7)]% d_log(8)]
    
        % list of the files
        files = dir(fullfile(d{1}, '*.mat'));
        run_l = length(files)
        
        % superstructure of TCs
        for run = 1:run_l
            file = [files(run).folder '\' files(run).name]
            struc_temp = load(file);
            TA(run) = {struc_temp.TC.TestArray.Tx_B1};
        end
        
        % loop through pcs
        seq_count = 1;
        for tlm = [1 2 3]
        
            % loop through tlms
            for pcs = [6 5 4 3 2 1]
            
                % loop through the files (i.e. the tests)
                for run = 1:run_l
                
                    % hold on to whatever is in your figure
                    hold on
                
                    % load the file
                    file = [files(run).folder '\' files(run).name]
                
                    % array of theta and phi
                    theta_phi = TA{1,run}.PT;
                    theta = [theta_phi.theta];
                    phi = [theta_phi.phi];
                    
                    % array of zeros for the current values
                    tlm_current_array = zeros(1,length(theta));
                    patches_active = string(zeros(1,length(theta)));
                    failures = string(zeros(1,length(theta)));
                
                    % loop through the angles
                    for ang = 1:length(theta)
                        tlm_powers = TA{1,run}(seq_count).Status(ang).DCPowers.Tx;
                        %sw_version = TA{1, run}(1).Status(1).SW_Versions.data.x3; 
                        tlm_power = tlm_powers(pcs, tlm);
                        tlm_current = [tlm_power.i];
                        if temp == false
                        tlm_current_selected = tlm_current(rail);
                        else
                        tlm_current_selected = TA{1, run}(seq_count).Status(ang).pcs(pcs).Temps.Txpll_B1;
                        end
                        test_datetime = TA{1,run}(seq_count).Status.timestamp;
                        tlm_current_array(1,ang) = tlm_current_selected;
                        patches = [TA{1,run}(seq_count).AP_at_MP(ang).Lens(lens).Patch.Number];
                        patches = num2str(patches(1:4));
                        patches_active(1,ang) = patches;
                    end

                    % check for error in operation
                    if max(tlm_current_array) - min(tlm_current_array) > 0.15
                        label = append(datestr(test_datetime, 'dd-mm HH:MM'))%, newline,"SW: ", sw_version);
                        error_flag = true;
                    else
                        label = append(datestr(test_datetime, 'dd-mm HH:MM'))%, newline,"SW: ", sw_version);
                    end
                
                    % cartesian plot
                    subplot(6,3,seq_count)
                    array_for_check = tlm_current_array(length(tlm_current_array))
                    array_for_check = array_for_check(1:length(array_for_check))
                    if std(array_for_check) > 0.1 || median(array_for_check) < 0.5 || median(array_for_check) > 0.8
                        plot([tlm_current_array'],'--x','LineWidth',2,'DisplayName',label)
                        sprintf(append('FAILURE:', 'PCS-', int2str(pcs), ' TLM-', int2str(tlm), ', ', label))
                        errors{error_count+1} = (append('FAILURE:', 'PCS-', int2str(pcs), ' TLM-', int2str(tlm), ', ', label))
                        error_count = error_count+1
                    else
                        plot([tlm_current_array'],'-','LineWidth',2,'DisplayName',label);
                    end
                    xlabel('Pointing direction (igloo point)');
                    xlabel(append('Active patches (lens ', num2str(lens), ')'));
                    xlim([0 length(theta)]);
                    xticks(linspace(1,length(theta),length(theta)));
                    xticklabels(append('th-', string(theta), ' phi-', string(phi)));
                    xticklabels(patches_active);
                    if temp == false
                    ylim([0 1.5]);
                    ylabel('I [A]');
                    else
                    ylim([0 80])
                    ylabel('T [degC]');
                    end
                    
                end
                
                % figure format
                set(gcf,'Position',[50 50 1800 900]);
                tlm_name = append('PCS-', int2str(pcs), ' TLM-', int2str(tlm))
                title(tlm_name);
                grid on;
                % legend('NumColumns',5,'FontSize',2, 'Location','EastOutside');
                a = get(gca,'XTickLabel');  
                set(gca,'XTickLabel',a,'fontsize',6)
                
                seq_count = seq_count + 1;
            end
        
        end
    end
    
    if rail == 7
        rail_letter = 'A'
    elseif rail == 6
        rail_letter = 'B'
    elseif rail == 5
        rail_letter = 'C'
    end

    
    title=append(terminal, " 4V-", rail_letter);
    Lgnd = legend('show', 'NumColumns', 2);
    Lgnd.Position(1) = 0.00;
    Lgnd.Position(2) = 0.3;
    sgtitle(title)
    exportgraphics(gcf,append(d{1}, append(title, '.png')),'Resolution',300)
end
