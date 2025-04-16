import matplotlib
matplotlib.use('TkAgg')

import os
import re
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
from scipy.signal import find_peaks
import math

#========================================
#         Parameters
#========================================
root_dir = 'photon_counts_data/20250415_dark_light_counts_vary_gain'
crop_off = 3900
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
def find_and_label_peaks(data, ax, label, crop_off, color, style, vertical_lines=False):
    data_cropped = data[:-crop_off]
    x = np.arange(len(data_cropped))
    peaks, _ = find_peaks(data_cropped, height=counts_threshold, distance=peak_spacing_threshold)

    ax.plot(x, data_cropped, label=label, alpha=0.8, color=color, linestyle=style)
    ax.scatter(x[peaks], data_cropped[peaks], color=color, edgecolors='black', zorder=5)

    if vertical_lines:
        for p in peaks:
            ax.axvline(x=p, color=color, linestyle='--', linewidth=1)

    return peaks

#========================================
#         CH0 and CH1 — Separate Figures
#========================================
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

        for ld_type, style in zip(["light", "dark"], ["solid", (0, (4, 2))]):
            if ld_type in voltage_data:
                label = f"{channel} {ld_type}"
                color = "black" if ld_type == "dark" else ("tab:blue" if channel == "CH0" else "tab:green")
                find_and_label_peaks(
                    voltage_data[ld_type],
                    ax,
                    label=label,
                    crop_off=crop_off,
                    color=color,
                    style=style,
                    vertical_lines=vertical_lines
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
