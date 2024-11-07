%% Script to measure the power detectors over a spacial grid, power cycle
%% and repeat.
rail = 7
error_flag = false
temp = false
power_cycle = true

pauses = [0.75 0.75 0.5 0.5 0.25 0.25 0.125 0.125 0.1 0.1 0.075 0.075 0.05 0.05 0.025 0.025 0.01 0.01 0.0 0.0]

for i = 1:length(pauses)
    clear TC
    pause_jm = 

    %% run get AP
    sprintf('Start')
    terminal_T2T_GetAPs_S2000_Sn_v2_forEdit
    pause(2*60)
    sprintf('Finished GetAPs')
    % Note: TC.Options.GetTLMCalcData=true

    d_in = TC.UUT.Results_Folder
    filename = sprintf('%s-%s-CalRun-%s.mat', TC.UUT.Name, TC.UUT.TestDescription, datestr(TC.Exe_StartTime,'yymmdd HH-MM'));


    seq_count = 1
        for pcs = [1 2 3 4 5 6]
            for tlm = [1 2 3]
                % array of theta and phi
                theta_phi = TC.TestArray.Tx_B1.PT;
                theta = [theta_phi.theta];
                phi = [theta_phi.phi];
                
                % array of zeros for the current values
                tlm_current_array = zeros(1,length(theta));
            
                % loop through the angles
                for ang = 1:length(theta)
                    tlm_powers = TC.TestArray.Tx_B1(seq_count).Status(ang).DCPowers.Tx;
                    % sw_version = TC.TestArray.Tx_B1(1).Status(1).SW_Versions.data.x3; 
                    tlm_power = tlm_powers(pcs, tlm);
                    tlm_current = [tlm_power.i];
                    if temp == false
                    tlm_current_selected = tlm_current(rail);
                    else
                    tlm_current_selected = TC.TestArray.Tx_B1(seq_count).Status(ang).pcs(pcs).Temps.Txpll_B1
                    end
                    % test_datetime = TC.TestArray.Tx_B1(seq_count).Status(seq_count).timestamp;
                    test_datetime = TC.TestArray.Tx_B1(seq_count).Status(1).timestamp;
                    tlm_current_array(1,ang) = tlm_current_selected;
                end
            
                % check for error in operation
                array_for_check = tlm_current_array(length(tlm_current_array))
                array_for_check = array_for_check(1:length(array_for_check))
                if std(array_for_check) > 0.1 || median(array_for_check) < 0.5 || median(array_for_check) > 0.8
                    label = append(datestr(test_datetime, 'dd-mm HH:MM'))%, newline,"SW: ", sw_version)
                    error_flag = true
                else
                    label = append(datestr(test_datetime, 'dd-mm HH:MM'))%, newline,"SW: ", sw_version)
                end
                sprintf('DELTA')
                % sprintf(num2str(min(tlm_current_array(length(tlm_current_array))) < 0.4))

                seq_count = seq_count + 1;
            end
    end








    % error_flag = false % negate the error search to keep running
    if error_flag == true
        sprintf('FOUND ERROR STATE!')
        % dbstop
    end

    
    %% power cycle the terminal using netio
    if power_cycle == true
        sprintf('Power down')
        socket_no = 1
        on_off = 0
        options = weboptions('RequestMethod', 'get');
        url = sprintf('http://172.16.9.151/netio.cgi?pass=admin&output%d=%d',socket_no, on_off)
        webread(url, options)
        
        pause(1*60)
        
        sprintf('Power up')
        on_off = 1
        options = weboptions('RequestMethod', 'get');
        url = sprintf('http://172.16.9.151/netio.cgi?pass=admin&output%d=%d',socket_no, on_off)
        webread(url, options)
    
        pause(5*60)
    end
end

sprintf('Loop finished')



