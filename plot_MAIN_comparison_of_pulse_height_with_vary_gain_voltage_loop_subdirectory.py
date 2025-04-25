import matplotlib
matplotlib.use('TkAgg')  # For PyCharm interactivity

import os
import re
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
from scipy.signal import find_peaks
import math
from scipy.ndimage import gaussian_filter1d
import csv

#========================================
#         Parameters
#========================================
root_dirs = [
    'data_photon_counts/20250417_1_3_pulse_height',
    'data_photon_counts/20250418_1_6_pulse_height'
]

crop_off_start = 100
crop_off_end = 3000
vertical_lines = False
counts_threshold = 100
peak_spacing_threshold = 15
experiment_duration_analysize = "300s"

# Fixed pulse color map
pulse_color_map = {
    1.3: 'green',
    1.6: 'orange'
    # 1.3: 'darkblue',
    # 1.6: 'deeppink'
}

#========================================
#         Data Structures
#========================================
data_by_channel = {
    "CH0": defaultdict(lambda: defaultdict(list)),
    "CH1": defaultdict(lambda: defaultdict(list))
}

pulse_by_voltage = defaultdict(lambda: defaultdict(float))  # Store pulse voltages

#========================================
#         Helpers
#========================================
def extract_gain_and_pulse_voltages(file_path):
    match = re.search(r"(\d+)_?(\d+)_gain_(\d+)_?(\d+)_pulse", file_path)
    if match:
        gain = float(f"{match.group(1)}.{match.group(2)}")
        pulse = float(f"{match.group(3)}.{match.group(4)}")
        return gain, pulse
    return None, None

def smooth_data(data, sigma=3.1):
    return gaussian_filter1d(data, sigma=sigma)

def write_peak_data_to_file(peaks, data_cropped, filename, gain_voltage, pulse_voltage, channel):
    '''

    :param peaks:
    :param data_cropped:
    :param filename:
    :param gain_voltage: gain voltage sent to photodiode
    :param pulse_voltage:
    :param channel:
    :return:
    '''
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Channel", "Voltage Gain (V)", "Pulse Voltage (V)", "Peak Number", "Peak Index", "Peak Counts", "Index Difference"])
        for i, peak_idx in enumerate(peaks):
            count_value = data_cropped[peak_idx]
            diff = peak_idx - peaks[i - 1] if i > 0 else "N/A"
            writer.writerow([channel, gain_voltage, pulse_voltage, i + 1, peak_idx, count_value, diff])
    print(f"Peak data written to {filename}")

def find_and_label_peaks(data, ax, label, crop_off_start, crop_off_end, color, style,
                         vertical_lines=False, print_peaks=False,
                         channel=None, gain_voltage=None, pulse_voltage=None,
                         output_file=None):
    data_cropped = data[crop_off_start:-crop_off_end]
    smoothed_data = smooth_data(data_cropped)
    x = np.arange(len(smoothed_data))
    peaks, _ = find_peaks(smoothed_data, height=counts_threshold, distance=peak_spacing_threshold)

    ax.plot(x, smoothed_data, label=label, alpha=0.8, color=color, linestyle=style)
    counts_at_peaks = smoothed_data[peaks]
    errors = np.sqrt(counts_at_peaks)
    ax.errorbar(x[peaks], counts_at_peaks, yerr=errors, fmt='o', color=color,
                ecolor='gray', elinewidth=1, capsize=3, markersize=5, label=f"{label} Peaks")

    if output_file:
        write_peak_data_to_file(peaks, smoothed_data, output_file, gain_voltage, pulse_voltage, channel)

    if vertical_lines:
        for p in peaks:
            ax.axvline(x=p, color=color, linestyle='--', linewidth=1)

    return peaks

#========================================
#         Load Data
#========================================
print("\n=== Loading Data Files ===\n")
for root_dir in root_dirs:
    for subdir, _, files in os.walk(root_dir):
        if experiment_duration_analysize not in subdir:
            continue
        for file in files:
            if not file.startswith("CH"):
                continue
            full_path = os.path.join(subdir, file)
            try:
                data = np.loadtxt(full_path, delimiter=',')
            except Exception as e:
                print(f"[ERROR] Could not load {full_path}: {e}")
                continue

            gain_v, pulse_v = extract_gain_and_pulse_voltages(file)
            if gain_v is None:
                print(f"[SKIPPED] Could not parse voltages from: {file}")
                continue

            channel = "CH0" if "CH0" in file else "CH1"
            is_dark = "dark" in file.lower()
            light_or_dark = "dark" if is_dark else "light"

            print(f"[LOADED] {channel} | {light_or_dark.upper()} | {gain_v} V gain, {pulse_v} V pulse | from {file}")
            data_by_channel[channel][gain_v][light_or_dark].append((data, pulse_v, os.path.basename(root_dir)))
            pulse_by_voltage[channel][gain_v] = pulse_v

#========================================
#         Plotting with Logging
#========================================
print("\n=== Plotting Subplots and Logging Used Files ===\n")
subplot_counter = 1  # To number the subplots

for channel, channel_data in data_by_channel.items():
    voltages_sorted = sorted(channel_data.keys())
    n_voltages = len(voltages_sorted)
    n_cols = 3
    n_rows = math.ceil(n_voltages / n_cols)

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 4 * n_rows))
    axes = axes.flatten()

    for idx, gain_v in enumerate(voltages_sorted):
        ax = axes[idx]
        voltage_data = channel_data[gain_v]
        pulse_v = pulse_by_voltage[channel][gain_v]

        print("                                                   ")
        print(f"Subplot {subplot_counter}: {channel} | Gain = {gain_v} V")

        for ld_type, style in zip(["light"], ["solid"]):
            if ld_type in voltage_data:
                for data, pulse_height_voltage_sent, src in voltage_data[ld_type]:
                    color = pulse_color_map.get(pulse_height_voltage_sent, 'gray')
                    label = f"{pulse_height_voltage_sent}V pulse"

                    # Log which file is being plotted
                    print(f"  ➤ File: {src}, Pulse = {pulse_height_voltage_sent}V")

                    find_and_label_peaks(
                        data,
                        ax,
                        label=label,
                        crop_off_start=crop_off_start,
                        crop_off_end=crop_off_end,
                        color=color,
                        style=style,
                        vertical_lines=vertical_lines,
                        print_peaks=False,
                        channel=channel,
                        gain_voltage=gain_v,
                        pulse_voltage=pulse_height_voltage_sent,
                        output_file=f"generated_peak_data_results/peak_data_{channel}_gain_{gain_v}V_pulse_{pulse_height_voltage_sent}V.csv"
                    )

        ax.set_title(f"{channel} — {gain_v} V gain", fontsize=10)
        ax.set_xlabel("Index")
        ax.set_ylabel("Counts")
        ax.grid(True)
        ax.legend(fontsize=8)
        subplot_counter += 1

    # Remove unused axes
    for j in range(idx + 1, len(axes)):
        fig.delaxes(axes[j])

    fig.suptitle(f"{channel} — Light Data", fontsize=18)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()

