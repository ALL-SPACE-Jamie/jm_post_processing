import pandas as pd
import numpy as np
import os
import glob
import csv

# directory
dirScript = os.getcwd()

# files in
os.chdir(os.path.join(dirScript, 'filesSpaces'))
fileLog = glob.glob('*RFA*.csv')

for i in range(len(fileLog)):
    # open file
    csvFile = []
    with open(fileLog[i],'r')as file:
       filecontent=csv.reader(file,delimiter=',')
       for row in filecontent:
          csvFile.append(row)
          
    # files out
    os.chdir(os.path.join(dirScript, 'filesNoSpaces'))
    
    # write new file
    fileName = fileLog[i][0:-4]
    print(fileName)
    newFileName = fileName.replace(" ", "_")
    print(newFileName)
    
    file = open(newFileName + '_FNnoSpaces.csv', 'w+', newline ='') 
    with file:     
        write = csv.writer(file) 
        write.writerows(csvFile) 
        
    # files in
    os.chdir(os.path.join(dirScript, 'filesSpaces'))
    