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

# Update the root directory path to reflect the new location of the data
root_dir = os.path.join(os.path.dirname(__file__), '../data-photon-counts-SiPM/20250417_1_3_pulse_height')

# Debugging: Check if files are being found
print(f"Looking for data files in: {os.path.abspath(root_dir)}")

#crop_off_start = 0
#crop_off_end = 3800
# newer lsb settings
crop_off_start = 200
crop_off_end = 3250
vertical_lines = False
counts_threshold = 100
peak_spacing_threshold = 15
experiment_duration_analysize = "300s"

#========================================
#         Data Structure
#========================================
data_by_channel = {
    "CH0": defaultdict(dict),
    "CH1": defaultdict(dict)
}
pulse_by_voltage = defaultdict(lambda: defaultdict(float))  # Store pulse voltages

#========================================
#         Extract Voltages
#========================================
def extract_gain_and_pulse_voltages(file_path):
    match = re.search(r"(\d+)_?(\d+)_gain_(\d+)_?(\d+)_pulse", file_path)
    if match:
        gain = float(f"{match.group(1)}.{match.group(2)}")
        pulse = float(f"{match.group(3)}.{match.group(4)}")
        return gain, pulse
    return None, None


def smooth_data(data, window_size=5, sigma=1):
    # Using a Gaussian filter to smooth the data (adjust window_size and sigma as needed)
    return gaussian_filter1d(data, sigma=sigma)


#========================================
#         File Loading + Logging
#========================================
print("\n=== Loading Data Files ===\n")
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
        data_by_channel[channel][gain_v][light_or_dark] = data
        pulse_by_voltage[channel][gain_v] = pulse_v

#========================================
#         Summary Log
#========================================
print("\n=== Voltage Summary ===")
for channel, voltages in data_by_channel.items():
    print(f"\n{channel} Voltages:")
    for v in sorted(voltages.keys()):
        types = ', '.join(data_by_channel[channel][v].keys())
        pulse = pulse_by_voltage[channel][v]
        print(f"  - {v} V gain, {pulse} V pulse ({types})")

#========================================
#         Plotting
#========================================

def write_peak_data_to_file(peaks, data_cropped, filename, gain_voltage, pulse_voltage):
    # Ensure the directory exists
    directory = os.path.dirname(filename)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Voltage Gain (V)", "Pulse Voltage (V)", "Peak Number", "Peak Index", "Peak Counts", "Index Difference"])
        for i, peak_idx in enumerate(peaks):
            count_value = data_cropped[peak_idx]
            if i > 0:
                diff = peak_idx - peaks[i - 1]
            else:
                diff = "N/A"  # No previous peak for the first peak
            writer.writerow([gain_voltage, pulse_voltage, i + 1, peak_idx, count_value, diff])
    print(f"Peak data written to {filename}")

# Function to find and label peaks
def find_and_label_peaks(data, ax, label, crop_off_start,crop_off_end, color, style, vertical_lines=False,
                         print_peaks=False, channel=None, gain_voltage=None, pulse_voltage=None, output_file=None):
    data_cropped = data[crop_off_start:-crop_off_end]
    smoothed_data = smooth_data(data_cropped)  # Apply smoothing here
    x = np.arange(len(smoothed_data))
    peaks, _ = find_peaks(smoothed_data, height=counts_threshold, distance=peak_spacing_threshold)

    ax.plot(x, smoothed_data, label=label, alpha=0.8, color=color, linestyle=style)
    counts_at_peaks = smoothed_data[peaks]
    errors = np.sqrt(counts_at_peaks)
    ax.errorbar(x[peaks], counts_at_peaks, yerr=errors, fmt='o', color=color,
                ecolor='gray', elinewidth=1, capsize=3, markersize=5, label=f"{label} Peaks")

    if output_file:  # Write to file if filename is provided
        write_peak_data_to_file(peaks, smoothed_data, output_file, gain_voltage, pulse_voltage)

    if vertical_lines:
        for p in peaks:
            ax.axvline(x=p, color=color, linestyle='--', linewidth=1)

    if print_peaks and channel and gain_voltage is not None and pulse_voltage is not None:
        print(f"\n[{channel}] {gain_voltage} V gain, {pulse_voltage} V pulse")
        for i, peak_idx in enumerate(peaks):
            count_value = smoothed_data[peak_idx]
            print(f"Peak {i + 1}: Index {peak_idx}, Counts {count_value:.2f}")
            if i > 0:
                diff = peak_idx - peaks[i - 1]
                print(f"Peak {i + 1} - Peak {i} = {diff}")

    return peaks


#========================================
#         CH0 and CH1 — Separate Figures
#========================================
output_file = "peak_data.csv"  # specify the file path where you want to store the data

for channel, channel_data in data_by_channel.items():
    voltages_sorted = sorted(channel_data.keys())
    n_voltages = len(voltages_sorted)
    # Ensure there are voltages to plot
    if n_voltages > 0:
        n_rows = math.ceil(n_voltages / n_cols)

        fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 4 * n_rows))
        axes = axes.flatten()

        for idx, gain_v in enumerate(voltages_sorted):
            ax = axes[idx]
            voltage_data = channel_data[gain_v]
            pulse_v = pulse_by_voltage[channel][gain_v]

            for ld_type, style in zip(["light", "dark"], ["solid", (0, (4, 2))]):
                if ld_type in voltage_data:
                    label = f"{channel} {ld_type}"
                    color = "black" if ld_type == "dark" else ("tab:blue" if channel == "CH0" else "tab:green")
                    find_and_label_peaks(
                        voltage_data[ld_type],
                        ax,
                        label=label,
                        crop_off_start=crop_off_start,
                        crop_off_end=crop_off_end,
                        color=color,
                        style=style,
                        vertical_lines=vertical_lines,
                        print_peaks=(ld_type == "light"),
                        channel=channel,
                        gain_voltage=gain_v,
                        pulse_voltage=pulse_v,
                        output_file=f"generated_peak_data_with_dark/peak_data_gain_voltage{gain_v}V_pulse_height{pulse_v}V.csv"
                    )

            ax.set_title(f"{channel} — {gain_v} V gain, {pulse_v} V pulse", fontsize=10)
            ax.set_xlabel("Index")
            ax.set_ylabel("Counts")
            ax.grid(True)
            ax.legend(fontsize=8)

        for j in range(idx + 1, len(axes)):
            fig.delaxes(axes[j])

        fig.suptitle(f"{channel} — Light vs Dark per Voltage", fontsize=18)
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        plt.show()
    else:
        print(f"[WARNING] No voltages found for channel {channel}. Skipping plot.")