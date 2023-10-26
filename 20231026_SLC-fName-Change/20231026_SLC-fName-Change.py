import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import csv
import pickle

# inputs
filePath = r'C:\Users\jmitchell\Downloads\dev\test'

# definitions
def find__measFiles(filePath, fileString):
    global measFiles
    files = []
    for root, directories, file in os.walk(filePath):
        for file in file:
            if (file.endswith(".csv")) == True:
                files.append(os.path.join(root, file))
    measFiles = []
    for i in range(len(files)):
        if fileString in files[i]:
            measFiles.append(files[i])

find__measFiles(filePath, 'SB2')
for measFile in measFiles:
    fName = measFile.split('\\')[-1]
    components = fName.split('_')
    comp4 = components[4]
    comp4 = comp4.replace("TLMPB", "TLMB")
    comp4 = comp4.replace("Ph", ".0Ph")
    comp4 = comp4 + '.0'
    fNameNew = components[0] + '_' + components[1] + '_' + components[2] + '_' + components[3] + '_' + comp4 + '_' + components[6] + '_' + components[7] + '_' + components[8] + '_' + components[9] + '_' + components[10] + '_' + components[11] + '_' + components[12] + '_' + components[13]
    measFileNew = filePath + '\\' + fNameNew

# write new file
os.rename(measFile, measFileNew)
