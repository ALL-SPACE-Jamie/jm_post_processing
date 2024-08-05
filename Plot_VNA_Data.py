import pandas as pd
import numpy as np
import matplotlib.pyplot as plt;
plt.rcParams['font.size'] = 12
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
import seaborn as sns
from matplotlib.markers import MarkerStyle
plt.close('all')

import os
import pandas as pd


directory = "c:\\Users\\RyanFairclough\\Downloads\\Beam1_port_pol_values"

for root, dirs, files in os.walk(directory):
    for file in files:
        if file.endswith(".csv"):
            filepath = os.path.join(root, file)
            df = pd.read_csv(filepath)
            data_to_plot = df.iloc[6:43, 3]  # Assuming D7:D43 corresponds to index 6:42
            plt.plot(data_to_plot, label=file)

plt.xlabel('Index')
plt.ylabel('Data')
plt.title('Data from column D7 to D43')
plt.legend()
plt.show()
