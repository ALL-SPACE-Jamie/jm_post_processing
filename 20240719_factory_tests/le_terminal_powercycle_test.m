%% Script to measure the power detectors over a spacial grid, power cycle
%% and repeat.
error_flag = false
temp = false
power_cycle = true

pauses = [0.0]

for i = 1:length(pauses)
    clear TC
    pause_jm = pauses(i)

    %% run get AP
    sprintf('Start')
    terminal_T2T_GetAPs_S2000_Sn_v2_forEdit
    pause(2*60)
    sprintf('Finished GetAPs')
    
    %% power cycle the terminal using netio
    if power_cycle == true
        sprintf('Power down')
        socket_no = 3
        on_off = 0
        options = weboptions('RequestMethod', 'get');
        url = sprintf('http://172.16.10.127/netio.cgi?pass=admin&output%d=%d',socket_no, on_off)
        webread(url, options)
        
        pause(1*60)
        
        sprintf('Power up')
        on_off = 1
        options = weboptions('RequestMethod', 'get');
        url = sprintf('http://172.16.10.127/netio.cgi?pass=admin&output%d=%d',socket_no, on_off)
        webread(url, options)
    
        pause(5*60)
    end
end

sprintf('Loop finished')



