import matplotlib
matplotlib.use('TkAgg')

from pathlib import Path
import matplotlib.pyplot as plt
import csv
import re
import numpy as np
from datetime import datetime

# === SETTINGS ===
include_second_peaks = list(range(1, 11))
crop_data = True
crop_start_amount = 100
crop_end_amount = 3000

font_size = 24
font_size_legend = 14
vertical_lines = False
time_per_sample = 1.0

peak_data = []
weighted_rows = []
script_dir = Path(__file__).resolve().parent
data_dir = script_dir.parent / parent_data_directory / data_directory

print(f"Searching in: {data_dir}")
peak_dirs = [d for d in data_dir.rglob("*") if d.is_dir() and d.name.startswith("peak")]

file_groups = {}

for peak_dir in peak_dirs:
    parts = peak_dir.name.split("_")
    if len(parts) < 3:
        continue
    first_peak = parts[0].replace("peak", "")
    second_peak = parts[1].replace("and", "")
    coincidence = f"Peak {first_peak} and {second_peak}"
    correlation_time = parts[2]
    state = next((s for s in ["filtered", "unfiltered", "raw"] if s in parts), "")

    for file_path in peak_dir.glob("*.txt"):
        name = file_path.name
        if "CH0" in name:
            channel = "CH0"
        elif "CH1" in name:
            channel = "CH1"
        else:
            continue

        structure = "AddBack" if "AddBack" in name else "CH"
        key = (channel, state)
        file_groups.setdefault(key, []).append((file_path, correlation_time, coincidence, structure))

# === PLOT ===
for (channel, state), files in file_groups.items():
    print(f"\nPlotting: {channel}, {state}")
    plt.figure(figsize=(10, 6))

    for file_path, correlation_time, coincidence, structure in files:
        match = re.search(r"Peak \d+ and (\d+)", coincidence)
        if not match or int(match.group(1)) not in include_second_peaks:
            continue

        with open(file_path, 'r') as f:
            data = [float(line.strip()) for line in f if line.strip()]

        if crop_data:
            data = data[crop_start_amount:-crop_end_amount]

        peak_val = max(data)
        peak_idx = data.index(peak_val)
        timestamp = peak_idx * time_per_sample

        print(f"{file_path.name} → Peak {peak_val:.1f} at {peak_idx} ({timestamp:.1f})")

        style = '--' if structure == "AddBack" else '-'
        x = np.arange(len(data))
        line, = plt.plot(x, data, style, label=f"{structure}: {coincidence}, {correlation_time}", linewidth=3)

        if vertical_lines:
            plt.axvline(x=peak_idx, color=line.get_color(), linestyle='--')

        weights = np.array(data)
        indices = np.arange(len(data))
        if weights.sum() > 0:
            mean_idx = np.average(indices, weights=weights)
            mean_time = mean_idx * time_per_sample
            weighted_rows.append({
                "file": file_path.name,
                "coincidence": coincidence,
                "correlation_time": correlation_time,
                "state": state,
                "channel": channel,
                "structure": structure,
                "weighted_mean_index": mean_idx,
                "weighted_mean_time": mean_time
            })

    plt.xlabel("Index", fontsize=font_size)
    plt.ylabel("Counts", fontsize=font_size)
    plt.title(f"{channel} — {state}", fontsize=font_size)
    plt.tick_params(axis='x', labelsize=font_size)
    plt.tick_params(axis='y', labelsize=font_size)
    plt.grid(True)

    handles, labels = plt.gca().get_legend_handles_labels()
    def sort_key(lbl):
        m1 = re.search(r"Peak \d+ and (\d+)", lbl)
        m2 = re.search(r",\s*([\d\.]+)", lbl)
        return (int(m1.group(1)) if m1 else float('inf'), float(m2.group(1)) if m2 else float('inf'))

    if handles:
        sorted_hl = sorted(zip(handles, labels), key=lambda x: sort_key(x[1]))
        h_sorted, l_sorted = zip(*sorted_hl)
        plt.legend(h_sorted, l_sorted, fontsize=font_size_legend)

    plt.tight_layout()
    plt.show()

# === EXPORT CSV ===
def extract_second_peak(coinc):
    m = re.search(r"Peak \d+ and (\d+)", coinc)
    return int(m.group(1)) if m else float('inf')

def extract_time_num(corr):
    m = re.match(r"(\d+(?:\.\d+)?)", corr)
    return float(m.group(1)) if m else float('inf')

state_priority = {"filtered": 0, "unfiltered": 1, "raw": 2}

rows_sorted = sorted(weighted_rows, key=lambda r: (
    r["channel"],
    state_priority.get(r["state"], 99),
    extract_second_peak(r["coincidence"]),
    extract_time_num(r["correlation_time"])
))

csv_path = script_dir / "CH_coic_data.csv"
with open(csv_path, 'w', newline='') as wf:
    writer = csv.writer(wf)
    writer.writerow(["File", "Coincidence", "Correlation Time", "State", "Channel", "Structure", "Weighted Mean Index", "Weighted Mean Time"])
    for row in rows_sorted:
        writer.writerow([
            row["file"], row["coincidence"], row["correlation_time"], row["state"],
            row["channel"], row["structure"], row["weighted_mean_index"], row["weighted_mean_time"]
        ])

print(f"\n✅ Saved weighted mean data to: {csv_path}")


# import matplotlib
# matplotlib.use('TkAgg')  # For PyCharm interactivity
#
# from pathlib import Path
# import matplotlib.pyplot as plt
# import csv
# import re
# import numpy as np
#
# # === FILTER SETTINGS: Include only these second peaks ===
# include_second_peaks = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
#
# # === CONFIG ===
# crop_data = True
# crop_start_amount = 600
# crop_end_amount = 3150
# parent_data_directory = "data-photon-counts-SiPM"
# data_directory = "20250507_more_peaks_compare_coicdence"
# font_size = 24
# font_size_legend = 14
# vertical_lines = False
# time_per_sample = 1.0
#
# # === Init ===
# peak_data = []
# weighted_rows = []
# script_dir = Path(__file__).resolve().parent
# data_dir = script_dir.parent / parent_data_directory / data_directory
#
# # === Discover directories ===
# print(f"Searching for subdirectories in: {data_dir}")
# peak_dirs = [subdir for subdir in data_dir.rglob("*") if subdir.is_dir() and subdir.name.startswith("peak")]
# print(f"Found peak directories: {[dir.name for dir in peak_dirs]}")
#
# file_groups = {}
#
# for peak_dir in peak_dirs:
#     folder_name = peak_dir.name
#     print(f"\nProcessing folder: {folder_name}")
#     parts = folder_name.split("_")
#
#     first_peak = parts[0].replace("peak", "")
#     second_peak = parts[1].replace("and", "")
#     coincidence = f"Peak {first_peak} and {second_peak}"
#     correlation_time = parts[2]
#     state = next((word for word in ["filtered", "unfiltered", "raw"] if word in parts), "")
#
#     data_files = list(peak_dir.glob("*.txt"))
#     print(f"Found files: {[file.name for file in data_files]}")
#
#     for file_path in data_files:
#         name = file_path.name
#         if "CH0" in name:
#             channel = "CH0"
#         elif "CH1" in name:
#             channel = "CH1"
#         else:
#             continue  # Skip unrecognized files
#
#         structure = "AddBack" if "AddBack" in name else "CH"
#         key = (channel, structure)
#         file_groups.setdefault(key, []).append((file_path, correlation_time, coincidence, state))
#
# # === Plotting ===
# for (channel, structure), files in file_groups.items():
#     print(f"\n📊 Plotting group: {structure}, Channel {channel}")
#     plt.figure(figsize=(10, 6))
#
#     for file_path, correlation_time, coincidence, state in files:
#         # Filter by peak #
#         match = re.search(r"Peak \d+ and (\d+)", coincidence)
#         if match:
#             second_peak_num = int(match.group(1))
#             if second_peak_num not in include_second_peaks:
#                 print(f"Skipping {coincidence} (second peak {second_peak_num} not in include list)")
#                 continue
#         else:
#             print(f"Could not extract second peak from label: {coincidence}")
#             continue
#
#         print(f"Loading file: {file_path.name}")
#         with open(file_path, 'r') as f:
#             data = [float(line.strip()) for line in f if line.strip()]
#
#         if crop_data:
#             data = data[crop_start_amount:-crop_end_amount]
#
#         peak_value = max(data)
#         peak_index = data.index(peak_value)
#         timestamp = peak_index * time_per_sample
#         print(f"  ➤ Peak: {peak_value:.2f} at index {peak_index}, time = {timestamp:.2f}")
#
#         x_vals = np.arange(len(data))
#         line_style = '--' if structure == "AddBack" else '-'
#         curve, = plt.plot(x_vals, data, line_style, label=f"{coincidence}, {correlation_time}", linewidth=3)
#         color = curve.get_color()
#
#         if vertical_lines:
#             plt.axvline(x=peak_index, color=color, linestyle='--', label=f"Peak @ {peak_index}")
#             plt.text(peak_index, peak_value, f"{peak_value:.2f}", color=color, fontsize=8)
#
#         # Weighted mean
#         weights = np.array(data)
#         indices = np.arange(len(data))
#         if weights.sum() > 0:
#             weighted_mean_index = np.average(indices, weights=weights)
#             weighted_mean_time = weighted_mean_index * time_per_sample
#             print(f"  ➤ Weighted mean index: {weighted_mean_index:.2f}, time: {weighted_mean_time:.2f}")
#
#             weighted_rows.append({
#                 "file": file_path.name,
#                 "coincidence": coincidence,
#                 "correlation_time": correlation_time,
#                 "state": state,
#                 "channel": channel,
#                 "structure": structure,
#                 "weighted_mean_index": weighted_mean_index,
#                 "weighted_mean_time": weighted_mean_time
#             })
#
#     # Final plot styling
#     plt.xlabel("Index", fontsize=font_size)
#     plt.ylabel("Counts", fontsize=font_size)
#     plt.title(f"{channel} — {state}", fontsize=font_size)
#     plt.tick_params(axis='x', labelsize=font_size)
#     plt.tick_params(axis='y', labelsize=font_size)
#     plt.grid(True)
#
#     handles, labels = plt.gca().get_legend_handles_labels()
#     def get_sort_key(label):
#         match_peak = re.search(r"Peak \d+ and (\d+)", label)
#         second_peak = int(match_peak.group(1)) if match_peak else float('inf')
#         match_time = re.search(r",\s*([\d\.]+)", label)
#         corr_time = float(match_time.group(1)) if match_time else float('inf')
#         return (second_peak, corr_time)
#
#     if handles:
#         sorted_pairs = sorted(zip(handles, labels), key=lambda x: get_sort_key(x[1]))
#         sorted_handles, sorted_labels = zip(*sorted_pairs)
#         plt.legend(sorted_handles, sorted_labels, fontsize=font_size_legend)
#
#     plt.tight_layout()
#     plt.show()
#
# # === Save Weighted Means to CSV ===
# def extract_numeric_time(corr_time):
#     match = re.match(r"(\d+(?:\.\d+)?)", corr_time)
#     return float(match.group(1)) if match else float('inf')
#
# def extract_second_peak_number(coincidence_str):
#     match = re.search(r"Peak \d+ and (\d+)", coincidence_str)
#     return int(match.group(1)) if match else float('inf')
#
# state_priority = {"filtered": 0, "unfiltered": 1, "raw": 2}
# weighted_rows_sorted = sorted(
#     weighted_rows,
#     key=lambda row: (
#         extract_second_peak_number(row["coincidence"]),
#         row["channel"],
#         extract_numeric_time(row["correlation_time"]),
#         state_priority.get(row["state"], 99)
#     )
# )
#
# weighted_csv_path = script_dir / "weighted_means.csv"
# with open(weighted_csv_path, 'w', newline='') as wf:
#     writer = csv.writer(wf)
#     writer.writerow([
#         "File", "Coincidence", "Correlation Time", "State",
#         "Channel", "Structure", "Weighted Mean Index", "Weighted Mean Time"
#     ])
#     for row in weighted_rows_sorted:
#         writer.writerow([
#             row["file"],
#             row["coincidence"],
#             row["correlation_time"],
#             row["state"],
#             row["channel"],
#             row["structure"],
#             row["weighted_mean_index"],
#             row["weighted_mean_time"]
#         ])
#
# print(f"\n✅ Sorted and saved weighted means to: {weighted_csv_path}")
#
#
#
# # # see what single file looks like
# #
# # import matplotlib
# # matplotlib.use('TkAgg')  # For PyCharm interactivity
# #
# # from pathlib import Path
# # import numpy as np
# # import matplotlib.pyplot as plt
# #
# # # === USER CONFIGURATION ===
# # data_folder_name = "20250507_more_peaks_compare_coicdence"
# # filename = "CH1@DT5720B_75_EspectrumF_peak_4_and4_750_ns_20250507_151921.txt"
# # subfolder_name = "peak4_and4_750ns_correlation_window_65_7_gain_1_6_pulse_60s_filtered"
# # crop_start_amount = 200
# # crop_end_amount = 3600
# #
# # # === PATH SETUP ===
# # repo_root = Path(__file__).resolve().parents[1]
# # base_data_dir = repo_root / "data-photon-counts-SiPM" / data_folder_name
# # subfolder_path = base_data_dir / subfolder_name
# # file_path = subfolder_path / filename
# #
# # # === LOAD DATA ===
# # print(f"Loading from: {file_path}")
# # assert file_path.exists(), f"File not found: {file_path}"
# # data = np.loadtxt(file_path)
# #
# # # === CROP DATA ===
# # # Crop data and generate matching index array
# # data_cropped = data[crop_start_amount:-crop_end_amount]
# # indices = np.arange(len(data_cropped))
# #
# #
# # # === PLOT ===
# # plt.figure(figsize=(10, 6))
# # plt.plot(indices, data_cropped, lw=2)
# # plt.xlabel("Index")
# # plt.ylabel("Value")
# # plt.title(f"Cropped Plot of {filename}")
# # plt.grid(True)
# # plt.tight_layout()
# # plt.show()
# #
# #
# #
