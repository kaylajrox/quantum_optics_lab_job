import matplotlib

matplotlib.use('TkAgg')  # For PyCharm interactivity

import os
import re
import numpy as np
import matplotlib.pyplot as plt
import math
from collections import defaultdict

# Set the root directory
# root_dir = 'data/20250402_pulse_height_vary'
root_dir = 'data/20250403'
crop_off = 3650

# Dictionaries to hold data grouped by duration (like '20s', '60s') and channel
ch0_by_duration = defaultdict(list)
ch1_by_duration = defaultdict(list)

# Regex to extract duration from folder names (e.g., '20s' from '1_2V_20s')
duration_pattern = re.compile(r'(\d+)s$')


# Function to extract the voltage and format the title
def extract_voltage_and_title(file_name):
    match = re.match(r"(\d+)_?(\d+)_gain", file_name)
    if match:
        voltage = float(f"{match.group(1)}.{match.group(2)}")  # Create voltage like 65.5V
        return f"{voltage}V gain"
    return file_name  # Default to the filename if not matching the pattern


# Walk through the directory tree
for subdir, _, files in os.walk(root_dir):
    match = duration_pattern.search(os.path.basename(subdir))
    if match:
        duration_key = match.group(0)  # e.g. "20s", "60s"
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
    for duration, data_list in sorted(data_dict.items()):
        n_plots = len(data_list)
        n_rows = math.ceil(n_plots / n_cols)

        fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 4 * n_rows))
        axes = axes.flatten()

        for idx, (data, label) in enumerate(data_list):
            ax = axes[idx]
            ax.plot(np.arange(len(data[:-crop_off])), data[:-crop_off])

            # Extract voltage-based title from the label
            title = extract_voltage_and_title(label)
            ax.set_title(title, fontsize=16)
            ax.set_xlabel("Index")
            ax.set_ylabel("Value")
            ax.grid(True)

        for j in range(idx + 1, len(axes)):
            fig.delaxes(axes[j])

        fig.suptitle(f"{title_prefix} - Duration: {duration}", fontsize=24)
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.show()


# Plot CH0 and CH1 grouped by duration
plot_grouped_subplots(ch0_by_duration, "CH0 Files")
plot_grouped_subplots(ch1_by_duration, "CH1 Files")
