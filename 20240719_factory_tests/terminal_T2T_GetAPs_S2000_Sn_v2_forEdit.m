%% Initialise the Test & Cal Object

terminal = 'I12';  
datapath = 'C:\getAP_pc\';
testSubFolder = 'APData_Check';

Beams = [1 2];

for num_patch=[4];


%% Freqs
pnts=uniformAngularGrid(70,14);
% pnts=uniformAngularGrid(0,14);

%% CalSet
    Tconfigs=struct( ...
        'Freq_Rx',{  17.7 18.3 18.7 19.3 19.7 20.1 20.7 21.1 17.7 18.3 18.7 19.3 19.7 20.1 20.7 21.1}, ...
        'Freq_Tx',{  27.55 27.95 28.550 28.950 29.550 29.95 30.55 30.95 27.55 27.95 28.550 28.950 29.550 29.95 30.55 30.95},    ...
        'Pol_Rx',{  'LHCP' 'LHCP' 'LHCP' 'LHCP' 'LHCP' 'LHCP' 'LHCP' 'LHCP' 'RHCP' 'RHCP' 'RHCP' 'RHCP' 'RHCP' 'RHCP' 'RHCP' 'RHCP' }, ...
        'Pol_Tx',{  'LHCP' 'LHCP' 'LHCP' 'LHCP' 'LHCP' 'LHCP' 'LHCP' 'LHCP' 'RHCP' 'RHCP' 'RHCP' 'RHCP' 'RHCP' 'RHCP' 'RHCP' 'RHCP' }, ...
        'Points',{ pnts pnts pnts pnts pnts pnts pnts pnts pnts pnts pnts pnts pnts pnts pnts pnts},...
        'Beam',{  Beams Beams Beams Beams Beams Beams Beams Beams Beams Beams Beams Beams Beams Beams Beams Beams} ...
        );

for ti= 1 %1:length(Tconfigs) %13 14 3 4 21 22 17 18 5 6 7 8 9 10 11

    Tconfig=Tconfigs(ti)
    %%Freq Loop

    for ccf=[ 0 ]  % 

            newTC=true;
            TC = TestCal_Routine;

            TC.UUT.Name            = terminal;
            TC.UUT.TestDescription = convertStringsToChars(sprintf("T2T_%0.2f%s_%0.2f%s", Tconfig.Freq_Rx, Tconfig.Pol_Rx, Tconfig.Freq_Tx, Tconfig.Pol_Tx));
            TC.UUT.TestDescription = strrep(TC.UUT.TestDescription,'.','g');
            TC.UUT.Results_Folder  = [datapath terminal '\Cal\T2T_PS\'  testSubFolder];

            if ~exist(TC.UUT.Results_Folder, 'dir')
                mkdir(TC.UUT.Results_Folder);
            end

            filename = sprintf('%s-%s-LOG-%s.txt', TC.UUT.Name, TC.UUT.TestDescription, datestr(datetime('now'),'yymmdd HH-MM'));
            diary (fullfile(TC.UUT.Results_Folder,filename))

            TC.Layout='S2000_Mk1_Lens_Layout.mat';
            TC.attach_terminal(terminal,'Gen','Mk1','Layout',TC.Layout, 'PSU_IP','none');

            %     TC.attach_terminal(TC.UUT.Name,'Gen','Mk1');
    TC.attach_chamber('None','usePositioner',false); %CATR

    if TC.Gen=='Mk1'
        TC.T.setconfig('System.TLM.UseCombinerPointingCalibrationLookUpTables',0);
    else
        TC.T.setconfig('UseCombinerPointingCalibrationLookUpTables',0);
    end

            TC.T.setTLMNormMode('Mode','Off','TxRx', 'Rx');
            TC.T.setTLMNormMode('Mode','Off','TxRx', 'Tx');
            TC.T.setTLMCompMode('Mode','Off','TxRx', 'Tx');
            TC.T.setTLMCompMode('Mode','Off','TxRx', 'Rx');
            TC.Options.pattern_delay=0.1;

        if ccf==0

        elseif ccf==1
            TC.T.setconfig('Beam1.TLM.Tx.Combiner.CommonAttenuation','36');
            TC.T.setconfig('Beam1.TLM.Tx.Patch.CommonAttenuation','12');
            TC.T.setconfig('Beam2.TLM.Tx.Combiner.CommonAttenuation','36');
            TC.T.setconfig('Beam2.TLM.Tx.Patch.CommonAttenuation','12');
    
            TC.T.setconfig('Beam1.TLM.Rx.Combiner.CommonAttenuation','36');
            TC.T.setconfig('Beam1.TLM.Rx.Patch.CommonAttenuation','36');
            TC.T.setconfig('Beam2.TLM.Rx.Combiner.CommonAttenuation','36');
            TC.T.setconfig('Beam2.TLM.Rx.Patch.CommonAttenuation','36');
    
            TC.T.setconfig('System.TLM.Tx.1PatchAtten','0');
            TC.T.setconfig('System.TLM.Tx.2PatchAtten','0');
            TC.T.setconfig('System.TLM.Tx.3PatchAtten','-4');
            TC.T.setconfig('System.TLM.Tx.4PatchAtten','-6');
            TC.T.setconfig('System.TLM.Tx.BaseAtten','3');
    
    
            TC.T.setconfig('System.TLM.Rx.1PatchAtten','0');
            TC.T.setconfig('System.TLM.Rx.2PatchAtten','0');
            TC.T.setconfig('System.TLM.Rx.3PatchAtten','0');
            TC.T.setconfig('System.TLM.Rx.4PatchAtten','0');
            TC.T.setconfig('System.TLM.Rx.BaseAtten','0');
           cc_name='No_Corr';
        elseif ccf==2
            TC.T.setconfig('Beam1.TLM.Tx.Combiner.CommonAttenuation','36');
            TC.T.setconfig('Beam1.TLM.Tx.Patch.CommonAttenuation','12');
            TC.T.setconfig('Beam2.TLM.Tx.Combiner.CommonAttenuation','36');
            TC.T.setconfig('Beam2.TLM.Tx.Patch.CommonAttenuation','12');
    
            TC.T.setconfig('Beam1.TLM.Rx.Combiner.CommonAttenuation','36');
            TC.T.setconfig('Beam1.TLM.Rx.Patch.CommonAttenuation','36');
            TC.T.setconfig('Beam2.TLM.Rx.Combiner.CommonAttenuation','36');
            TC.T.setconfig('Beam2.TLM.Rx.Patch.CommonAttenuation','36');
    
            TC.T.setconfig('System.TLM.Tx.1PatchAtten','0');
            TC.T.setconfig('System.TLM.Tx.2PatchAtten','0');
            TC.T.setconfig('System.TLM.Tx.3PatchAtten','-4');
            TC.T.setconfig('System.TLM.Tx.4PatchAtten','-6');
            TC.T.setconfig('System.TLM.Tx.BaseAtten','3');
    
            TC.T.setconfig('System.TLM.Rx.1PatchAtten','6');
            TC.T.setconfig('System.TLM.Rx.2PatchAtten','3');
            TC.T.setconfig('System.TLM.Rx.3PatchAtten','0');
            TC.T.setconfig('System.TLM.Rx.4PatchAtten','0');
            TC.T.setconfig('System.TLM.Rx.BaseAtten','0');
            cc_name='Corr1';
        elseif ccf==3     
            TC.T.setconfig('Beam1.TLM.Tx.Combiner.CommonAttenuation','36');
            TC.T.setconfig('Beam1.TLM.Tx.Patch.CommonAttenuation','12');
            TC.T.setconfig('Beam2.TLM.Tx.Combiner.CommonAttenuation','36');
            TC.T.setconfig('Beam2.TLM.Tx.Patch.CommonAttenuation','12');
    
            TC.T.setconfig('Beam1.TLM.Rx.Combiner.CommonAttenuation','36');
            TC.T.setconfig('Beam1.TLM.Rx.Patch.CommonAttenuation','36');
            TC.T.setconfig('Beam2.TLM.Rx.Combiner.CommonAttenuation','36');
            TC.T.setconfig('Beam2.TLM.Rx.Patch.CommonAttenuation','36');
    
            TC.T.setconfig('System.TLM.Tx.1PatchAtten','0');
            TC.T.setconfig('System.TLM.Tx.2PatchAtten','-2');
            TC.T.setconfig('System.TLM.Tx.3PatchAtten','-4');
            TC.T.setconfig('System.TLM.Tx.4PatchAtten','-6');
            TC.T.setconfig('System.TLM.Tx.BaseAtten','0');
    
            TC.T.setconfig('System.TLM.Rx.1PatchAtten','6');
            TC.T.setconfig('System.TLM.Rx.2PatchAtten','3');
            TC.T.setconfig('System.TLM.Rx.3PatchAtten','0');
            TC.T.setconfig('System.TLM.Rx.4PatchAtten','0');
            TC.T.setconfig('System.TLM.Rx.BaseAtten','-6');
            cc_name='Corr2';
        elseif ccf==4
            TC.T.setconfig('Beam1.TLM.Tx.Combiner.CommonAttenuation','36');
            TC.T.setconfig('Beam1.TLM.Tx.Patch.CommonAttenuation','12');
            TC.T.setconfig('Beam2.TLM.Tx.Combiner.CommonAttenuation','36');
            TC.T.setconfig('Beam2.TLM.Tx.Patch.CommonAttenuation','12');
    
            TC.T.setconfig('Beam1.TLM.Rx.Combiner.CommonAttenuation','36');
            TC.T.setconfig('Beam1.TLM.Rx.Patch.CommonAttenuation','12');
            TC.T.setconfig('Beam2.TLM.Rx.Combiner.CommonAttenuation','36');
            TC.T.setconfig('Beam2.TLM.Rx.Patch.CommonAttenuation','12');
    
            TC.T.setconfig('System.TLM.Tx.1PatchAtten','0');
            TC.T.setconfig('System.TLM.Tx.2PatchAtten','0');
            TC.T.setconfig('System.TLM.Tx.3PatchAtten','0');
            TC.T.setconfig('System.TLM.Tx.4PatchAtten','0');
            TC.T.setconfig('System.TLM.Tx.BaseAtten','-6');
    
    
            TC.T.setconfig('System.TLM.Rx.1PatchAtten','0');
            TC.T.setconfig('System.TLM.Rx.2PatchAtten','0');
            TC.T.setconfig('System.TLM.Rx.3PatchAtten','0');
            TC.T.setconfig('System.TLM.Rx.4PatchAtten','0');
            TC.T.setconfig('System.TLM.Rx.BaseAtten','-6');

            cc_name='Corr3';

        end

    TxRxS = {'Tx' 'Rx'};

    %% Define the Phi/Theta Measurement Points
    % [Points] = uniformAngularGrid(70,10);
    [Points] = Tconfig.Points;

    % dt = 2; %10; %20
    % [P1,T1] = meshgrid( [-4:dt:4], 56:dt:64 );
    % P1 = reshape(P1,[1,25]);
    % T1 = reshape(T1,[1,25]);
    % [P1,T1] = meshgrid( [0:dt:350], dt:dt:70 );

    %%%
    %%%
    figure
    % Plot the grid
    ax = gca;
    hold all
    t = 0:1:360;
    for r = 10:10:80
        x = r.*sind(t);
        y = r.*cosd(t);
        plot(ax,x,y,'-','Color',[0.9 0.9 0.9]);
    end
    r = [0 85];
    for t = 0:30:330
        x = r.*sind([t t]);
        y = r.*cosd([t t]);
        plot(ax,x,y,'-','Color',[0.9 0.9 0.9]);
    end
%     add_geo_meo_pass_to_xy_plot(ax,0);

%     load('MEOGEO_testPoints.mat');
%     ph = MEOGEO_testPoints.MinCalPoints(:,1);
%     th = MEOGEO_testPoints.MinCalPoints(:,2);

    TC.MPs.theta =  Points.theta;% [0 th'];
    TC.MPs.phi =   Points.phi;% [0 ph'];
    
    %Sort to speed up measurement
    TC.MPs=sort_MP_for_CATR(TC.MPs);

    [x,y] = phitheta2xy(TC.MPs.phi,TC.MPs.theta);
    z = x*0+0;
    plot3(ax, x,y,z,'ok');
    axis equal



    %% Define the Options for the test: Tx and/or Rx, Beam 1 and/or 2
    TC.Options.TxRx = [1 2];
    TC.Options.Beams = Beams;
    TC.Options.Parallel = true;

    % Options for the Ref/Test Phase Sweep
    TC.Options.Ref_Test_Phase_Sweep = false;
    TC.Options.phase_sweep = 0: 11.125*4 :360;
    TC.Options.Gain_Freq_i = 3;                                     % Freq to use for Gain Comparisons
    TC.Options.Max_DeltaGain = 3;                                   % Acceptable max gain between Ref & Test
    TC.Options.Max_DeltaGainToApply = 12;                           % max gain able to apply to Ref or Test
    TC.Options.Gain_check=-60;
    TC.Options.Rx_Cal_pwr_offset=10;

    TC.Options.PlotRunResults = true;
    TC.Options.SaveRunResults = true;

    TC.Options.Keep_Terminal_Pointed_to_Horn = true;   % Set to true for cal sweeps

    TC.Options.Add_Steering_Dimension = false;

    TC.Options.Apply_PhiTheta_Mask = false;
    TC.Options.RecordLogFiles = false;

    TC.Options.RunLiveCal = false;

    TC.Options.SaveEachMPResult = true;

    TC.Options.Use_BeamTracking=false;

    TC.Options.Tx_Weights(1)="Default";
    TC.Options.Tx_Weights(2)="Default";
    TC.Options.Rx_Weights(1)="Default";
    TC.Options.Rx_Weights(2)="Default";

    TC.Options.measure_patterns=false;
    TC.Options.testpause=0.1;
    TC.Options.GetTLMCalcData=false;

    TC.Options.useSigGen = false;
    TC.Options.detailed_status=true;
    TC.Options.Use_Port_Cal_Values=false;
    
    TC.Options.vnadata='SP';
    TC.Options.PNA_Averages=10;
    
    TC.Options.beamstep=10;
    TC.Options.pause_before_AP=pause_jm;


    TC.Options.ifbw=1000;


    TC.Options.APsource='Terminal';
    TC.Options.Verify=true;

    span=0.25;  %Span in GHz
    
    %% Define the TestArray

    for TxRx = TC.Options.TxRx
        for beam = TC.Options.Beams

            % Set the Ref Lens
            if TC.Options.Ref_Test_Phase_Sweep
                RefLens.TxRx = TxRx;
                RefLens.pcs = 1;
                RefLens.tlm = 1;
                RefLens.beam = beam;
                RefLens.lens = 0;
            else
                RefLens = [];
            end

            % Set the list of Test Lenses
            pcs_list = 1:6;
            tlm_list = 1:3;
            lens_list = [0];

            % Create the TestArray
            TC.create_testarray(TxRx, beam, RefLens, pcs_list, tlm_list, lens_list);

            TC.Options.Rx_Bringup_Freq=Tconfig.Freq_Rx;
            TC.Options.Tx_Bringup_Freq=Tconfig.Freq_Tx;

           
                    % Define the Frequencies
                    if TxRx==1
                        %Tx Frequencies
                        TC.Options.Tx_Freq = TC.Options.Tx_Bringup_Freq+linspace(-span/2,span/2,5);%28.64 + linspace(-0.15,+0.15,5);     %28.6:0.1:29.0; %28.0:0.1:29.5; 28.65
                        TC.Options.Tx_TerminalFreq = TC.Options.Tx_Bringup_Freq;
                        TC.Options.Tx_Cal_Pol = Tconfig.Pol_Tx;%'LHCP';
                        TC.Options.Tx_Test_Power=-45;
                    else
                        % Rx Frequencies
                        TC.Options.Rx_Freq = TC.Options.Rx_Bringup_Freq+linspace(-span/2,span/2,5); %18.75 + linspace(-0.15,+0.15,5); %18.6:0.1:19.0; %18.8 nom;
                        TC.Options.Rx_TerminalFreq = TC.Options.Rx_Bringup_Freq;
                        TC.Options.Rx_Cal_Pol = Tconfig.Pol_Rx;%'LHCP';
                        TC.Options.Rx_Test_Power=-55;
                    end

        end
    end


    close all; try delete(findall(0)); catch end

    TC.T.setconfig('System.LiveCalibration.Mode',18,'Verbose',true);

    TC.config_for_catr();

    TC.T.set_num_patches(num_patch,num_patch,'byatten_tx',true,'byatten_rx',true);

    processor = 'ACU';
    js= [];
    response = TC.T.setRestCommand('resetRfdcAttenuator',processor,js,[]);

    bringup_start=datetime('now');

    try
        TC.T.Bringup(Tconfig,'CheckLC', false);
        TC.UUT.failedBUcount=0;
    catch
        try
            TC.UUT.failedBUcount=1;
            TC.T.Bringup(Tconfig,'CheckLC', false);
        catch
            TC.UUT.failedBUcount=2;
            TC.T.Bringup(Tconfig,'CheckLC', false);
        end
    end

    

    bringup_end=datetime('now');
    TC.Options.Timing.bringup=bringup_end-bringup_start;


                 % TC.T.set_modem_IF_gain(1,1, 36); %TxRx, beam, gain
                 % TC.T.set_modem_IF_gain(1,2, 36); %TxRx, beam, gain
                 % TC.T.set_modem_IF_gain(2,1, 12); %TxRx, beam, gain
                 % TC.T.set_modem_IF_gain(2,2, 12); %TxRx, beam, gain
                 % 
                 
                 TC.T.enableTx(1);

   %% TC.execute();

       % Download the Terminal Config & Cal
    TC.logline('Downloading Terminal Config & Cal File Status...\n');
    TC.UUT.Config = TC.T.getAllConfig();
    TC.UUT.CalFiles = TC.T.check_cal_config;
    TC.T.getStatus;
    TC.UUT.Status = TC.T.Status;
    
    start_angle = 1;
    TC.Exe_Completed_i = 0;
    TC.Exe_StartTime = datetime('now');
    
    
        % Set the steering angle
        TC.T.setManualPhiTheta('phi',0,'theta',0,'beam',1,...
        'TxPol',TC.Options.Tx_Cal_Pol,...
        'TxFreqMHz',TC.Options.Tx_TerminalFreq*1000,...
        'RxPol',TC.Options.Rx_Cal_Pol,...
        'RxFreqMHz',TC.Options.Rx_TerminalFreq*1000,...
        'UseBeamController',false);

        TC.T.setManualPhiTheta('phi',0,'theta',50,'beam',2,...
        'TxPol',TC.Options.Tx_Cal_Pol,...
        'TxFreqMHz',TC.Options.Tx_TerminalFreq*1000,...
        'RxPol',TC.Options.Rx_Cal_Pol,...
        'RxFreqMHz',TC.Options.Rx_TerminalFreq*1000,...
        'UseBeamController',false);
    

            
    TC.UUT.APs_state_start=TC.T.get_state();

    % Check if the TestArray & Phi Mask have been prepared
    if TC.Prepared == false
        TC.prepare_execution();
    end
    
    % Run the Live Cal
    if TC.Options.RunLiveCal == true
        TC.RunLiveCal(TC, 'ResultsName', 'PreExecution')
    end

    TC.UUT.APs_state_end=TC.T.get_state();

    TC.T.enableTx(0);

    TC.save_after_break;
    
    diary('off');

    end
end
    
end
