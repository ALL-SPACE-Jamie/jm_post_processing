import numpy as np
import os
import json
import csv
import pandas as pd
import matplotlib.pyplot as plt; plt.close('all')
colMap = []
for i in range(1000):
    colMap.append('r')
    colMap.append('g')
    colMap.append('b')
    colMap.append('c')
    colMap.append('m')
    colMap.append('y')
    colMap.append('brown')
    colMap.append('purple')
    colMap.append('pink')

# definitions

def find__RFAfiles(path):
    global filesRFA
    files = []
    for root, directories, file in os.walk(path):
    	for file in file:
    		if(file.endswith(".csv")):
    			files.append(os.path.join(root,file))
    filesRFA = []
    for i in range(len(files)):
        if 'RFA' in files[i]:
            filesRFA.append(files[i])
            
def analyse__RFAparams(filesRFA):
    global RFAparamDict
    RFAparamDict = {}
    log_fileName = []
    log_temperature = []
    log_f_set = []
    log_beam = []
    log_board = []
    for i in range(len(filesRFA)):
        fileName = filesRFA[i].split('\\')[-1]
        log_fileName.append(fileName)
        log_temperature.append(fileName.split('_')[-1][0:-5])
        log_f_set.append(fileName.split('_')[11])
        log_beam.append(fileName.split('_')[5][-1])
        log_board.append(fileName.split('_')[4])
    RFAparamDict['fileNames'] = log_fileName
    RFAparamDict['temperatures'] = log_temperature
    RFAparamDict['f_sets'] = log_f_set
    RFAparamDict['beams'] = log_beam
    RFAparamDict['boards'] = log_board
    RFAparamDict['filePaths'] = filesRFA
    
def load__RFA(filePath):
    global meas_info, meas_array, f_measPoints
    meas_info = []
    with open(filePath, 'r')as file:
        filecontent = csv.reader(file, delimiter=',')
        for row in filecontent:
            meas_info.append(row)
        meas_info = meas_info[0:22]
        meas_array = np.genfromtxt(filePath, delimiter=',', skip_header=22)
        f_measPoints = np.array(meas_info[21])[::2].astype(float)

## RUN
filePath = r'C:\codeRun\20230209_SES_Terminal_Tx'
# filePath = r'SES_Terminal_Tx'
find__RFAfiles(filePath)
analyse__RFAparams(filesRFA)
df = pd.DataFrame.from_dict(RFAparamDict)
ports = 1#456
        
exponDict = {}

# gain

beams = [1, 2]
exponDict['gain'] = {}
for p in range(len(beams)):
    dfCut = df[df['beams'] == str(beams[p])]
    boards = list(set(RFAparamDict['boards']))
    exponDict['gain']['beam'+str(beams[p])] = {}
    
    for h in range(ports):
        f_sets = list(set(dfCut['f_sets']))  
        f_sets = np.sort(np.array(f_sets))
        f_sets = f_sets[0:-2]
        exponDict['gain']['beam'+str(beams[p])]['port'+str(h+1)] = {}
        
        for m in range(len(f_sets)):
            plt.figure(figsize=(7,4))
        # for m in range(1):
            dfCut_fSet = dfCut[dfCut['f_sets'] == f_sets[m]]
            zlog = []; z1log = []; z2log = []   
            
            averageY = np.zeros([31])
            fitCount = 0.0
            fitValsL = []
            fitValsR = []
            for k in range(len(boards)):
                dfCut_fSet_boards = dfCut_fSet[dfCut_fSet['boards'] == boards[k]]
                temps = list(dfCut_fSet_boards['temperatures'])
                vals = []
                
                for i in range(len(temps)):
                    T = dfCut_fSet_boards[dfCut_fSet_boards['temperatures'] == temps[i]]
                    if len(T) == 1:
                        forLoad = list(dfCut_fSet_boards['filePaths'])[i]
                        load__RFA(forLoad)
                        col = np.argmin(np.abs((f_measPoints-float(f_sets[m]))**2))*2
                        val2append = meas_array[h,col]
                        vals.append(val2append)
                        
                increment = True
                for n in range(1, len(vals)):
                    if vals[n] - vals[n-1] > 0:
                        increment = False                    
                deviationCheck = max(vals)-min(vals)
                
                if deviationCheck < 8 and len(temps) > 2:
                # A = 1
                # if A == 1:
                        
                    temps, vals = zip(*sorted(zip(np.array(temps).astype(float), vals)))
                    x, y = temps, vals
                    print(x,y)
                    # fit
                    z = np.polyfit(x, y, 2)
                    x2 = np.linspace(min(x),max(x),num=31)
                    yNew = z[0]*x2**2+z[1]*x2+z[2]
                    valNorm = z[0]*45**2+z[1]*45+z[2]
                    yNew = yNew - valNorm
                    plt.plot(x,y-valNorm,'ro')
                    plt.plot(x2,yNew,color='r', linewidth=1, alpha=0.1)
                    # sum fitted data for each board
                    yNew = 10**(yNew/20.0)
                    averageY = averageY + yNew
                    fitValsL.append(averageY[0])
                    fitValsR.append(averageY[-1])
                    fitCount = fitCount +1
            
            # average of normalised fitted data over boards
            averageY = 1.0*averageY/fitCount
            averageY = 20.0*np.log10(averageY)
            plt.plot(x2, averageY, 'g--', linewidth=4)
            # fit averageY to get a function for generating new RFA files
            x, y = x2, averageY
            # plt.plot(x2, averageY, 'k-', linewidth=3)
            z = np.polyfit(x, y, 2)
            yNew = z[0]*x2**2+z[1]*x2+z[2]
            plt.plot(x2, yNew, color=colMap[m], linewidth = 2, label = 'freq = ' + f_sets[m] + ' GHz')
            # save the values
            exponDict['gain']['beam'+str(beams[p])]['port'+str(h+1)]['f_set='+str(f_sets[m])+'GHz'] = z
            exponDict['gain']['beam'+str(beams[p])]['port'+str(h+1)]['f_set='+str(f_sets[m])+'GHz'+'_error'] = np.max([np.std(fitValsL), np.std(fitValsR)])
            
            # format
            plt.legend(fontsize=10, loc='lower right')
            title = 'Port' + str(h+1) + ', beam' + str(beams[p]) + ', f_s = ' + str(f_sets[m]) + ' GHz'
            plt.title(title)
            plt.xticks(np.linspace(0,100,num=int((100-0)/5+1))); plt.xlim([20,70]); plt.xlabel('Temperature [degC]')
            plt.yticks(np.linspace(-100,100,num=int((200)/1+1))); plt.ylim([-5,5]); plt.ylabel('S21 [dB]\n(normalised to 45 degC)')
            plt.grid('on')
            plt.tight_layout()
            plt.savefig('C:\\codeRun\\figures\\' + title + '_Gain' + '.png', dpi=200)
            plt.close('all')
        print(str(h) + '/' + str(ports))
# phase

beams = [1, 2]
exponDict['phase'] = {}
for p in range(len(beams)):
    dfCut = df[df['beams'] == str(beams[p])]
    boards = list(set(RFAparamDict['boards']))
    exponDict['phase']['beam'+str(beams[p])] = {}
    
    for h in range(ports):
        f_sets = list(set(dfCut['f_sets']))  
        f_sets = np.sort(np.array(f_sets))
        f_sets = f_sets[0:-2]
        exponDict['phase']['beam'+str(beams[p])]['port'+str(h+1)] = {}
        
        for m in range(len(f_sets)):
            plt.figure(figsize=(7,4))
            dfCut_fSet = dfCut[dfCut['f_sets'] == f_sets[m]]
            zlog = []; z1log = []; z2log = []   

            averageY = np.zeros([31])
            fitCount = 0.0
            for k in range(len(boards)):
                dfCut_fSet_boards = dfCut_fSet[dfCut_fSet['boards'] == boards[k]]
                temps = list(dfCut_fSet_boards['temperatures'])
                vals = []

                for i in range(len(temps)):
                    T = dfCut_fSet_boards[dfCut_fSet_boards['temperatures'] == temps[i]]
                    if len(T) == 1:
                        forLoad = list(dfCut_fSet_boards['filePaths'])[i]
                        load__RFA(forLoad)
                        col = np.argmin(np.abs((f_measPoints-float(f_sets[m]))**2))*2
                        val2append = meas_array[h,col+1]
                        vals.append(val2append)

                for j in range(len(vals)):
                    if vals[j] - np.average(vals) > 90.0:
                        vals[j] = vals[j] - 360.0
                    if vals[j] - np.average(vals) < -90.0:
                        vals[j] = vals[j] + 360.0
                for j in range(len(vals)):
                    if vals[j] > 360.0:
                        vals = np.array(vals) - 360.0
                
                
                if len(temps) > 2:
                    
                    temps, vals = zip(*sorted(zip(np.array(temps).astype(float), vals)))
                    
                    increment = True
                    for n in range(1, len(vals)):
                        if vals[n] - vals[n-1] < 0:
                            increment = False                    
                    deviationCheck = max(vals)-min(vals)
                    
                    if increment == True and deviationCheck < 60:
                        
                        x, y = temps, vals
                        if any(np.isnan(y)) == False:
                            # fit
                            z = np.polyfit(x, y, 2)
                            x2 = np.linspace(min(x),max(x),num=31)
                            yNew = z[0]*x2**2+z[1]*x2+z[2]
                            valNorm = z[0]*45**2+z[1]*45+z[2]
                            yNew = yNew - valNorm
                            plt.plot(x,y-valNorm,'ro')
                            plt.plot(x2,yNew,color='r', linewidth=1, alpha=0.1)
                            # sum fitted data for each board
                            yNew = 10**(yNew/20.0)
                            averageY = averageY + yNew
                            fitCount = fitCount + 1
                            fitValsL.append(averageY[0])
                            fitValsR.append(averageY[-1])
            
            if np.abs(np.max(averageY)) > 0.05:
            
                # average of normalised fitted data over boards
                averageY = averageY/fitCount
                averageY = 20*np.log10(averageY)
                # fit averageY to get a function for generating new RFA files
                x, y = x2, averageY
                z = np.polyfit(x, y, 2)
                yNew = z[0]*x2**2+z[1]*x2+z[2]
                plt.plot(x2, yNew, color=colMap[m], linewidth = 2, label = 'freq = ' + f_sets[m] + ' GHz')
                # save the values
                exponDict['phase']['beam'+str(beams[p])]['port'+str(h+1)]['f_set='+str(f_sets[m])+'GHz'] = z
                exponDict['phase']['beam'+str(beams[p])]['port'+str(h+1)]['f_set='+str(f_sets[m])+'GHz'+'_error'] = np.max([np.std(fitValsL), np.std(fitValsR)])
                
                # format
                plt.legend(fontsize=10, loc='lower right')
                title = 'Port' + str(h+1) + ', beam' + str(beams[p]) + ', f_s = ' + str(f_sets[m]) + ' GHz'
                plt.title(title)
                plt.xticks(np.linspace(0,100,num=int((100-0)/5+1))); plt.xlim([20,70]); plt.xlabel('Temperature [degC]')
                plt.yticks(np.linspace(-100,100,num=int((200)/5+1))); plt.ylim([-45,40]); plt.ylabel('Phase [deg]\n(normalised to 45 degC)')
                plt.grid('on')
                plt.tight_layout()
                plt.savefig('C:\\codeRun\\figures\\' + title + '_Phase' + '.png', dpi=200)
                plt.close('all')
        print(str(h) + '/' + str(ports))

plt.close('all')
# go through
for m in range(len(f_sets)):
    plt.figure(figsize=(7,8))
    for i in range(ports):
        # beam 1
        z = exponDict['gain']['beam'+str(1)]['port'+str(i+1)]['f_set='+str(f_sets[m])+'GHz']
        y25 = z[0]*25**2 + z[1]*25 + z[2]
        y45 = z[0]*45**2 + z[1]*45 + z[2]
        y65 = z[0]*65**2 + z[1]*65 + z[2]
        grad1 = (y25-y45)/(25-45)
        grad2 = (y45-y65)/(45-65)
        grad = (grad1 + grad2)/2
        plt.subplot(2, 1, 1)
        plt.plot(float(i+1), grad, colMap[m]+'s')
    plt.plot(float(i+1), grad, colMap[m]+'s', label = 'freq = ' + f_sets[m] + ' GHz (beam 1)')
    plt.xlabel('port'); plt.ylabel('dB/degC')
    plt.ylim([-0.25, 0.25])
    plt.legend()
    plt.grid('on')
    for i in range(ports):
        z = exponDict['gain']['beam'+str(2)]['port'+str(i+1)]['f_set='+str(f_sets[m])+'GHz']
        y25 = z[0]*25**2 + z[1]*25 + z[2]
        y45 = z[0]*45**2 + z[1]*45 + z[2]
        y65 = z[0]*65**2 + z[1]*65 + z[2]
        grad1 = (y25-y45)/(25-45)
        grad2 = (y45-y65)/(45-65)
        grad = (grad1 + grad2)/2
        plt.subplot(2, 1, 2)
        plt.plot(float(i+1), grad, colMap[m]+'s')
    plt.plot(float(i+1), grad, colMap[m]+'s', label = 'freq = ' + f_sets[m] + ' GHz (beam 2)')
    plt.xlabel('port'); plt.ylabel('dB/degC')
    plt.ylim([-0.25, 0.25])
    plt.legend()
    plt.grid('on')
    plt.savefig('C:\\codeRun\\figures\\' + 'GRADIENTS__Gain_' + 'f_s = ' + str(f_sets[m]) + ' GHz' '.png', dpi=200)
    
# go through
for m in range(len(f_sets)):
    plt.figure(figsize=(7,8))
    for i in range(ports):
        # beam 1
        z = exponDict['phase']['beam'+str(1)]['port'+str(i+1)]['f_set='+str(f_sets[m])+'GHz']
        y25 = z[0]*25**2 + z[1]*25 + z[2]
        y45 = z[0]*45**2 + z[1]*45 + z[2]
        y65 = z[0]*65**2 + z[1]*65 + z[2]
        grad1 = (y25-y45)/(25-45)
        grad2 = (y45-y65)/(45-65)
        grad = (grad1 + grad2)/2
        plt.subplot(2, 1, 1)
        plt.plot(float(i+1), grad, colMap[m]+'s')
    plt.plot(float(i+1), grad, colMap[m]+'s', label = 'freq = ' + f_sets[m] + ' GHz (beam 1)')
    plt.xlabel('port'); plt.ylabel('deg/degC')
    plt.ylim([0, 2])
    plt.legend()
    plt.grid('on')
    for i in range(ports):
        z = exponDict['phase']['beam'+str(2)]['port'+str(i+1)]['f_set='+str(f_sets[m])+'GHz']
        y25 = z[0]*25**2 + z[1]*25 + z[2]
        y45 = z[0]*45**2 + z[1]*45 + z[2]
        y65 = z[0]*65**2 + z[1]*65 + z[2]
        grad1 = (y25-y45)/(25-45)
        grad2 = (y45-y65)/(45-65)
        grad = (grad1 + grad2)/2
        plt.subplot(2, 1, 2)
        plt.plot(float(i+1), grad, colMap[m]+'s')
    plt.plot(float(i+1), grad, colMap[m]+'s', label = 'freq = ' + f_sets[m] + ' GHz (beam 2)')
    plt.xlabel('port'); plt.ylabel('deg/degC')
    plt.ylim([0, 2])
    plt.legend()
    plt.grid('on')
    plt.savefig('C:\\codeRun\\figures\\' + 'GRADIENTS__Phase_' + 'f_s = ' + str(f_sets[m]) + ' GHz' '.png', dpi=200)
        
import pickle
# save dictionary to pickle file
with open('Tx_Temperature_Dependancies_20230207.pickle', 'wb') as file:
    pickle.dump(exponDict, file, protocol=pickle.HIGHEST_PROTOCOL)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
import numpy as np
import os
import json
import csv
import pandas as pd
import matplotlib.pyplot as plt; plt.close('all')
colMap = []
for i in range(1000):
    colMap.append('r')
    colMap.append('g')
    colMap.append('b')
    colMap.append('c')
    colMap.append('m')
    colMap.append('y')
    colMap.append('brown')
    colMap.append('purple')
    colMap.append('pink')

# definitions

def find__RFAfiles(path):
    global filesRFA
    files = []
    for root, directories, file in os.walk(path):
    	for file in file:
    		if(file.endswith(".csv")):
    			files.append(os.path.join(root,file))
    filesRFA = []
    for i in range(len(files)):
        if 'RFA' in files[i]:
            filesRFA.append(files[i])
            
def analyse__RFAparams(filesRFA):
    global RFAparamDict
    RFAparamDict = {}
    log_fileName = []
    log_temperature = []
    log_f_set = []
    log_beam = []
    log_board = []
    for i in range(len(filesRFA)):
        fileName = filesRFA[i].split('\\')[-1]
        log_fileName.append(fileName)
        log_temperature.append(fileName.split('_')[-1][0:-5])
        log_f_set.append(fileName.split('_')[11])
        log_beam.append(fileName.split('_')[5][-1])
        log_board.append(fileName.split('_')[4])
    RFAparamDict['fileNames'] = log_fileName
    RFAparamDict['temperatures'] = log_temperature
    RFAparamDict['f_sets'] = log_f_set
    RFAparamDict['beams'] = log_beam
    RFAparamDict['boards'] = log_board
    RFAparamDict['filePaths'] = filesRFA
    
def load__RFA(filePath):
    global meas_info, meas_array, f_measPoints
    meas_info = []
    with open(filePath, 'r')as file:
        filecontent = csv.reader(file, delimiter=',')
        for row in filecontent:
            meas_info.append(row)
        meas_info = meas_info[0:22]
        meas_array = np.genfromtxt(filePath, delimiter=',', skip_header=22)
        f_measPoints = np.array(meas_info[21])[::2].astype(float)

## RUN
filePath = r'C:\codeRun\20230209_SES_Terminal_Rx'
# filePath = r'SES_Terminal_Tx'
find__RFAfiles(filePath)
analyse__RFAparams(filesRFA)
df = pd.DataFrame.from_dict(RFAparamDict)
ports = 1#288
        
exponDict = {}

# gain

beams = [1, 2]
exponDict['gain'] = {}
for p in range(len(beams)):
    dfCut = df[df['beams'] == str(beams[p])]
    boards = list(set(RFAparamDict['boards']))
    exponDict['gain']['beam'+str(beams[p])] = {}
    
    for h in range(ports):
        f_sets = list(set(dfCut['f_sets']))  
        f_sets = np.sort(np.array(f_sets))
        f_sets = f_sets[0:-2]
        exponDict['gain']['beam'+str(beams[p])]['port'+str(h+1)] = {}
        
        for m in range(len(f_sets)):
            plt.figure(figsize=(7,4))
        # for m in range(1):
            dfCut_fSet = dfCut[dfCut['f_sets'] == f_sets[m]]
            zlog = []; z1log = []; z2log = []   
            
            averageY = np.zeros([31])
            fitCount = 0.0
            print('start')
            for k in range(len(boards)):
                dfCut_fSet_boards = dfCut_fSet[dfCut_fSet['boards'] == boards[k]]
                temps = list(dfCut_fSet_boards['temperatures'])
                vals = []
                
                for i in range(len(temps)):
                    T = dfCut_fSet_boards[dfCut_fSet_boards['temperatures'] == temps[i]]
                    if len(T) == 1:
                        forLoad = list(dfCut_fSet_boards['filePaths'])[i]
                        load__RFA(forLoad)
                        col = np.argmin(np.abs((f_measPoints-float(f_sets[m]))**2))*2
                        val2append = meas_array[h,col]
                        vals.append(val2append)
                        
                increment = True
                for n in range(1, len(vals)):
                    if vals[n] - vals[n-1] > 0:
                        increment = False                    
                deviationCheck = max(vals)-min(vals)
                if deviationCheck < 8 and len(temps) > 2 and np.average(vals) > -5 and len(temps) == 3:
                # A = 1
                # if A == 1:
                        
                    temps, vals = zip(*sorted(zip(np.array(temps).astype(float), vals)))
                    x, y = temps, vals
                    # fit
                    z = np.polyfit(x, y, 2)
                    x2 = np.linspace(min(x),max(x),num=31)
                    yNew = z[0]*x2**2+z[1]*x2+z[2]
                    valNorm = z[0]*45**2+z[1]*45+z[2]
                    yNew = yNew - valNorm
                    plt.plot(x,y-valNorm,'ro')
                    plt.plot(x2,yNew,color='r', linewidth=1, alpha=0.1)
                    # sum fitted data for each board
                    yNew = 10**(yNew/20.0)
                    averageY = averageY + yNew
                    fitValsL.append(averageY[0])
                    fitValsR.append(averageY[-1])
                    fitCount = fitCount + 1
            
            # average of normalised fitted data over boards
            averageY = averageY/fitCount
            averageY = 20*np.log10(averageY)
            # fit averageY to get a function for generating new RFA files
            x, y = x2, averageY
            # plt.plot(x2, averageY, 'k-', linewidth=3)
            z = np.polyfit(x, y, 2)
            yNew = z[0]*x2**2+z[1]*x2+z[2]
            plt.plot(x2, yNew, color=colMap[m], linewidth = 2, label = 'freq = ' + f_sets[m] + ' GHz')
            # save the values
            exponDict['gain']['beam'+str(beams[p])]['port'+str(h+1)]['f_set='+str(f_sets[m])+'GHz'] = z
            exponDict['gain']['beam'+str(beams[p])]['port'+str(h+1)]['f_set='+str(f_sets[m])+'GHz'+'_error'] = np.max([np.std(fitValsL), np.std(fitValsR)])
            
            # format
            plt.legend(fontsize=10, loc='lower right')
            title = 'Port' + str(h+1) + ', beam' + str(beams[p]) + ', f_s = ' + str(f_sets[m]) + ' GHz'
            plt.title(title)
            plt.xticks(np.linspace(0,100,num=int((100-0)/5+1))); plt.xlim([20,70]); plt.xlabel('Temperature [degC]')
            plt.yticks(np.linspace(-100,100,num=int((200)/1+1))); plt.ylim([-5,5]); plt.ylabel('S21 [dB]\n(normalised to 45 degC)')
            plt.grid('on')
            print('stop')
            plt.tight_layout()
            plt.savefig('C:\\codeRun\\figures\\' + 'Rx_' + title + '_Gain' + '.png', dpi=200)
            plt.close('all')
        print(str(h) + '/' + str(ports))

# phase

beams = [1, 2]
exponDict['phase'] = {}
for p in range(len(beams)):
    dfCut = df[df['beams'] == str(beams[p])]
    boards = list(set(RFAparamDict['boards']))
    exponDict['phase']['beam'+str(beams[p])] = {}
    
    for h in range(ports):
        f_sets = list(set(dfCut['f_sets']))  
        f_sets = np.sort(np.array(f_sets))
        f_sets = f_sets[0:-2]
        exponDict['phase']['beam'+str(beams[p])]['port'+str(h+1)] = {}
        
        for m in range(len(f_sets)):
            plt.figure(figsize=(7,4))
            dfCut_fSet = dfCut[dfCut['f_sets'] == f_sets[m]]
            zlog = []; z1log = []; z2log = []   

            averageY = np.zeros([31])
            fitCount = 0.0
            for k in range(len(boards)):
                dfCut_fSet_boards = dfCut_fSet[dfCut_fSet['boards'] == boards[k]]
                temps = list(dfCut_fSet_boards['temperatures'])
                vals = []

                for i in range(len(temps)):
                    T = dfCut_fSet_boards[dfCut_fSet_boards['temperatures'] == temps[i]]
                    if len(T) == 1:
                        forLoad = list(dfCut_fSet_boards['filePaths'])[i]
                        load__RFA(forLoad)
                        col = np.argmin(np.abs((f_measPoints-float(f_sets[m]))**2))*2
                        val2append = meas_array[h,col+1]
                        vals.append(val2append)

                for j in range(len(vals)):
                    if vals[j] - np.average(vals) > 90.0:
                        vals[j] = vals[j] - 360.0
                    if vals[j] - np.average(vals) < -90.0:
                        vals[j] = vals[j] + 360.0
                for j in range(len(vals)):
                    if vals[j] > 360.0:
                        vals = np.array(vals) - 360.0
                
                
                if len(temps) > 2:
                    
                    temps, vals = zip(*sorted(zip(np.array(temps).astype(float), vals)))
                    
                    increment = True
                    for n in range(1, len(vals)):
                        if vals[n] - vals[n-1] < 0:
                            increment = False                    
                    deviationCheck = max(vals)-min(vals)
                    
                    if increment == True and deviationCheck < 60:
                        
                        x, y = temps, vals
                        if any(np.isnan(y)) == False:
                            # fit
                            z = np.polyfit(x, y, 2)
                            x2 = np.linspace(min(x),max(x),num=31)
                            yNew = z[0]*x2**2+z[1]*x2+z[2]
                            valNorm = z[0]*45**2+z[1]*45+z[2]
                            yNew = yNew - valNorm
                            plt.plot(x,y-valNorm,'ro')
                            plt.plot(x2,yNew,color='r', linewidth=1, alpha=0.1)
                            # sum fitted data for each board
                            yNew = 10**(yNew/20.0)
                            averageY = averageY + yNew
                            fitValsL.append(averageY[0])
                            fitValsR.append(averageY[-1])
                            fitCount = fitCount + 1
            
            if np.abs(np.max(averageY)) > 0.05:
            
                # average of normalised fitted data over boards
                averageY = averageY/fitCount
                averageY = 20*np.log10(averageY)
                # fit averageY to get a function for generating new RFA files
                x, y = x2, averageY
                z = np.polyfit(x, y, 2)
                yNew = z[0]*x2**2+z[1]*x2+z[2]
                plt.plot(x2, yNew, color=colMap[m], linewidth = 2, label = 'freq = ' + f_sets[m] + ' GHz')
                # save the values
                exponDict['phase']['beam'+str(beams[p])]['port'+str(h+1)]['f_set='+str(f_sets[m])+'GHz'] = z
                exponDict['phase']['beam'+str(beams[p])]['port'+str(h+1)]['f_set='+str(f_sets[m])+'GHz'+'_error'] = np.max([np.std(fitValsL), np.std(fitValsR)])
                
                # format
                plt.legend(fontsize=10, loc='lower right')
                title = 'Port' + str(h+1) + ', beam' + str(beams[p]) + ', f_s = ' + str(f_sets[m]) + ' GHz'
                plt.title(title)
                plt.xticks(np.linspace(0,100,num=int((100-0)/5+1))); plt.xlim([20,70]); plt.xlabel('Temperature [degC]')
                plt.yticks(np.linspace(-100,100,num=int((200)/5+1))); plt.ylim([-45,40]); plt.ylabel('Phase [deg]\n(normalised to 45 degC)')
                plt.grid('on')
                plt.tight_layout()
                plt.savefig('C:\\codeRun\\figures\\' + 'Rx_' + title + '_Phase' + '.png', dpi=200)
                plt.close('all')
        print(str(h) + '/' + str(ports))

plt.close('all')
# go through
for m in range(len(f_sets)):
    plt.figure(figsize=(7,8))
    for i in range(ports):
        # beam 1
        z = exponDict['gain']['beam'+str(1)]['port'+str(i+1)]['f_set='+str(f_sets[m])+'GHz']
        y25 = z[0]*25**2 + z[1]*25 + z[2]
        y45 = z[0]*45**2 + z[1]*45 + z[2]
        y65 = z[0]*65**2 + z[1]*65 + z[2]
        grad1 = (y25-y45)/(25-45)
        grad2 = (y45-y65)/(45-65)
        grad = (grad1 + grad2)/2
        plt.subplot(2, 1, 1)
        error = exponDict['gain']['beam'+str(1)]['port'+str(i+1)]['f_set='+str(f_sets[m])+'GHz_error']
        plt.plot(float(i+1), grad, colMap[m]+'s')
    plt.plot(float(i+1), grad, colMap[m]+'s', label = 'freq = ' + f_sets[m] + ' GHz (beam 1)')
    plt.xlabel('port'); plt.ylabel('dB/degC')
    plt.ylim([-0.25, 0.25])
    plt.legend()
    plt.grid('on')
    for i in range(ports):
        z = exponDict['gain']['beam'+str(2)]['port'+str(i+1)]['f_set='+str(f_sets[m])+'GHz']
        y25 = z[0]*25**2 + z[1]*25 + z[2]
        y45 = z[0]*45**2 + z[1]*45 + z[2]
        y65 = z[0]*65**2 + z[1]*65 + z[2]
        grad1 = (y25-y45)/(25-45)
        grad2 = (y45-y65)/(45-65)
        grad = (grad1 + grad2)/2
        plt.subplot(2, 1, 2)
        plt.plot(float(i+1), grad, colMap[m]+'s')
    plt.plot(float(i+1), grad, colMap[m]+'s', label = 'freq = ' + f_sets[m] + ' GHz (beam 2)')
    plt.xlabel('port'); plt.ylabel('dB/degC')
    plt.ylim([-0.25, 0.25])
    plt.legend()
    plt.grid('on')
    plt.savefig('C:\\codeRun\\figures\\' + 'Rx_' + 'GRADIENTS__Gain_' + 'f_s = ' + str(f_sets[m]) + ' GHz' '.png', dpi=200)
    
# go through
for m in range(len(f_sets)):
    plt.figure(figsize=(7,8))
    for i in range(ports):
        # beam 1
        z = exponDict['phase']['beam'+str(1)]['port'+str(i+1)]['f_set='+str(f_sets[m])+'GHz']
        y25 = z[0]*25**2 + z[1]*25 + z[2]
        y45 = z[0]*45**2 + z[1]*45 + z[2]
        y65 = z[0]*65**2 + z[1]*65 + z[2]
        grad1 = (y25-y45)/(25-45)
        grad2 = (y45-y65)/(45-65)
        grad = (grad1 + grad2)/2
        plt.subplot(2, 1, 1)
        plt.plot(float(i+1), grad, colMap[m]+'s')
    plt.plot(float(i+1), grad, colMap[m]+'s', label = 'freq = ' + f_sets[m] + ' GHz (beam 1)')
    plt.xlabel('port'); plt.ylabel('deg/degC')
    plt.ylim([0, 2])
    plt.legend()
    plt.grid('on')
    for i in range(ports):
        z = exponDict['phase']['beam'+str(2)]['port'+str(i+1)]['f_set='+str(f_sets[m])+'GHz']
        y25 = z[0]*25**2 + z[1]*25 + z[2]
        y45 = z[0]*45**2 + z[1]*45 + z[2]
        y65 = z[0]*65**2 + z[1]*65 + z[2]
        grad1 = (y25-y45)/(25-45)
        grad2 = (y45-y65)/(45-65)
        grad = (grad1 + grad2)/2
        plt.subplot(2, 1, 2)
        plt.plot(float(i+1), grad, colMap[m]+'s')
    plt.plot(float(i+1), grad, colMap[m]+'s', label = 'freq = ' + f_sets[m] + ' GHz (beam 2)')
    plt.xlabel('port'); plt.ylabel('deg/degC')
    plt.ylim([0, 2])
    plt.legend()
    plt.grid('on')
    plt.savefig('C:\\codeRun\\figures\\' + 'Rx_' + 'GRADIENTS__Phase_' + 'f_s = ' + str(f_sets[m]) + ' GHz' '.png', dpi=200)
        
import pickle
# save dictionary to pickle file
with open('Rx_Temperature_Dependancies_20230207run2.pickle', 'wb') as file:
    pickle.dump(exponDict, file, protocol=pickle.HIGHEST_PROTOCOL)