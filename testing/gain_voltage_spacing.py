'''
Plots peaks with variable vertical lines to turn on and off and varibale threshold based on the
counts and the spacing between the initial two peaks.

chooses which experiment duration to plot. Saves all

'''


import matplotlib
matplotlib.use('TkAgg')  # For PyCharm interactivity

import os
import re
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
from scipy.signal import find_peaks
import math

#===================================================
#        User set parameters here only
#===================================================

# Set the root directory
root_dir = '../data_photon_counts/20250403'
crop_off = 3700
vertical_lines = False
counts_threshold = 100
peak_spacing_threshold = 15
experiment_duration_analysize = "300s"



#========================================================
#========================================================
#========================================================


# Dictionaries to hold data_photon_counts grouped by duration and channel
ch0_by_duration = defaultdict(list)
ch1_by_duration = defaultdict(list)

# Regex to extract duration from folder names (e.g., '20s' from '1_2V_20s')
duration_pattern = re.compile(r'(\d+)s$')




# Walk through the directory tree
for subdir, _, files in os.walk(root_dir):
    if experiment_duration_analysize != experiment_duration_analysize:
        continue

    match = duration_pattern.search(os.path.basename(subdir))
    if match:
        duration_key = match.group(0)
        if duration_key != experiment_duration_analysize:
            continue  # Skip folders that aren't 300s

        for file in sorted(files):
            file_path = os.path.join(subdir, file)
            try:
                if file.startswith("CH0"):
                    data = np.loadtxt(file_path, delimiter=',')
                    label = os.path.relpath(file_path, root_dir)
                    ch0_by_duration[duration_key].append((data, label))
                elif file.startswith("CH1"):
                    data = np.loadtxt(file_path, delimiter=',')
                    label = os.path.relpath(file_path, root_dir)
                    ch1_by_duration[duration_key].append((data, label))
                    print(data)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")



# Function to extract voltage and format the title
# def extract_gain_voltage_and_title(file_name):
#     match = re.match(r"(\d+)_?(\d+)_gain", file_name)
#     if match:
#         gain_voltage = float(f"{match.group(1)}.{match.group(2)}")  # Create voltage like 65.5V
#         print(gain_voltage)
#
#         return gain_voltage



gain_voltages = [0 for k in range(len())]
for file in sorted(os.listdir(root_dir)):
    match = re.match(r"(\d+)_?(\d+)_gain", file)
    if match:
        gain_voltage = float(f"{match.group(1)}.{match.group(2)}")  # Create voltage like 65.5V
        print(gain_voltage)

print(gain_voltages)