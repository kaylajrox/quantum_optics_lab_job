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
root_dir = 'photon_counts_data/20250403'
crop_off = 3700
vertical_lines = False
counts_threshold = 100
peak_spacing_threshold = 15
experiment_duration_analysize = "300s"



#========================================================
#========================================================
#========================================================


# Dictionaries to hold photon_counts_data grouped by duration and channel
ch0_by_duration = defaultdict(list)
ch1_by_duration = defaultdict(list)

# Regex to extract duration from folder names (e.g., '20s' from '1_2V_20s')
duration_pattern = re.compile(r'(\d+)s$')

# Function to extract voltage and format the title
def extract_gain_voltage_and_title(file_name):
    match = re.match(r"(\d+)_?(\d+)_gain", file_name)
    if match:
        gain_voltage = float(f"{match.group(1)}.{match.group(2)}")  # Create voltage like 65.5V
        return gain_voltage,f"{gain_voltage}V gain"
    return file_name  # Default to the filename if not matching the pattern


def analyze_peaks(data_dict, channel_name="CH0"):
    print(f"\n--- Peak Analysis for {channel_name} ---\n")
    for duration, data_list in sorted(data_dict.items()):
        for data, label in data_list:
            gain_voltage, title = extract_gain_voltage_and_title(label)
            cropped_data = data[:-crop_off]

            # Find peaks (you can tweak parameters like height, distance)
            peaks, _ = find_peaks(cropped_data, height=counts_threshold,distance=peak_spacing_threshold)  # adjust height as needed

            # Compute differences between consecutive peaks
            peak_diffs = np.diff(peaks)

            print(f"{title}:")
            print(f"  Found peak indices: {peaks}")
            print(f"  Differences between peaks: {peak_diffs}")
            print()

def find_and_label_peaks(data, ax, label, crop_off, vertical_lines=vertical_lines):
    # Apply cropping
    data_cropped = data[:-crop_off]
    x = np.arange(len(data_cropped))

    # Find peaks
    peaks, _ = find_peaks(data_cropped, height=counts_threshold, distance=peak_spacing_threshold)

    # Plot the photon_counts_data and peaks
    ax.plot(x, data_cropped, label=label, alpha=0.7)
    ax.scatter(x[peaks], data_cropped[peaks], color='red', label='Peaks')

    # Add vertical lines if enabled
    if vertical_lines:
        for peak in peaks:
            ax.axvline(x=peak, color='red', linestyle='--', linewidth=1)

    # Label each peak
    for i, idx in enumerate(peaks):
        ax.text(x[idx], data_cropped[idx] + 100, f'{i + 1}', ha='center', va='bottom', fontsize=9, color='red')

    ax.set_xlabel("Index")
    ax.set_ylabel("Value")
    ax.grid(True)

    # Calculate and return the horizontal distance between consecutive peaks
    distance = []
    for i in range(1, len(peaks)):
        distance.append(x[peaks[i]] - x[peaks[i - 1]])

    return distance, peaks, data_cropped


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
            except Exception as e:
                print(f"Error loading {file_path}: {e}")


def plot_grouped_subplots(data_dict, title_prefix, n_cols=3):
    distance_dict = defaultdict(list)

    for duration, data_list in sorted(data_dict.items()):
        n_plots = len(data_list)
        n_rows = math.ceil(n_plots / n_cols)

        fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 4 * n_rows))
        axes = axes.flatten()

        for idx, (data, label) in enumerate(data_list):
            ax = axes[idx]
            gain_voltage,title = extract_gain_voltage_and_title(label)
            distance, peaks, cropped_data = find_and_label_peaks(data, ax, title, crop_off)
            distance_dict[title].append(distance)
            ax.set_title(title, fontsize=8)

        for j in range(idx + 1, len(axes)):
            fig.delaxes(axes[j])

        fig.suptitle(f"{title_prefix} - Duration: {duration}", fontsize=16)
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.show()

    return distance_dict

analyze_peaks(ch0_by_duration, "CH0")
analyze_peaks(ch1_by_duration, "CH1")


# Get the distance photon_counts_data for CH0 and CH1 grouped by duration
ch0_distances = plot_grouped_subplots(ch0_by_duration, "CH0 Files")
ch1_distances = plot_grouped_subplots(ch1_by_duration, "CH1 Files")


