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
data_dir = 'data-photon-counts-SiPM/20250428_more_light'
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

# ========================================
# Plotting & Peak Detection
# ========================================
print("\n=== Plotting and Peak Detection ===\n")

for channel, channel_data in data_by_channel.items():
    voltages_sorted = sorted(channel_data.keys())
    fig, axes = plt.subplots(len(voltages_sorted), 1, figsize=(15, 4 * len(voltages_sorted)))
    axes = np.atleast_1d(axes)

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



# import matplotlib
# matplotlib.use('TkAgg')  # For PyCharm interactivity
#
# import os
# import re
# import numpy as np
# import matplotlib.pyplot as plt
# from collections import defaultdict
# from scipy.signal import find_peaks
# from scipy.ndimage import gaussian_filter1d
# import csv
# from datetime import datetime
# from pathlib import Path
# import pandas as pd
#
# # ========================================
# # Parameters
# # ========================================
# data_dir = 'data-photon-counts-SiPM/20250428_more_light'
# pulse_voltages_to_plot = [1.3,1.6]
# gain_voltages_to_plot = [65.7,65.8,65.9,66.0]
# crop_off_start = 100
# crop_off_end = 3000
# vertical_lines = False
# counts_threshold = 100
# peak_spacing_threshold = 16
# sigma = 3.6
# subplot_col_size = 2 # TODO make this work, has only 1 col becuase analyzing 1 but i want ot change the size of subpplots
#
# pulse_color_map = {
#     1.0: 'black',
#     1.1: 'darkblue',
#     1.3: 'green',
#     1.6: 'orange',
#     2.0: 'deeppink',
#     2.3: 'red',
# }
#
# manual_peak_indices = {
#     ('CH0', 65.7, 1.6): [140, 178, 553, 590],
#     ('CH1', 65.7, 1.6): [130, 177],
# }
#
# data_by_channel = {
#     "CH0": defaultdict(lambda: defaultdict(list)),
#     "CH1": defaultdict(lambda: defaultdict(list))
# }
#
# pulse_by_voltage = defaultdict(lambda: defaultdict(float))
#
# # ========================================
# # Functions
# # ========================================
# def extract_gain_and_pulse_voltages(filename):
#     match = re.search(r"_(\d+)_?(\d+)_gain_(\d+)_?(\d+)[Vv]?_pulse", filename)
#     if match:
#         gain = float(f"{match.group(1)}.{match.group(2)}")
#         pulse = float(f"{match.group(3)}.{match.group(4)}")
#         return gain, pulse
#     return None, None
#
# def smooth_data(data, sigma=sigma):
#     return gaussian_filter1d(data, sigma=sigma)
#
# def write_peak_data_to_file(peaks, data_cropped, filename, gain_voltage, pulse_voltage, channel):
#     timestamp_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#     with open(filename, mode='w', newline='') as file:
#         writer = csv.writer(file)
#         writer.writerow([
#             "Timestamp", "Channel", "Voltage Gain (V)", "Pulse Voltage (V)",
#             "Peak Number", "Peak Index", "Peak Counts", "Index Difference"
#         ])
#         for i, peak_idx in enumerate(peaks):
#             count_value = data_cropped[peak_idx]
#             diff = peak_idx - peaks[i - 1] if i > 0 else "N/A"
#             writer.writerow([
#                 timestamp_str, channel, gain_voltage, pulse_voltage,
#                 i + 1, peak_idx, count_value, diff
#             ])
#     print(f"✅ Peak data written to {filename}")
#
# def find_and_label_peaks(data, ax, label, crop_off_start, crop_off_end, color, style,
#                          vertical_lines=False, channel=None, gain_voltage=None, pulse_voltage=None,
#                          output_file=None, manual_peaks=None):
#     data_cropped = data[crop_off_start:-crop_off_end]
#     smoothed_data = smooth_data(data_cropped)
#     x = np.arange(len(smoothed_data))
#
#     peaks, _ = find_peaks(smoothed_data, height=counts_threshold, distance=peak_spacing_threshold)
#
#     if manual_peaks is not None:
#         peaks = np.unique(np.concatenate([peaks, np.array(manual_peaks)]))
#
#     ax.plot(x, smoothed_data, label=label, alpha=0.8, color=color, linestyle=style, linewidth=2)
#     counts_at_peaks = smoothed_data[peaks]
#     errors = np.sqrt(counts_at_peaks)
#     ax.errorbar(x[peaks], counts_at_peaks, yerr=errors, fmt='o', color=color,
#                 ecolor='gray', elinewidth=1, capsize=3, markersize=5, label=f"{label} Peaks")
#
#     if vertical_lines:
#         for p in peaks:
#             ax.axvline(x=p, color=color, linestyle='--', linewidth=1)
#
#     if output_file:
#         write_peak_data_to_file(peaks, smoothed_data, output_file, gain_voltage, pulse_voltage, channel)
#
#     return peaks
#
# # ========================================
# # Load Data Files
# # ========================================
# print("\n=== Loading Data Files ===\n")
# for subdir, _, files in os.walk(data_dir):
#     for file in files:
#         if not file.startswith("CH") or "dark" in file.lower():
#             continue
#
#         full_path = os.path.join(subdir, file)
#         try:
#             data = np.loadtxt(full_path, delimiter=',')
#         except Exception as e:
#             print(f"[ERROR] Could not load {full_path}: {e}")
#             continue
#
#         gain_v, pulse_v = extract_gain_and_pulse_voltages(file)
#         if gain_v is None:
#             print(f"[SKIPPED] Could not parse voltages from: {file}")
#             continue
#
#         if gain_voltages_to_plot and gain_v not in gain_voltages_to_plot:
#             continue
#         if pulse_voltages_to_plot and pulse_v not in pulse_voltages_to_plot:
#             continue
#
#         channel = "CH0" if "CH0" in file else "CH1"
#         print(f"[LOADED] {channel} | Gain = {gain_v} V | Pulse = {pulse_v} V | from {file}")
#         data_by_channel[channel][gain_v]["light"].append((data, pulse_v, file))
#         pulse_by_voltage[channel][gain_v] = pulse_v
#
# # ========================================
# # Plotting & Peak Detection
# # ========================================
# print("\n=== Plotting and Peak Detection ===\n")
#
# for channel, channel_data in data_by_channel.items():
#     voltages_sorted = sorted(channel_data.keys())
#     fig, axes = plt.subplots(len(voltages_sorted), 1, figsize=(15, 4 * len(voltages_sorted)))
#     axes = np.atleast_1d(axes)
#
#     for idx, gain_v in enumerate(voltages_sorted):
#         ax = axes[idx]
#         voltage_data = channel_data[gain_v]
#
#         if "light" in voltage_data:
#             for data, pulse_v, src in voltage_data["light"]:
#                 color = pulse_color_map.get(pulse_v, 'gray')
#                 label = f"{pulse_v}V pulse"
#                 manual_peaks = manual_peak_indices.get((channel, gain_v, pulse_v))
#                 output_file = f"generated_peak_data_results/peak_data_{channel}_gain_{gain_v}V_pulse_{pulse_v}V.csv"
#
#                 find_and_label_peaks(
#                     data=data,
#                     ax=ax,
#                     label=label,
#                     crop_off_start=crop_off_start,
#                     crop_off_end=crop_off_end,
#                     color=color,
#                     style='solid',
#                     vertical_lines=vertical_lines,
#                     channel=channel,
#                     gain_voltage=gain_v,
#                     pulse_voltage=pulse_v,
#                     output_file=output_file,
#                     manual_peaks=manual_peaks
#                 )
#
#         ax.set_title(f"{channel} — {gain_v} V gain", fontsize=18)
#         ax.set_xlabel("Index", fontsize=14)
#         ax.set_ylabel("Counts", fontsize=14)
#         ax.grid(True)
#         ax.legend(fontsize=10)
#
#     plt.tight_layout()
#     plt.show()
#
# # ========================================
# # Combine All Peak Data into Final Output CSV
# # ========================================
# repo_root = Path(__file__).resolve().parents[0]
# generated_data_dir = repo_root / 'generated_peak_data_results'
# results_dir = repo_root / 'results-from-generated-data'
# results_dir.mkdir(parents=True, exist_ok=True)
#
# csv_files = list(generated_data_dir.glob('peak_data_*.csv'))
# if not csv_files:
#     print(f"[WARNING] No peak_data_*.csv files found in {generated_data_dir}")
# else:
#     print(f"Found {len(csv_files)} peak data CSV files to combine.")
#     combined_df = pd.concat(
#         [pd.read_csv(f).assign(SourceFile=f.name) for f in csv_files],
#         ignore_index=True
#     )
#     # ✅ Combine CSVs with additional metadata
#     combined_df = pd.concat(
#         [
#             pd.read_csv(f).assign(
#                 SourceFile=f.name,
#                 State='filtered' if 'filtered' in f.name.lower() else
#                 'unfiltered' if 'unfiltered' in f.name.lower() else
#                 'raw' if 'raw' in f.name.lower() else 'N/A',
#                 GeneratedBy=Path(__file__).name
#             )
#             for f in csv_files
#         ],
#         ignore_index=True
#     )
#
#     # ✅ Sort by Channel, Gain Voltage, Pulse Voltage, Peak Index
#     combined_df = combined_df.sort_values(
#         by=['Channel', 'Voltage Gain (V)', 'Pulse Voltage (V)', 'Peak Index'],
#         ascending=[True, True, True, True]
#     )
#
#     # ✅ Write output CSV to results-from-generated-data
#     combined_output_file = results_dir / 'all_peaks_combined_sorted.csv'
#     combined_df.to_csv(combined_output_file, index=False)
#
#     print(f"✅ Combined peak data written to: {combined_output_file}")
#
#     # ✅ Write output CSV to results-from-generated-data
#     combined_output_file = results_dir / 'all_peaks_combined_sorted.csv'
#     combined_df.to_csv(combined_output_file, index=False)
#
#     print(f"✅ Combined peak data written to: {combined_output_file}")
#
# #
# # import matplotlib
# # matplotlib.use('TkAgg')  # For PyCharm interactivity
# #
# # import os
# # import re
# # import numpy as np
# # import matplotlib.pyplot as plt
# # from collections import defaultdict
# # from scipy.signal import find_peaks
# # from scipy.ndimage import gaussian_filter1d
# # import csv
# # from datetime import datetime
# # from pathlib import Path
# # import pandas as pd
# #
# # # ========================================
# # # Parameters: Gain & Pulse Filtering
# # # ========================================
# # # uncomment for coicidence analysis
# # #data_dir = 'data-photon-counts-SiPM/20250507_baseline_data_for_coic_comparison'
# # data_dir = 'data-photon-counts-SiPM/20250428_more_light'
# #
# #
# # pulse_voltages_to_plot = [1.6,2.0]  # Only plot these pulse voltages
# # gain_voltages_to_plot = [65.7]  # Only plot these gain voltages
# #
# # crop_off_start = 100
# # crop_off_end = 3000
# # vertical_lines = False
# #
# # # Peak finding parameters
# # counts_threshold = 100
# # peak_spacing_threshold = 16
# # sigma = 3.6
# #
# # pulse_color_map = {
# #     1.0: 'black',
# #     1.1: 'darkblue',
# #     1.3: 'green',
# #     1.6: 'orange',
# #     2.0: 'deeppink',
# #     2.3: 'red',
# # }
# #
# # manual_peak_indices = {
# #     ('CH0', 65.7, 1.6): [140,178,553,590],
# #     ('CH1', 65.7, 1.6): [130,177],
# # }
# #
# # data_by_channel = {
# #     "CH0": defaultdict(lambda: defaultdict(list)),
# #     "CH1": defaultdict(lambda: defaultdict(list))
# # }
# # pulse_by_voltage = defaultdict(lambda: defaultdict(float))
# #
# # # ========================================
# # # Helper Functions
# # # ========================================
# # def extract_gain_and_pulse_voltages(filename):
# #     match = re.search(r"_(\d+)_?(\d+)_gain_(\d+)_?(\d+)[Vv]?_pulse", filename)
# #     if match:
# #         gain = float(f"{match.group(1)}.{match.group(2)}")
# #         pulse = float(f"{match.group(3)}.{match.group(4)}")
# #         return gain, pulse
# #     return None, None
# #
# # def smooth_data(data, sigma=sigma):
# #     return gaussian_filter1d(data, sigma=sigma)
# #
# # def write_peak_data_to_file(peaks, data_cropped, filename, gain_voltage, pulse_voltage, channel):
# #     timestamp_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
# #     with open(filename, mode='w', newline='') as file:
# #         writer = csv.writer(file)
# #         writer.writerow([
# #             "Timestamp", "Channel", "Voltage Gain (V)", "Pulse Voltage (V)",
# #             "Peak Number", "Peak Index", "Peak Counts", "Index Difference"
# #         ])
# #         for i, peak_idx in enumerate(peaks):
# #             count_value = data_cropped[peak_idx]
# #             diff = peak_idx - peaks[i - 1] if i > 0 else "N/A"
# #             writer.writerow([
# #                 timestamp_str, channel, gain_voltage, pulse_voltage,
# #                 i + 1, peak_idx, count_value, diff
# #             ])
# #     print(f"✅ Peak data written to {filename}")
# #
# # def find_and_label_peaks(data, ax, label, crop_off_start, crop_off_end, color, style,
# #                          vertical_lines=False, channel=None, gain_voltage=None, pulse_voltage=None,
# #                          output_file=None, manual_peaks=None):
# #     data_cropped = data[crop_off_start:-crop_off_end]
# #     smoothed_data = smooth_data(data_cropped)
# #     x = np.arange(len(smoothed_data))
# #
# #     peaks, _ = find_peaks(smoothed_data, height=counts_threshold, distance=peak_spacing_threshold)
# #
# #     if manual_peaks is not None:
# #         peaks = np.unique(np.concatenate([peaks, np.array(manual_peaks)]))
# #
# #     ax.plot(x, smoothed_data, label=label, alpha=0.8, color=color, linestyle=style, linewidth=2)
# #     counts_at_peaks = smoothed_data[peaks]
# #     errors = np.sqrt(counts_at_peaks)
# #     ax.errorbar(x[peaks], counts_at_peaks, yerr=errors, fmt='o', color=color,
# #                 ecolor='gray', elinewidth=1, capsize=3, markersize=5, label=f"{label} Peaks")
# #
# #     if vertical_lines:
# #         for p in peaks:
# #             ax.axvline(x=p, color=color, linestyle='--', linewidth=1)
# #
# #     if output_file:
# #         write_peak_data_to_file(peaks, smoothed_data, output_file, gain_voltage, pulse_voltage, channel)
# #
# #     return peaks
# #
# # # ========================================
# # # Load Data Files with Filters
# # # ========================================
# # print("\n=== Loading Data Files ===\n")
# # for subdir, _, files in os.walk(data_dir):
# #     for file in files:
# #         if not file.startswith("CH") or "dark" in file.lower():
# #             continue
# #
# #         full_path = os.path.join(subdir, file)
# #         try:
# #             data = np.loadtxt(full_path, delimiter=',')
# #         except Exception as e:
# #             print(f"[ERROR] Could not load {full_path}: {e}")
# #             continue
# #
# #         gain_v, pulse_v = extract_gain_and_pulse_voltages(file)
# #         if gain_v is None:
# #             print(f"[SKIPPED] Could not parse voltages from: {file}")
# #             continue
# #
# #         # Filter based on global pulse/gain voltages
# #         if gain_voltages_to_plot and gain_v not in gain_voltages_to_plot:
# #             print(f"[SKIPPED] Gain voltage {gain_v}V not in gain_voltages_to_plot list.")
# #             continue
# #         if pulse_voltages_to_plot and pulse_v not in pulse_voltages_to_plot:
# #             print(f"[SKIPPED] Pulse voltage {pulse_v}V not in pulse_voltages_to_plot list.")
# #             continue
# #
# #         channel = "CH0" if "CH0" in file else "CH1"
# #         print(f"[LOADED] {channel} | Gain = {gain_v} V | Pulse = {pulse_v} V | from {file}")
# #         data_by_channel[channel][gain_v]["light"].append((data, pulse_v, file))
# #         pulse_by_voltage[channel][gain_v] = pulse_v
# #
# # # ========================================
# # # Plotting & Peak Detection
# # # ========================================
# # print("\n=== Plotting and Peak Detection ===\n")
# # subplot_counter = 1
# #
# # for channel, channel_data in data_by_channel.items():
# #     voltages_sorted = sorted(channel_data.keys())
# #
# #     fig, axes = plt.subplots(len(voltages_sorted), 1, figsize=(15, 4 * len(voltages_sorted)))
# #     axes = np.atleast_1d(axes)
# #
# #     for idx, gain_v in enumerate(voltages_sorted):
# #         ax = axes[idx]
# #         voltage_data = channel_data[gain_v]
# #
# #         if "light" in voltage_data:
# #             for data, pulse_v, src in voltage_data["light"]:
# #                 color = pulse_color_map.get(pulse_v, 'gray')
# #                 label = f"{pulse_v}V pulse"
# #                 print(f"Processing {channel} | Gain: {gain_v} V | Pulse: {pulse_v} V | File: {src}")
# #
# #                 manual_peaks = manual_peak_indices.get((channel, gain_v, pulse_v))
# #                 output_file = f"generated_peak_data_results/peak_data_{channel}_gain_{gain_v}V_pulse_{pulse_v}V.csv"
# #
# #                 find_and_label_peaks(
# #                     data=data,
# #                     ax=ax,
# #                     label=label,
# #                     crop_off_start=crop_off_start,
# #                     crop_off_end=crop_off_end,
# #                     color=color,
# #                     style='solid',
# #                     vertical_lines=vertical_lines,
# #                     channel=channel,
# #                     gain_voltage=gain_v,
# #                     pulse_voltage=pulse_v,
# #                     output_file=output_file,
# #                     manual_peaks=manual_peaks
# #                 )
# #
# #         ax.set_title(f"{channel} — {gain_v} V gain", fontsize=18)
# #         ax.set_xlabel("Index", fontsize=14)
# #         ax.set_ylabel("Counts", fontsize=14)
# #         ax.grid(True)
# #         ax.legend(fontsize=10)
# #
# #         subplot_counter += 1
# #
# #     plt.tight_layout()
# #     plt.show()
# #
# #
# # # import matplotlib
# # # matplotlib.use('TkAgg')  # For PyCharm interactivity
# # #
# # # import os
# # # import re
# # # import numpy as np
# # # import matplotlib.pyplot as plt
# # # from collections import defaultdict
# # # from scipy.signal import find_peaks
# # # from scipy.ndimage import gaussian_filter1d
# # # import csv
# # # from datetime import datetime
# # # from pathlib import Path
# # # import pandas as pd
# # #
# # # # ========================================
# # # # Parameters
# # # # ========================================
# # # data_dir = 'data-photon-counts-SiPM/20250507_baseline_data_for_coic_comparison'
# # # crop_off_start = 100
# # # crop_off_end = 3000
# # # vertical_lines = True
# # #
# # # counts_threshold = 100
# # # peak_spacing_threshold = 16
# # # sigma = 3.6
# # #
# # # pulse_color_map = {
# # #     1.0: 'black',
# # #     1.1: 'darkblue',
# # #     1.3: 'green',
# # #     1.6: 'orange',
# # #     2.0: 'deeppink',
# # #     2.3: 'red',
# # # }
# # #
# # # manual_peak_indices = {
# # #     ('CH0', 65.7, 1.6): [140,178,553,590],
# # #     ('CH1', 65.7, 1.6): [130,177],
# # # }
# # #
# # # data_by_channel = {
# # #     "CH0": defaultdict(lambda: defaultdict(list)),
# # #     "CH1": defaultdict(lambda: defaultdict(list))
# # # }
# # # pulse_by_voltage = defaultdict(lambda: defaultdict(float))
# # #
# # # # ========================================
# # # # Functions
# # # # ========================================
# # # def extract_gain_and_pulse_voltages(filename):
# # #     match = re.search(r"_(\d+)_?(\d+)_gain_(\d+)_?(\d+)[Vv]?_pulse", filename)
# # #     if match:
# # #         gain = float(f"{match.group(1)}.{match.group(2)}")
# # #         pulse = float(f"{match.group(3)}.{match.group(4)}")
# # #         return gain, pulse
# # #     return None, None
# # #
# # # def smooth_data(data, sigma=sigma):
# # #     return gaussian_filter1d(data, sigma=sigma)
# # #
# # # def write_peak_data_to_file(peaks, data_cropped, filename, gain_voltage, pulse_voltage, channel):
# # #     timestamp_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
# # #     with open(filename, mode='w', newline='') as file:
# # #         writer = csv.writer(file)
# # #         writer.writerow([
# # #             "Timestamp", "Channel", "Voltage Gain (V)", "Pulse Voltage (V)",
# # #             "Peak Number", "Peak Index", "Peak Counts", "Index Difference"
# # #         ])
# # #         for i, peak_idx in enumerate(peaks):
# # #             count_value = data_cropped[peak_idx]
# # #             diff = peak_idx - peaks[i - 1] if i > 0 else "N/A"
# # #             writer.writerow([
# # #                 timestamp_str, channel, gain_voltage, pulse_voltage,
# # #                 i + 1, peak_idx, count_value, diff
# # #             ])
# # #     print(f"✅ Peak data written to {filename}")
# # #
# # # def find_and_label_peaks(data, ax, label, crop_off_start, crop_off_end, color, style,
# # #                          vertical_lines=False, channel=None, gain_voltage=None, pulse_voltage=None,
# # #                          output_file=None, manual_peaks=None):
# # #     data_cropped = data[crop_off_start:-crop_off_end]
# # #     smoothed_data = smooth_data(data_cropped)
# # #     x = np.arange(len(smoothed_data))
# # #
# # #     peaks, _ = find_peaks(smoothed_data, height=counts_threshold, distance=peak_spacing_threshold)
# # #
# # #     if manual_peaks is not None:
# # #         peaks = np.unique(np.concatenate([peaks, np.array(manual_peaks)]))
# # #
# # #     ax.plot(x, smoothed_data, label=label, alpha=0.8, color=color, linestyle=style, linewidth=2)
# # #     counts_at_peaks = smoothed_data[peaks]
# # #     errors = np.sqrt(counts_at_peaks)
# # #     ax.errorbar(x[peaks], counts_at_peaks, yerr=errors, fmt='o', color=color,
# # #                 ecolor='gray', elinewidth=1, capsize=3, markersize=5, label=f"{label} Peaks")
# # #
# # #     if vertical_lines:
# # #         for p in peaks:
# # #             ax.axvline(x=p, color=color, linestyle='--', linewidth=1)
# # #
# # #     if output_file:
# # #         write_peak_data_to_file(peaks, smoothed_data, output_file, gain_voltage, pulse_voltage, channel)
# # #
# # #     return peaks
# # #
# # # # ========================================
# # # # Load Data Files
# # # # ========================================
# # # print("\n=== Loading Data Files ===\n")
# # # for subdir, _, files in os.walk(data_dir):
# # #     for file in files:
# # #         if not file.startswith("CH") or "dark" in file.lower():
# # #             continue
# # #
# # #         full_path = os.path.join(subdir, file)
# # #         try:
# # #             data = np.loadtxt(full_path, delimiter=',')
# # #         except Exception as e:
# # #             print(f"[ERROR] Could not load {full_path}: {e}")
# # #             continue
# # #
# # #         gain_v, pulse_v = extract_gain_and_pulse_voltages(file)
# # #         if gain_v is None:
# # #             print(f"[SKIPPED] Could not parse voltages from: {file}")
# # #             continue
# # #
# # #         channel = "CH0" if "CH0" in file else "CH1"
# # #         print(f"[LOADED] {channel} | Gain = {gain_v} V | Pulse = {pulse_v} V | from {file}")
# # #         data_by_channel[channel][gain_v]["light"].append((data, pulse_v, file))
# # #         pulse_by_voltage[channel][gain_v] = pulse_v
# # #
# # # # ========================================
# # # # Plotting & Peak Detection
# # # # ========================================
# # # print("\n=== Plotting and Peak Detection ===\n")
# # #
# # # subplot_counter = 1
# # #
# # # for channel, channel_data in data_by_channel.items():
# # #     voltages_sorted = sorted(channel_data.keys())
# # #
# # #     fig, axes = plt.subplots(len(voltages_sorted), 1, figsize=(15, 4 * len(voltages_sorted)))
# # #     axes = np.atleast_1d(axes)
# # #
# # #     for idx, gain_v in enumerate(voltages_sorted):
# # #         ax = axes[idx]
# # #         voltage_data = channel_data[gain_v]
# # #
# # #         if "light" in voltage_data:
# # #             for data, pulse_v, src in voltage_data["light"]:
# # #                 color = pulse_color_map.get(pulse_v, 'gray')
# # #                 label = f"{pulse_v}V pulse"
# # #                 print(f"Processing {channel} | Gain: {gain_v} V | Pulse: {pulse_v} V | File: {src}")
# # #
# # #                 manual_peaks = manual_peak_indices.get((channel, gain_v, pulse_v))
# # #                 output_file = f"generated_peak_data_results/peak_data_{channel}_gain_{gain_v}V_pulse_{pulse_v}V.csv"
# # #
# # #                 find_and_label_peaks(
# # #                     data=data,
# # #                     ax=ax,
# # #                     label=label,
# # #                     crop_off_start=crop_off_start,
# # #                     crop_off_end=crop_off_end,
# # #                     color=color,
# # #                     style='solid',
# # #                     vertical_lines=vertical_lines,
# # #                     channel=channel,
# # #                     gain_voltage=gain_v,
# # #                     pulse_voltage=pulse_v,
# # #                     output_file=output_file,
# # #                     manual_peaks=manual_peaks
# # #                 )
# # #
# # #         ax.set_title(f"{channel} — {gain_v} V gain", fontsize=18)
# # #         ax.set_xlabel("Index", fontsize=14)
# # #         ax.set_ylabel("Counts", fontsize=14)
# # #         ax.grid(True)
# # #         ax.legend(fontsize=10)
# # #
# # #         subplot_counter += 1
# # #
# # #     plt.tight_layout()
# # #     plt.show()
# # #
# # #     from pathlib import Path
# # #     import pandas as pd
# # #
# # #     # ✅ Get repo root path (quantum_optics_lab_job)
# # #     repo_root = Path(__file__).resolve().parents[0]  # Only up ONE level
# # #
# # #     # ✅ Correct folders inside repo
# # #     generated_data_dir = repo_root / 'generated_peak_data_results'
# # #     results_dir = repo_root / 'results-from-generated-data'
# # #     print(results_dir)
# # #     results_dir.mkdir(parents=True, exist_ok=True)
# # #
# # #     # ✅ Find peak_data_*.csv files
# # #     csv_files = list(generated_data_dir.glob('peak_data_*.csv'))
# # #
# # #     if not csv_files:
# # #         print(f"[WARNING] No peak_data_*.csv files found in {generated_data_dir}")
# # #     else:
# # #         print(f"Found {len(csv_files)} CSV files to combine.")
# # #
# # #         # ✅ Combine CSVs
# # #         combined_df = pd.concat(
# # #             [pd.read_csv(f).assign(SourceFile=f.name) for f in csv_files],
# # #             ignore_index=True
# # #         )
# # #
# # #         # ✅ Sort
# # #         combined_df = combined_df.sort_values(by=['Channel', 'Peak Index'], ascending=[True, True])
# # #
# # #         # ✅ Write output CSV to results-from-generated-data
# # #         combined_output_file = results_dir / 'all_peaks_combined_sorted.csv'
# # #         combined_df.to_csv(combined_output_file, index=False)
# # #
# # #         print(f"✅ Combined peak data written to: {combined_output_file}")
# # #
# # # # # ======================================
# # # # #         Combine & Sort Peak Data
# # # # # ========================================
# # # # print("\n=== Combining All Peak Data CSV Files ===\n")
# # # #
# # # # from pathlib import Path
# # # # import pandas as pd
# # # #
# # # # # Get repo root path dynamically
# # # # repo_root = Path(__file__).resolve().parents[1]
# # # #
# # # # # Define directories
# # # # generated_data_dir = repo_root / 'generated_peak_data_results'
# # # # results_dir = repo_root / 'results-from-generated-data'
# # # # results_dir.mkdir(parents=True, exist_ok=True)
# # # #
# # # # # Find all CSV files matching peak_data_*.csv
# # # # csv_files = list(generated_data_dir.glob('peak_data_*.csv'))
# # # #
# # # # if not csv_files:
# # # #     print(f"[WARNING] No peak_data_*.csv files found in {generated_data_dir}")
# # # # else:
# # # #     print(f"Found {len(csv_files)} CSV files to combine.")
# # # #
# # # #     # Load and concatenate all CSVs
# # # #     combined_df = pd.concat(
# # # #         [pd.read_csv(f).assign(SourceFile=f.name) for f in csv_files],
# # # #         ignore_index=True
# # # #     )
# # # #
# # # #     # Sort by Channel, Peak Index
# # # #     combined_df = combined_df.sort_values(
# # # #         by=['Channel', 'Peak Index'],
# # # #         ascending=[True, True]
# # # #     )
# # # #
# # # #     # Output file path
# # # #     combined_output_file = results_dir / 'all_peaks_combined_sorted.csv'
# # # #
# # # #     # Save combined CSV
# # # #     combined_df.to_csv(combined_output_file, index=False)
# # # #
# # # #     print(f"✅ Combined peak data written to {combined_output_file}")
# # # #
# # # # # # ========================================
# # # # # # Combine & Sort Peak Data
# # # # # # ========================================
# # # # # print("\n=== Combining and Sorting Peak Data Files ===\n")
# # # #
# # # # generated_data_dir = Path(__file__).resolve().parents[1] / 'generated_peak_data_results'
# # # # output_dir = Path(__file__).resolve().parents[1] / 'results-from-generated-data'
# # # # output_dir.mkdir(parents=True, exist_ok=True)
# # # #
# # # # csv_files = list(generated_data_dir.glob('peak_data_*.csv'))
# # # #
# # # # if not csv_files:
# # # #     print(f"[WARNING] No peak_data_*.csv files found in {generated_data_dir}")
# # # # else:
# # # #     print(f"Found {len(csv_files)} peak data CSV files. Combining now...")
# # # #
# # # #     df_list = []
# # # #     for csv_file in csv_files:
# # # #         df = pd.read_csv(csv_file)
# # # #         df['Source File'] = csv_file.name
# # # #         df_list.append(df)
# # # #
# # # #     combined_df = pd.concat(df_list, ignore_index=True)
# # # #     combined_df['Filtered'] = combined_df['Source File'].apply(lambda x: 'filtered' in x.lower())
# # # #
# # # #     combined_df = combined_df.sort_values(by=['Filtered', 'Channel', 'Peak Index'],
# # # #                                           ascending=[False, True, True])
# # # #
# # # #     combined_output_file = output_dir / 'all_peak_data_combined_sorted.csv'
# # # #     combined_df.to_csv(combined_output_file, index=False)
# # # #
# # # #     print(f"✅ Combined and sorted peak data saved to: {combined_output_file}")
# # #
# # #
# # #
# # #
# # # #
# # # # # REMOVE or comment this line when running in a headless environment (like here)
# # # # import matplotlib
# # # # from sympy.printing.pretty.pretty_symbology import line_width
# # # #
# # # # matplotlib.use('TkAgg')  # For PyCharm interactivity
# # # #
# # # # import os
# # # # import re
# # # # import numpy as np
# # # # import matplotlib.pyplot as plt
# # # # from collections import defaultdict
# # # # from scipy.signal import find_peaks
# # # # import math
# # # # from scipy.ndimage import gaussian_filter1d
# # # # import csv
# # # # from datetime import datetime
# # # # from analysis_single_dataset.combine_data_from_separate_directories_into_single_database import *
# # # #
# # # #
# # # # # ========================================
# # # # #         Parameters
# # # # #  Note: the data directory will be different project that coicdence analysis data directory.
# # # # # The peaks generated in this data directory are used to generate the addback data in the coincidence analysis data directory.
# # # # #
# # # # # ========================================
# # # # #data_dir = 'data-photon-counts-SiPM/20250428_more_light'
# # # #
# # # #
# # # #
# # # # data_dir = 'data-photon-counts-SiPM/20250507_baseline_data_for_coic_comparison'
# # # #
# # # # pulse_voltages_to_plot = [1.6]  # <- Edit this as needed
# # # # gain_voltages_to_plot = [65.7] # <- Edit this list as needed
# # # #
# # # # crop_off_start = 100
# # # # crop_off_end = 3000
# # # # vertical_lines = True
# # # #
# # # # # peak finding parameters
# # # # counts_threshold = 100
# # # # peak_spacing_threshold = 16
# # # # sigma = 3.6
# # # #
# # # # pulse_color_map = {
# # # #     1.0: 'black',
# # # #     1.1: 'darkblue',
# # # #     1.3: 'green',
# # # #     1.6: 'orange',
# # # #     2.0: 'deeppink',
# # # #     2.3: 'red',
# # # # }
# # # #
# # # # # settings for the 20250428_more_light data
# # # # manual_peak_indices = {
# # # #     # ('CH0', 65.7, 1.0): [242, 279],
# # # #     # ('CH0', 65.7, 1.3): [344, 380],
# # # #     # ('CH0', 65.7, 1.6): [415, 449,485],#4/28/25 dats
# # # #     ('CH0', 65.7, 1.6): [140,178,553,590],
# # # #     # ('CH0', 65.7, 2.0): [549, 583,616,656],
# # # #     # ('CH0', 65.8, 1.0): [250,289],
# # # #     # ('CH0', 65.8, 1.3): [365, 401],
# # # #     # ('CH0', 65.8, 1.6): [472, 509, 545],
# # # #     # ('CH0', 65.8, 2.0): [659, 697,733,775,810],
# # # #     # ('CH0', 65.9, 1.0): [252, 296],
# # # #     # ('CH0', 65.9, 1.3): [378, 415,461,505],
# # # #     # ('CH0', 65.9, 1.6): [491, 528, 571,609],
# # # #     # ('CH0', 65.9, 2.0): [723, 763, 798,840],
# # # #     # ('CH0', 66.0, 1.0): [256, 298,344],
# # # #     # ('CH0', 66.0, 1.3): [382, 425,470,509],
# # # #     # ('CH0', 66.0, 1.6): [521, 565, 612, 649],
# # # #     # ('CH0', 66.0, 2.0): [884, 924, 968, 1007,1044,1084,1128],
# # # #     #
# # # #
# # # #     # ('CH1', 65.7, 1.0): [260, 303,350],
# # # #     # ('CH1', 65.7, 1.3): [386, 430, 475,],
# # # #     # ('CH1', 65.7, 1.6): [519, 563,607,642],
# # # #      ('CH1', 65.7, 1.6): [130,177],
# # # #     # ('CH1', 65.7, 2.0): [730,777,817,860,909],
# # # #     # ('CH1', 65.8, 1.0): [260, 314,358],
# # # #     # ('CH1', 65.8, 1.3): [403, 448, 497],
# # # #     # ('CH1', 65.8, 1.6): [537, 580, 627,678],
# # # #     # ('CH1', 65.8, 2.0): [809, 860,902,949],
# # # #     # ('CH1', 65.9, 1.0): [263, 316,375,440],
# # # #     # ('CH1', 65.9, 1.3): [412, 464,519,559],
# # # #     # ('CH1', 65.9, 1.6): [551, 603,694,741],
# # # #     # ('CH1', 65.9, 2.0): [838,885,941],
# # # #     # ('CH1', 66.0, 1.0): [265,328,371,429],
# # # #     # ('CH1', 66.0, 1.3): [121,419,471,521,576],
# # # #     # ('CH1', 66.0, 1.6): [582,635,684,739,794],
# # # #     # ('CH1', 66.0, 2.0): [1044,1128],
# # # #
# # # # }
# # # #
# # # # #==========================================
# # # # #      Actual code doing the work
# # # # #==========================================
# # # #
# # # # data_by_channel = {
# # # #     "CH0": defaultdict(lambda: defaultdict(list)),
# # # #     "CH1": defaultdict(lambda: defaultdict(list))
# # # # }
# # # # pulse_by_voltage = defaultdict(lambda: defaultdict(float))
# # # #
# # # # def extract_gain_and_pulse_voltages(filename):
# # # #     match = re.search(r"_(\d+)_?(\d+)_gain_(\d+)_?(\d+)[Vv]?_pulse", filename)
# # # #     if match:
# # # #         gain = float(f"{match.group(1)}.{match.group(2)}")
# # # #         pulse = float(f"{match.group(3)}.{match.group(4)}")
# # # #         return gain, pulse
# # # #     return None, None
# # # #
# # # #
# # # # # def extract_gain_and_pulse_voltages(filename):
# # # # #     '''
# # # # #     Extract gain and pulse voltages from the filename.
# # # # #     :param filename: file name of the data file structured in such a way to parse the gain voltage and pulse height
# # # # #     :return: gain voltage (e.g 65.7V) and pulse height (e.g 1.0V)
# # # # #     '''
# # # # #     match = re.search(r"(\d+)_?(\d+)_gain_(\d+)_?(\d+)_pulse", filename)
# # # # #     if match:
# # # # #         gain = float(f"{match.group(1)}.{match.group(2)}")
# # # # #         pulse = float(f"{match.group(3)}.{match.group(4)}")
# # # # #         return gain, pulse
# # # # #     return None, None
# # # #
# # # # def smooth_data(data, sigma=sigma):
# # # #     '''
# # # #     Smooth the data using a Gaussian filter.
# # # #     :param data:
# # # #     :param sigma:
# # # #     :return:
# # # #     '''
# # # #     return gaussian_filter1d(data, sigma=sigma)
# # # #
# # # # def write_peak_data_to_file(peaks, data_cropped, filename, gain_voltage, pulse_voltage, channel):
# # # #     '''
# # # #     Write peak data to a CSV file.
# # # #     :param peaks:
# # # #     :param data_cropped:
# # # #     :param filename: file name to write to
# # # #     :param gain_voltage:
# # # #     :param pulse_voltage:
# # # #     :param channel:
# # # #     :return:
# # # #     '''
# # # #     timestamp_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
# # # #     with open(filename, mode='w', newline='') as file:
# # # #         writer = csv.writer(file)
# # # #         writer.writerow([
# # # #             "Timestamp", "Channel", "Voltage Gain (V)", "Pulse Voltage (V)",
# # # #             "Peak Number", "Peak Index", "Peak Counts", "Index Difference"
# # # #         ])
# # # #         for i, peak_idx in enumerate(peaks):
# # # #             count_value = data_cropped[peak_idx]
# # # #             diff = peak_idx - peaks[i - 1] if i > 0 else "N/A"
# # # #             writer.writerow([
# # # #                 timestamp_str, channel, gain_voltage, pulse_voltage,
# # # #                 i + 1, peak_idx, count_value, diff
# # # #             ])
# # # #     print(f"Peak data written to {filename}")
# # # #
# # # # def find_and_label_peaks(data, ax, label, crop_off_start, crop_off_end, color, style,
# # # #                          vertical_lines=False, print_peaks=True,
# # # #                          channel=None, gain_voltage=None, pulse_voltage=None,
# # # #                          output_file=None, manual_peaks=None):
# # # #     '''
# # # #     Find and label peaks in the data.
# # # #     :param data:
# # # #     :param ax:
# # # #     :param label:
# # # #     :param crop_off_start:
# # # #     :param crop_off_end:
# # # #     :param color:
# # # #     :param style:
# # # #     :param vertical_lines:
# # # #     :param print_peaks:
# # # #     :param channel:
# # # #     :param gain_voltage:
# # # #     :param pulse_voltage:
# # # #     :param output_file:
# # # #     :param manual_peaks:
# # # #     :return:
# # # #     '''
# # # #     data_cropped = data[crop_off_start:-crop_off_end]
# # # #     smoothed_data = smooth_data(data_cropped)
# # # #     x = np.arange(len(smoothed_data))
# # # #
# # # #     peaks, _ = find_peaks(
# # # #         smoothed_data,
# # # #         height=counts_threshold,
# # # #         distance=peak_spacing_threshold
# # # #     )
# # # #
# # # #     if manual_peaks is not None:
# # # #         peaks = np.concatenate([peaks, np.array(manual_peaks)])
# # # #         peaks = np.unique(peaks)
# # # #
# # # #     ax.plot(x, smoothed_data, label=label, alpha=0.8, color=color, linestyle=style,linewidth=2)
# # # #     counts_at_peaks = smoothed_data[peaks]
# # # #     errors = np.sqrt(counts_at_peaks)
# # # #     ax.errorbar(x[peaks], counts_at_peaks, yerr=errors, fmt='o', color=color,
# # # #                 ecolor='gray', elinewidth=1, capsize=3, markersize=5, label=f"{label} Peaks")
# # # #
# # # #     # Force legend display
# # # #     handles, labels = ax.get_legend_handles_labels()
# # # #     if handles:
# # # #         ax.legend(handles, labels, fontsize=8)
# # # #     else:
# # # #         print(f"[WARNING] No legend items found for subplot {subplot_counter}.")
# # # #     if output_file:
# # # #         write_peak_data_to_file(peaks, smoothed_data, output_file, gain_voltage, pulse_voltage, channel)
# # # #
# # # #     if vertical_lines:
# # # #         for p in peaks:
# # # #             ax.axvline(x=p, color=color, linestyle='--', linewidth=1)
# # # #     if print_peaks:
# # # #         print(f"\n[PEAK INDICES] {channel} | Gain: {gain_voltage} V | Pulse: {pulse_voltage} V")
# # # #         print("Peak # | Index | Counts")
# # # #         for i, peak_idx in enumerate(peaks):
# # # #             count_val = smoothed_data[peak_idx]
# # # #             print(f"{i+1:6} | {peak_idx:5} | {count_val:.2f}")
# # # #
# # # #
# # # #
# # # #     return peaks
# # # #
# # # # # ========================================
# # # # #         Load Data
# # # # # ========================================
# # # # print("\n=== Loading Data Files From Single Directory ===\n")
# # # # for subdir, _, files in os.walk(data_dir):
# # # #     for file in files:
# # # #         print(f"Subfolder: {subdir}      (Processing file: {file} )")
# # # #         if not file.startswith("CH") or "dark" in file.lower():
# # # #             continue
# # # #
# # # #         full_path = os.path.join(subdir, file)
# # # #         try:
# # # #             data = np.loadtxt(full_path, delimiter=',')
# # # #         except Exception as e:
# # # #             print(f"[ERROR] Could not load {full_path}: {e}")
# # # #             continue
# # # #
# # # #         gain_v, pulse_v = extract_gain_and_pulse_voltages(file)
# # # #         if gain_v is None:
# # # #             print(f"[SKIPPED] Could not parse voltages from: {file}")
# # # #             continue
# # # #
# # # #         channel = "CH0" if "CH0" in file else "CH1"
# # # #         print(f"[LOADED] {channel} | Gain = {gain_v} V | Pulse = {pulse_v} V | from {file}")
# # # #         data_by_channel[channel][gain_v]["light"].append((data, pulse_v, file))
# # # #         pulse_by_voltage[channel][gain_v] = pulse_v
# # # #
# # # # # ========================================
# # # # #         Plotting
# # # # # ========================================
# # # # print("\n=== Plotting Subplots and Logging Used Files ===\n")
# # # # subplot_counter = 1
# # # #
# # # # for channel, channel_data in data_by_channel.items():
# # # #     voltages_sorted = [v for v in sorted(channel_data.keys()) if gain_voltages_to_plot is None or v in gain_voltages_to_plot]
# # # #     if not voltages_sorted:
# # # #         print(f"[SKIP] No valid gain voltages found for {channel}.")
# # # #         continue
# # # #
# # # #     n_cols = 1
# # # #     n_rows = math.ceil(len(voltages_sorted) / n_cols)
# # # #
# # # #     fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 4 * n_rows))
# # # #
# # # #     # If only one subplot is created, axes is not an array—make it one for consistency
# # # #     if isinstance(axes, np.ndarray):
# # # #         axes = axes.flatten()
# # # #     else:
# # # #         axes = [axes]  # wrap single Axes object in a list
# # # #
# # # #     subplot_idx = 0
# # # #
# # # #     for gain_v in voltages_sorted:
# # # #         ax = axes[subplot_idx]
# # # #         voltage_data = channel_data[gain_v]
# # # #
# # # #         print(f"\n--- Subplot {subplot_counter}: {channel} | Gain = {gain_v} V ---")
# # # #         if "light" in voltage_data:
# # # #             for data, pulse_v, src in voltage_data["light"]:
# # # #                 if pulse_voltages_to_plot is not None and pulse_v not in pulse_voltages_to_plot:
# # # #                     continue
# # # #                 color = pulse_color_map.get(pulse_v, 'gray')
# # # #                 label = f"{pulse_v}V pulse"
# # # #                 print(f"  ➔ File: {src}, Pulse = {pulse_v}V")
# # # #
# # # #                 manual_peaks = manual_peak_indices.get((channel, gain_v, pulse_v))
# # # #                 output_file = f"generated_peak_data_results/peak_data_{channel}_gain_{gain_v}V_pulse_{pulse_v}V.csv"
# # # #
# # # #                 find_and_label_peaks(
# # # #                     data=data,
# # # #                     ax=ax,
# # # #                     label=label,
# # # #                     crop_off_start=crop_off_start,
# # # #                     crop_off_end=crop_off_end,
# # # #                     color=color,
# # # #                     style='solid',
# # # #                     print_peaks=True,
# # # #                     vertical_lines=vertical_lines,
# # # #                     channel=channel,
# # # #                     gain_voltage=gain_v,
# # # #                     pulse_voltage=pulse_v,
# # # #                     output_file=output_file,
# # # #                     manual_peaks=manual_peaks
# # # #                 )
# # # #
# # # #         ax.set_title(f"{channel} — {gain_v} V gain", fontsize=24)
# # # #         ax.set_xlabel("Index",fontsize=24)
# # # #         plt.tick_params(axis='x', labelsize=24)
# # # #         plt.tick_params(axis='y', labelsize=24)
# # # #         ax.set_ylabel("Counts",fontsize=24)
# # # #         ax.grid(True)
# # # #         ax.legend(fontsize=8)
# # # #
# # # #         subplot_counter += 1
# # # #         subplot_idx += 1
# # # #
# # # #     for j in range(subplot_idx, len(axes)):
# # # #         fig.delaxes(axes[j])
# # # #
# # # #     #fig.suptitle(f"{channel} — Light Data", fontsize=18)
# # # #     #plt.tight_layout(rect=[0, 0, 1, 0.95])
# # # #     plt.show()
# # # #
# # # #
# # # # # from datetime import datetime
# # # # # import csv
# # # # # import numpy as np
# # # #
# # # #
# # # # #
# # # # # # Prepare output CSV for weighted mean data
# # # # # weighted_means2_path = "weighted_means2.csv"
# # # # # with open(weighted_means2_path, mode='w', newline='') as wf:
# # # # #     writer = csv.writer(wf)
# # # # #     writer.writerow([
# # # # #         "Timestamp", "Channel", "Structure", "State",
# # # # #         "Coincidence", "Correlation Time", "File",
# # # # #         "Weighted Mean Index", "Weighted Mean Time"
# # # # #     ])
# # # # #
# # # # #     for (channel, structure), files in file_groups.items():
# # # # #         for file_path, correlation_time, coincidence, state in files:
# # # # #             with open(file_path, 'r') as f:
# # # # #                 data = [float(line.strip()) for line in f if line.strip()]
# # # # #                 if crop_data:
# # # # #                     data = data[crop_start_amount:-crop_end_amount]
# # # # #             weights = np.array(data)
# # # # #             indices = np.arange(len(data))
# # # # #             if weights.sum() > 0:
# # # # #                 weighted_mean_index = np.average(indices, weights=weights)
# # # # #                 weighted_mean_time = weighted_mean_index * time_per_sample
# # # # #                 timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
# # # # #                 writer.writerow([
# # # # #                     timestamp, channel, structure, state,
# # # # #                     coincidence, correlation_time, file_path.name,
# # # # #                     weighted_mean_index, weighted_mean_time
# # # # #                 ])
# # # #
# # # #
# # # # #
# # # # # # REMOVE or comment this line when running in a headless environment (like here)
# # # # # import matplotlib
# # # # # matplotlib.use('TkAgg')  # For PyCharm interactivity
# # # # #
# # # # # import os
# # # # # import re
# # # # # import numpy as np
# # # # # import matplotlib.pyplot as plt
# # # # # from collections import defaultdict
# # # # # from scipy.signal import find_peaks
# # # # # import math
# # # # # from scipy.ndimage import gaussian_filter1d
# # # # # import csv
# # # # # from datetime import datetime
# # # # #
# # # # # # ========================================
# # # # # #         Parameters
# # # # # # ========================================
# # # # # data_dir = 'data-photon-counts-SiPM/20250428_more_light'  # <- Edit this as needed
# # # # #
# # # # # pulse_voltages_to_plot = [1.0,1.3, 1.6, 2.0]  # <- Edit this as needed
# # # # # gain_voltages_to_plot = [65.7] # <- Edit this list as needed
# # # # #
# # # # # crop_off_start = 100
# # # # # crop_off_end = 2800
# # # # # vertical_lines = False
# # # # # counts_threshold = 100
# # # # # peak_spacing_threshold = 16
# # # # # sigma = 3.6
# # # # #
# # # # # pulse_color_map = {
# # # # #     1.0: 'black',
# # # # #     1.1: 'darkblue',
# # # # #     1.3: 'green',
# # # # #     1.6: 'orange',
# # # # #     2.0: 'deeppink',
# # # # #     2.3: 'red',
# # # # # }
# # # # #
# # # # # # settings for the 20250428_more_light data
# # # # # manual_peak_indices = {
# # # # #     ('CH0', 65.7, 1.0): [242, 279],
# # # # #     ('CH0', 65.7, 1.3): [344, 380],
# # # # #     ('CH0', 65.7, 1.6): [415, 449,485],
# # # # #     ('CH0', 65.7, 2.0): [549, 583,616,656],
# # # # #     ('CH0', 65.8, 1.0): [250,289],
# # # # #     ('CH0', 65.8, 1.3): [365, 401],
# # # # #     ('CH0', 65.8, 1.6): [472, 509, 545],
# # # # #     ('CH0', 65.8, 2.0): [659, 697,733,775,810],
# # # # #     ('CH0', 65.9, 1.0): [252, 296],
# # # # #     ('CH0', 65.9, 1.3): [378, 415,461,505],
# # # # #     ('CH0', 65.9, 1.6): [491, 528, 571,609],
# # # # #     ('CH0', 65.9, 2.0): [723, 763, 798,840],
# # # # #     ('CH0', 66.0, 1.0): [256, 298,344],
# # # # #     ('CH0', 66.0, 1.3): [382, 425,470,509],
# # # # #     ('CH0', 66.0, 1.6): [521, 565, 612, 649],
# # # # #     ('CH0', 66.0, 2.0): [884, 924, 968, 1007,1044,1084,1128],
# # # # #
# # # # #
# # # # #     ('CH1', 65.7, 1.0): [260, 303,350],
# # # # #     ('CH1', 65.7, 1.3): [386, 430, 475,],
# # # # #     ('CH1', 65.7, 1.6): [519, 563,607,642],
# # # # #     ('CH1', 65.7, 2.0): [730,777,817,860,909],
# # # # #     ('CH1', 65.8, 1.0): [260, 314,358],
# # # # #     ('CH1', 65.8, 1.3): [403, 448, 497],
# # # # #     ('CH1', 65.8, 1.6): [537, 580, 627,678],
# # # # #     ('CH1', 65.8, 2.0): [809, 860,902,949],
# # # # #     ('CH1', 65.9, 1.0): [263, 316,375,440],
# # # # #     ('CH1', 65.9, 1.3): [412, 464,519,559],
# # # # #     ('CH1', 65.9, 1.6): [551, 603,694,741],
# # # # #     ('CH1', 65.9, 2.0): [838,885,941],
# # # # #     ('CH1', 66.0, 1.0): [265,328,371,429],
# # # # #     ('CH1', 66.0, 1.3): [121,419,471,521,576],
# # # # #     ('CH1', 66.0, 1.6): [582,635,684,739,794],
# # # # #     # ('CH1', 66.0, 2.0): [1044,1128],
# # # # #
# # # # # }
# # # # #
# # # # # data_by_channel = {
# # # # #     "CH0": defaultdict(lambda: defaultdict(list)),
# # # # #     "CH1": defaultdict(lambda: defaultdict(list))
# # # # # }
# # # # # pulse_by_voltage = defaultdict(lambda: defaultdict(float))
# # # # #
# # # # # def extract_gain_and_pulse_voltages(filename):
# # # # #     '''
# # # # #     Extract gain and pulse voltages from the filename.
# # # # #     :param filename: file name of the data file structured in such a way to parse the gain voltage and pulse height
# # # # #     :return: gain voltage (e.g 65.7V) and pulse height (e.g 1.0V)
# # # # #     '''
# # # # #     match = re.search(r"(\d+)_?(\d+)_gain_(\d+)_?(\d+)_pulse", filename)
# # # # #     if match:
# # # # #         gain = float(f"{match.group(1)}.{match.group(2)}")
# # # # #         pulse = float(f"{match.group(3)}.{match.group(4)}")
# # # # #         return gain, pulse
# # # # #     return None, None
# # # # #
# # # # # def smooth_data(data, sigma=sigma):
# # # # #     '''
# # # # #     Smooth the data using a Gaussian filter.
# # # # #     :param data:
# # # # #     :param sigma:
# # # # #     :return:
# # # # #     '''
# # # # #     return gaussian_filter1d(data, sigma=sigma)
# # # # #
# # # # # def write_peak_data_to_file(peaks, data_cropped, filename, gain_voltage, pulse_voltage, channel):
# # # # #     '''
# # # # #     Write peak data to a CSV file.
# # # # #     :param peaks:
# # # # #     :param data_cropped:
# # # # #     :param filename: file name to write to
# # # # #     :param gain_voltage:
# # # # #     :param pulse_voltage:
# # # # #     :param channel:
# # # # #     :return:
# # # # #     '''
# # # # #     timestamp_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
# # # # #     with open(filename, mode='w', newline='') as file:
# # # # #         writer = csv.writer(file)
# # # # #         writer.writerow([
# # # # #             "Timestamp", "Channel", "Voltage Gain (V)", "Pulse Voltage (V)",
# # # # #             "Peak Number", "Peak Index", "Peak Counts", "Index Difference"
# # # # #         ])
# # # # #         for i, peak_idx in enumerate(peaks):
# # # # #             count_value = data_cropped[peak_idx]
# # # # #             diff = peak_idx - peaks[i - 1] if i > 0 else "N/A"
# # # # #             writer.writerow([
# # # # #                 timestamp_str, channel, gain_voltage, pulse_voltage,
# # # # #                 i + 1, peak_idx, count_value, diff
# # # # #             ])
# # # # #     print(f"Peak data written to {filename}")
# # # # #
# # # # # def find_and_label_peaks(data, ax, label, crop_off_start, crop_off_end, color, style,
# # # # #                          vertical_lines=False, print_peaks=False,
# # # # #                          channel=None, gain_voltage=None, pulse_voltage=None,
# # # # #                          output_file=None, manual_peaks=None):
# # # # #     '''
# # # # #     Find and label peaks in the data.
# # # # #     :param data:
# # # # #     :param ax:
# # # # #     :param label:
# # # # #     :param crop_off_start:
# # # # #     :param crop_off_end:
# # # # #     :param color:
# # # # #     :param style:
# # # # #     :param vertical_lines:
# # # # #     :param print_peaks:
# # # # #     :param channel:
# # # # #     :param gain_voltage:
# # # # #     :param pulse_voltage:
# # # # #     :param output_file:
# # # # #     :param manual_peaks:
# # # # #     :return:
# # # # #     '''
# # # # #     data_cropped = data[crop_off_start:-crop_off_end]
# # # # #     smoothed_data = smooth_data(data_cropped)
# # # # #     x = np.arange(len(smoothed_data))
# # # # #
# # # # #     peaks, _ = find_peaks(
# # # # #         smoothed_data,
# # # # #         height=counts_threshold,
# # # # #         distance=peak_spacing_threshold
# # # # #     )
# # # # #
# # # # #     if manual_peaks is not None:
# # # # #         peaks = np.concatenate([peaks, np.array(manual_peaks)])
# # # # #         peaks = np.unique(peaks)
# # # # #
# # # # #     ax.plot(x, smoothed_data, label=label, alpha=0.8, color=color, linestyle=style)
# # # # #     counts_at_peaks = smoothed_data[peaks]
# # # # #     errors = np.sqrt(counts_at_peaks)
# # # # #     ax.errorbar(x[peaks], counts_at_peaks, yerr=errors, fmt='o', color=color,
# # # # #                 ecolor='gray', elinewidth=1, capsize=3, markersize=5, label=f"{label} Peaks")
# # # # #
# # # # #     if output_file:
# # # # #         write_peak_data_to_file(peaks, smoothed_data, output_file, gain_voltage, pulse_voltage, channel)
# # # # #
# # # # #     if vertical_lines:
# # # # #         for p in peaks:
# # # # #             ax.axvline(x=p, color=color, linestyle='--', linewidth=1)
# # # # #
# # # # #     return peaks
# # # # #
# # # # # # ========================================
# # # # # #         Load Data
# # # # # # ========================================
# # # # # print("\n=== Loading Data Files From Single Directory ===\n")
# # # # # for subdir, _, files in os.walk(data_dir):
# # # # #     for file in files:
# # # # #         if not file.startswith("CH") or "dark" in file.lower():
# # # # #             continue
# # # # #
# # # # #         full_path = os.path.join(subdir, file)
# # # # #         try:
# # # # #             data = np.loadtxt(full_path, delimiter=',')
# # # # #         except Exception as e:
# # # # #             print(f"[ERROR] Could not load {full_path}: {e}")
# # # # #             continue
# # # # #
# # # # #         gain_v, pulse_v = extract_gain_and_pulse_voltages(file)
# # # # #         if gain_v is None:
# # # # #             print(f"[SKIPPED] Could not parse voltages from: {file}")
# # # # #             continue
# # # # #
# # # # #         channel = "CH0" if "CH0" in file else "CH1"
# # # # #         print(f"[LOADED] {channel} | Gain = {gain_v} V | Pulse = {pulse_v} V | from {file}")
# # # # #         data_by_channel[channel][gain_v]["light"].append((data, pulse_v, file))
# # # # #         pulse_by_voltage[channel][gain_v] = pulse_v
# # # # #
# # # # # # ========================================
# # # # # #         Plotting
# # # # # # ========================================
# # # # # print("\n=== Plotting Subplots and Logging Used Files ===\n")
# # # # # subplot_counter = 1
# # # # #
# # # # # for channel, channel_data in data_by_channel.items():
# # # # #     voltages_sorted = [v for v in sorted(channel_data.keys()) if gain_voltages_to_plot is None or v in gain_voltages_to_plot]
# # # # #     if not voltages_sorted:
# # # # #         print(f"[SKIP] No valid gain voltages found for {channel}.")
# # # # #         continue
# # # # #
# # # # #     n_cols = 1
# # # # #     n_rows = math.ceil(len(voltages_sorted) / n_cols)
# # # # #
# # # # #     fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 4 * n_rows))
# # # # #     #axes = axes.flatten()
# # # # #     subplot_idx = 0
# # # # #
# # # # #     for gain_v in voltages_sorted:
# # # # #         ax = axes[subplot_idx]
# # # # #         voltage_data = channel_data[gain_v]
# # # # #
# # # # #         print(f"\n--- Subplot {subplot_counter}: {channel} | Gain = {gain_v} V ---")
# # # # #         if "light" in voltage_data:
# # # # #             for data, pulse_v, src in voltage_data["light"]:
# # # # #                 if pulse_voltages_to_plot is not None and pulse_v not in pulse_voltages_to_plot:
# # # # #                     continue
# # # # #                 color = pulse_color_map.get(pulse_v, 'gray')
# # # # #                 label = f"{pulse_v}V pulse"
# # # # #                 print(f"  ➔ File: {src}, Pulse = {pulse_v}V")
# # # # #
# # # # #                 manual_peaks = manual_peak_indices.get((channel, gain_v, pulse_v))
# # # # #                 output_file = f"generated_peak_data_results/peak_data_{channel}_gain_{gain_v}V_pulse_{pulse_v}V.csv"
# # # # #
# # # # #                 find_and_label_peaks(
# # # # #                     data=data,
# # # # #                     ax=ax,
# # # # #                     label=label,
# # # # #                     crop_off_start=crop_off_start,
# # # # #                     crop_off_end=crop_off_end,
# # # # #                     color=color,
# # # # #                     style='solid',
# # # # #                     vertical_lines=vertical_lines,
# # # # #                     print_peaks=False,
# # # # #                     channel=channel,
# # # # #                     gain_voltage=gain_v,
# # # # #                     pulse_voltage=pulse_v,
# # # # #                     output_file=output_file,
# # # # #                     manual_peaks=manual_peaks
# # # # #                 )
# # # # #
# # # # #         ax.set_title(f"{channel} — {gain_v} V gain", fontsize=10)
# # # # #         ax.set_xlabel("Index")
# # # # #         ax.set_ylabel("Counts")
# # # # #         ax.grid(True)
# # # # #         ax.legend(fontsize=8)
# # # # #
# # # # #         subplot_counter += 1
# # # # #         subplot_idx += 1
# # # # #
# # # # #     for j in range(subplot_idx, len(axes)):
# # # # #         fig.delaxes(axes[j])
# # # # #
# # # # #     fig.suptitle(f"{channel} — Light Data", fontsize=18)
# # # # #     plt.tight_layout(rect=[0, 0, 1, 0.95])
# # # # #     plt.show()
# # # # #
# # # # # # from quick_single_data_set_analysis_tools.combine_data_from_separate_directories_into_single_database import *