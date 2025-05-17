import matplotlib
matplotlib.use('TkAgg')  # For PyCharm interactivity

import os
import re
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d
import csv
from datetime import datetime
from pathlib import Path
import pandas as pd
import json

# Load parameters from JSON config
params_path = "params_config.json"
if os.path.exists(params_path):
    with open(params_path, "r") as f:
        user_params = json.load(f)
else:
    raise FileNotFoundError(f"{params_path} not found. Run via GUI or supply config.")



# ========================================
# Clean Output Directory Before Writing New Peak Data
# ========================================
generated_data_dir = Path('generated_peak_data_results')
if generated_data_dir.exists():
    print(f"🗑️ Clearing existing files in {generated_data_dir} ...")
    for file in generated_data_dir.glob('peak_data_*.csv'):
        file.unlink()
    print(f"✅ Cleaned up {generated_data_dir}")
else:
    print(f"📁 Creating directory {generated_data_dir}")
    generated_data_dir.mkdir(parents=True, exist_ok=True)

# ========================================
# Parameters
# ========================================
data_dir = 'photon_counts_data/20250403'
pulse_voltages_to_plot = [1.3, 1.6]
gain_voltages_to_plot = [ 65.7,65.8, 65.9, 66.0]
crop_off_start = 100
crop_off_end = 3000
vertical_lines = False
counts_threshold = 100
peak_spacing_threshold = 16
sigma = 3.6

pulse_color_map = {
    1.0: 'black', 1.1: 'darkblue', 1.3: 'green',
    1.6: 'orange', 2.0: 'deeppink', 2.3: 'red',
}

manual_peak_indices = {
    ('CH0', 65.7, 1.6): [140, 178, 553, 590],
    ('CH1', 65.7, 1.6): [130, 177],
}

data_by_channel = {"CH0": defaultdict(lambda: defaultdict(list)),
                   "CH1": defaultdict(lambda: defaultdict(list))}
pulse_by_voltage = defaultdict(lambda: defaultdict(float))

# Override defaults with user parameters
gain_voltages_to_plot = user_params.get("gain_voltages_to_plot", [])
crop_off_start = user_params.get("crop_off_start", 0)
crop_off_end = user_params.get("crop_off_end", 0)
counts_threshold = user_params.get("counts_threshold", 10)
peak_spacing_threshold = user_params.get("peak_spacing_threshold", 5)
sigma = user_params.get("sigma", 1.0)
manual_peak_indices_raw = user_params.get("manual_peak_indices", [])

# ========================================
# Functions
# ========================================
def extract_gain_and_pulse_voltages(filename):
    match = re.search(r"_(\d+)_?(\d+)_gain_(\d+)_?(\d+)[Vv]?_pulse", filename)
    if match:
        gain = float(f"{match.group(1)}.{match.group(2)}")
        pulse = float(f"{match.group(3)}.{match.group(4)}")
        return gain, pulse
    return None, None

def smooth_data(data, sigma=sigma):
    return gaussian_filter1d(data, sigma=sigma)

def write_peak_data_to_file(peaks, data_cropped, filename, gain_voltage, pulse_voltage, channel):
    timestamp_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            "Timestamp", "Channel", "Voltage Gain (V)", "Pulse Voltage (V)",
            "Peak Number", "Peak Index", "Peak Counts", "Index Difference"
        ])
        for i, peak_idx in enumerate(peaks):
            count_value = data_cropped[peak_idx]
            diff = peak_idx - peaks[i - 1] if i > 0 else "N/A"
            writer.writerow([
                timestamp_str, channel, gain_voltage, pulse_voltage,
                i + 1, peak_idx, count_value, diff
            ])
    print(f"✅ Peak data written to {filename}")

def find_and_label_peaks(data, ax, label, crop_off_start, crop_off_end, color, style,
                         vertical_lines=False, channel=None, gain_voltage=None, pulse_voltage=None,
                         output_file=None, manual_peaks=None):
    data_cropped = data[crop_off_start:-crop_off_end]
    smoothed_data = smooth_data(data_cropped)
    x = np.arange(len(smoothed_data))

    peaks, _ = find_peaks(smoothed_data, height=counts_threshold, distance=peak_spacing_threshold)
    if manual_peaks is not None:
        peaks = np.unique(np.concatenate([peaks, np.array(manual_peaks)]))

    ax.plot(x, smoothed_data, label=label, alpha=0.8, color=color, linestyle=style, linewidth=2)
    counts_at_peaks = smoothed_data[peaks]
    errors = np.sqrt(counts_at_peaks)
    ax.errorbar(x[peaks], counts_at_peaks, yerr=errors, fmt='o', color=color,
                ecolor='gray', elinewidth=1, capsize=3, markersize=5, label=f"{label} Peaks")

    if vertical_lines:
        for p in peaks:
            ax.axvline(x=p, color=color, linestyle='--', linewidth=1)

    if output_file:
        write_peak_data_to_file(peaks, smoothed_data, output_file, gain_voltage, pulse_voltage, channel)

    return peaks

# ========================================
# Load Data Files
# ========================================
print("\n=== Loading Data Files ===\n")
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
            print(f"[SKIPPED] Could not parse voltages from: {file}")
            continue

        if gain_voltages_to_plot and gain_v not in gain_voltages_to_plot:
            continue
        if pulse_voltages_to_plot and pulse_v not in pulse_voltages_to_plot:
            continue

        channel = "CH0" if "CH0" in file else "CH1"
        print(f"[LOADED] {channel} | Gain = {gain_v} V | Pulse = {pulse_v} V | from {file}")
        data_by_channel[channel][gain_v]["light"].append((data, pulse_v, file))
        pulse_by_voltage[channel][gain_v] = pulse_v
print(f"Looking for gain_voltages: {gain_voltages_to_plot}")

# ========================================
# Plotting & Peak Detection
# ========================================
print("\n=== Plotting and Peak Detection ===\n")

for channel, channel_data in data_by_channel.items():
    voltages_sorted = sorted(channel_data.keys())

    print("\n=== Plotting and Peak Detection ===\n")
    print("DEBUG: Channel =", channel)
    print("DEBUG: voltages_sorted =", voltages_sorted)
    print("DEBUG: len(voltages_sorted) =", len(voltages_sorted))

    if len(voltages_sorted) == 0:
        print(f"[SKIPPED] No voltages found for channel {channel}")
        continue

    fig, axes = plt.subplots(len(voltages_sorted), 1, figsize=(15, 4 * len(voltages_sorted)))
    for idx, gain_v in enumerate(voltages_sorted):
        ax = axes[idx]
        voltage_data = channel_data[gain_v]

        if "light" in voltage_data:
            for data, pulse_v, src in voltage_data["light"]:
                color = pulse_color_map.get(pulse_v, 'gray')
                label = f"{pulse_v}V pulse"
                manual_peaks = manual_peak_indices.get((channel, gain_v, pulse_v))
                output_file = generated_data_dir / f"peak_data_{channel}_gain_{gain_v}V_pulse_{pulse_v}V.csv"

                find_and_label_peaks(
                    data=data,
                    ax=ax,
                    label=label,
                    crop_off_start=crop_off_start,
                    crop_off_end=crop_off_end,
                    color=color,
                    style='solid',
                    vertical_lines=vertical_lines,
                    channel=channel,
                    gain_voltage=gain_v,
                    pulse_voltage=pulse_v,
                    output_file=output_file,
                    manual_peaks=manual_peaks
                )

        ax.set_title(f"{channel} — {gain_v} V gain", fontsize=18)
        ax.set_xlabel("Index", fontsize=14)
        ax.set_ylabel("Counts", fontsize=14)
        ax.grid(True)
        ax.legend(fontsize=10)

    plt.tight_layout()
    plt.show()

# ========================================
# Combine All Peak Data into Final Output CSV
# ========================================
repo_root = Path(__file__).resolve().parent
results_dir = repo_root / 'results-from-generated-data'
results_dir.mkdir(parents=True, exist_ok=True)

csv_files = list(generated_data_dir.glob('peak_data_*.csv'))
if not csv_files:
    print(f"[WARNING] No peak_data_*.csv files found in {generated_data_dir}")
else:
    print(f"Found {len(csv_files)} peak data CSV files to combine.")

    combined_df = pd.concat(
        [pd.read_csv(f).assign(SourceFile=f.name) for f in csv_files],
        ignore_index=True
    ).sort_values(
        by=['Channel', 'Voltage Gain (V)', 'Pulse Voltage (V)', 'Peak Index'],
        ascending=[True, True, True, True]
    )

    combined_output_file = results_dir / 'all_peaks_combined_sorted.csv'
    combined_df.to_csv(combined_output_file, index=False)

    print(f"✅ Combined peak data written to: {combined_output_file}")


