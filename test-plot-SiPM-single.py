# TODO add where the generated data on csv came from (which python file generated it)

import matplotlib
matplotlib.use('TkAgg')  # For PyCharm interactivity

import os
import re
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d
from datetime import datetime
import csv

# =================== PARAMETERS ===================
data_dir = 'data-photon-counts-SiPM/20250507_baseline_data_for_coic_comparison'
gain_voltages_to_plot = [65.7]
pulse_voltages_to_plot = [1.6]
crop_off_start = 100
crop_off_end = 3000
vertical_lines = False
counts_threshold = 100
peak_spacing_threshold = 16
sigma = 3.6

pulse_color_map = {
    1.0: 'black',
    1.1: 'darkblue',
    1.3: 'green',
    1.6: 'orange',
    2.0: 'deeppink',
    2.3: 'red',
}

manual_peak_indices = {
    ('CH0', 65.7, 1.6): [140, 178, 553, 590],
    ('CH1', 65.7, 1.6): [130, 177],
}

# =================== HELPER FUNCTIONS ===================

def extract_gain_and_pulse_voltages(filename):
    match = re.search(r"CH(\d+)_gain_(\d+\.\d+)[Vv]?_pulse_(\d+\.\d+)[Vv]?", filename)
    if match:
        channel = int(match.group(1))
        gain = float(match.group(2))
        pulse = float(match.group(3))
        return gain, pulse
    return None, None

def smooth_data(data, sigma=sigma):
    return gaussian_filter1d(data, sigma=sigma)

def find_and_label_peaks(data, ax, label, crop_off_start, crop_off_end, color, style,
                         vertical_lines=False, print_peaks=True,
                         channel=None, gain_voltage=None, pulse_voltage=None,
                         output_file=None, manual_peaks=None):
    data_cropped = data[crop_off_start:-crop_off_end]
    smoothed_data = smooth_data(data_cropped)
    x = np.arange(len(smoothed_data))

    peaks, _ = find_peaks(
        smoothed_data,
        height=counts_threshold,
        distance=peak_spacing_threshold
    )

    if manual_peaks is not None:
        peaks = np.concatenate([peaks, np.array(manual_peaks)])
        peaks = np.unique(peaks)

    ax.plot(x, smoothed_data, label=label, alpha=0.8, color=color, linestyle=style, linewidth=2)
    counts_at_peaks = smoothed_data[peaks]
    errors = np.sqrt(counts_at_peaks)
    ax.errorbar(x[peaks], counts_at_peaks, yerr=errors, fmt='o', color=color,
                ecolor='gray', elinewidth=1, capsize=3, markersize=5, label=f"{label} Peaks")

    if vertical_lines:
        for p in peaks:
            ax.axvline(x=p, color=color, linestyle='--', linewidth=1)

    if print_peaks:
        print(f"\n[PEAK INDICES] {channel} | Gain: {gain_voltage} V | Pulse: {pulse_voltage} V")
        print("Peak # | Index | Counts")
        for i, peak_idx in enumerate(peaks):
            count_val = smoothed_data[peak_idx]
            print(f"{i+1:6} | {peak_idx:5} | {count_val:.2f}")

# =================== LOAD DATA ===================
data_by_channel = {"CH0": defaultdict(lambda: defaultdict(list)), "CH1": defaultdict(lambda: defaultdict(list))}
pulse_by_voltage = defaultdict(lambda: defaultdict(float))

for subdir, _, files in os.walk(data_dir):
    for file in files:
        if not file.startswith("CH") or "dark" in file.lower():
            continue

        full_path = os.path.join(subdir, file)
        try:
            data = np.loadtxt(full_path, delimiter=',')
        except Exception as e:
            print(f"[ERROR] Could not load {full_path}: {e}")
            continue

        gain_v, pulse_v = extract_gain_and_pulse_voltages(file)
        if gain_v is None:
            continue

        channel = "CH0" if "CH0" in file else "CH1"
        data_by_channel[channel][gain_v]["light"].append((data, pulse_v, file))
        pulse_by_voltage[channel][gain_v] = pulse_v

# =================== SIDE-BY-SIDE PLOTTING ===================
gain_voltage = gain_voltages_to_plot[0]
pulse_voltage = pulse_voltages_to_plot[0]

fig, (ax0, ax1) = plt.subplots(1, 2, figsize=(16, 6), sharey=True)
axes = [ax0, ax1]
channels = ["CH0", "CH1"]

for ax, channel in zip(axes, channels):
    try:
        data_list = data_by_channel[channel][gain_voltage]["light"]
    except KeyError:
        print(f"[WARNING] No data for {channel} at {gain_voltage} V.")
        continue

    for data, pulse_v, src in data_list:
        if pulse_v != pulse_voltage:
            continue
        color = pulse_color_map.get(pulse_v, 'gray')
        label = f"{channel} {pulse_v}V pulse"
        manual_peaks = manual_peak_indices.get((channel, gain_voltage, pulse_v))
        output_file = f"generated_peak_data_results/peak_data_{channel}_gain_{gain_voltage}V_pulse_{pulse_v}V.csv"

        find_and_label_peaks(
            data=data,
            ax=ax,
            label=label,
            crop_off_start=crop_off_start,
            crop_off_end=crop_off_end,
            color=color,
            style='solid',
            print_peaks=True,
            vertical_lines=vertical_lines,
            channel=channel,
            gain_voltage=gain_voltage,
            pulse_voltage=pulse_voltage,
            output_file=output_file,
            manual_peaks=manual_peaks
        )

    ax.set_title(f"{channel} — {gain_voltage} V gain", fontsize=24)
    ax.set_xlabel("Index", fontsize=24)
    ax.set_ylabel("Counts", fontsize=24)
    ax.tick_params(axis='both', labelsize=20)
    ax.grid(True)
    ax.legend(fontsize=10)

plt.tight_layout()
plt.show()


