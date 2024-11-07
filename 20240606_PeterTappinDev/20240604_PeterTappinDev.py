# -*- coding: utf-8 -*-
"""
Created on Mon Dec 18 16:40:42 2023

@author: ptappin
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.backends.backend_pdf
from matplotlib import cm, colors
from scipy.stats import norm
import os
import glob
import copy
import csv
import json
import time
from pylab import *
# import seaborn as sns
from matplotlib.markers import MarkerStyle
plt.close('all')

# code
peter_results = pd.read_csv(r'C:\GitHub\jm_post_processing\20240606_PeterTappinDev\example.csv')

temp_data = peter_results['18.5']


