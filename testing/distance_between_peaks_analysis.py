import matplotlib
matplotlib.use('TkAgg')  # For PyCharm interactivity

import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict
from scipy.signal import find_peaks
import math

root_dir = '../data_photon_counts/20250403'
crop_off = 3500
vertical_lines = True
counts_threshold = 10

ch0_by_duration = defaultdict(list)
ch1_by_duration = defaultdict(list)

print("\n--- Peak Indices for 300s Datasets (Labeled) ---\n")

for subdir, _, files in os.walk(root_dir):
    if not subdir.endswith("300s"):
        continue

    folder_name = os.path.basename(subdir)
    match = re.match(r"(\d+)_?(\d+)_gain_(\d+)_(\d+)_300s", folder_name)
    if not match:
        continue

    print(subdir, folder_name, match.groups())
    voltage = f"{match.group(1)}.{match.group(2)}V"
    pulse = f"{int(match.group(3))}.{match.group(4)}V"

    def extract_voltage_and_title(file_name):
        match = re.match(r"(\d+)_?(\d+)_gain", file_name)
        if match:
            voltage = float(f"{match.group(1)}.{match.group(2)}")
            return f"{voltage}V gain"
        return file_name

    def find_and_label_peaks(data, ax, label, crop_off, vertical_lines=vertical_lines):
        data_cropped = data[:-crop_off]
        x = np.arange(len(data_cropped))

        peaks, _ = find_peaks(data_cropped, height=counts_threshold, distance=15)

        ax.plot(x, data_cropped, label=label, alpha=0.7)
        ax.scatter(x[peaks], data_cropped[peaks], color='blue', label='Peaks')

        if vertical_lines:
            for peak in peaks:
                ax.axvline(x=peak, color='red', linestyle='--', linewidth=1)

        for i, idx in enumerate(peaks):
            ax.text(x[idx], data_cropped[idx] + 100, f'{i + 1}', ha='center', va='bottom', fontsize=9, color='red')

        ax.set_xlabel("Index")
        ax.set_ylabel("Value")
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)  # Finer grid

        distance = []
        for i in range(1, len(peaks)):
            distance.append(x[peaks[i]] - x[peaks[i - 1]])

        return distance, peaks, data_cropped

    def plot_grouped_subplots(data_dict, title_prefix, n_cols=3):
        distance_dict = defaultdict(list)

        for duration, data_list in sorted(data_dict.items()):
            n_plots = len(data_list)
            n_rows = math.ceil(n_plots / n_cols)

            fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 4 * n_rows))
            axes = axes.flatten()

            for idx, (data, label) in enumerate(data_list):
                ax = axes[idx]
                title = extract_voltage_and_title(label)
                distance, peaks, cropped_data = find_and_label_peaks(data_dict, ax, title, crop_off)
                distance_dict[title].append(distance)
                ax.set_title(title, fontsize=8)

            for j in range(idx + 1, len(axes)):
                fig.delaxes(axes[j])

            fig.suptitle(f"{title_prefix} - Duration: {duration}", fontsize=16)
            plt.tight_layout(rect=[0, 0, 1, 0.96])
            plt.show()

    for file in files:
        if not file.startswith("CH0"):
            continue

        file_path = os.path.join(subdir, file)
        try:
            data = np.loadtxt(file_path, delimiter=',')

            if len(data) > crop_off:
                cropped_data = data[:-crop_off]
            else:
                cropped_data = data

            peaks, _ = find_peaks(cropped_data, height=counts_threshold, distance=15)
            limited_peaks = peaks[:12]

            labeled_peaks = [
                {"Peak Number": i + 1, "Index of Peak": int(idx), "Counts": int(cropped_data[int(idx)])}
                for i, idx in enumerate(limited_peaks)
            ]

            print(f"Gain: {voltage}, Pulse: {pulse} → Peaks: {labeled_peaks}")

        except Exception as e:
            print(f"Error reading {file_path}: {e}")

# Run grouped plotting
ch0_distances = plot_grouped_subplots(ch0_by_duration, "CH0 Files")
ch1_distances = plot_grouped_subplots(ch1_by_duration, "CH1 Files")
