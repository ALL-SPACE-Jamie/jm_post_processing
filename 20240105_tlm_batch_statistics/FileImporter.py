# -*- coding: utf-8 -*-
"""
Created on Thu Dec 21 16:20:49 2023

@author: jmitchell
desc: Classes used for importing various files.
"""
import os
class ImportRFA:
    
    def __init__(self, file_path):
        self.file_path = file_path
                 
    def testDef(self, inVar):
        self.inVar = inVar
        print('test sucessful')
        calc = inVar*5.0
        return calc
    
    def load_RFA_files(self, file_path: str, file_string: str, beam: int):
        files = []
        for root, directories, file in os.walk(file_path):
            for file in file:
                if (file.endswith(".csv")) == True:
                    files.append(os.path.join(root, file))
        meas_files = []
        for i in range(len(files)):
            if file_string in files[i] and 'eam' + str(beam) in files[i] and 'rchive' not in files[i]:
                meas_files.append(files[i])
        
        return meas_files
