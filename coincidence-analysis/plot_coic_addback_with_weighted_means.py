import matplotlib
matplotlib.use('TkAgg')  # For PyCharm interactivity

from pathlib import Path
import matplotlib.pyplot as plt
import csv
import re
import numpy as np
from datetime import datetime

script_name = Path(__file__).name  # ✅ Provenance tracking

# === SETTINGS ===
include_second_peaks = [3, 4, 5, 6, 7, 8]
crop_data = True
crop_start_amount = 600
crop_end_amount = 3100
data_directory = "20250507_more_peaks_compare_coicdence"
font_size = 24
font_size_legend = 14
time_per_sample = 1.0

peak_data = []

# === Weighted Mean Function ===
def calculate_weighted_mean(data, time_per_sample=1.0):
    if len(data) == 0 or np.sum(data) == 0:
        print("[WARNING] Empty or zero-sum data passed to weighted mean calculation.")
        return None, None, 0

    indices = np.arange(len(data))
    total_counts = np.sum(data)
    weighted_mean_index = np.average(indices, weights=data)
    weighted_mean_time = weighted_mean_index * time_per_sample

    return weighted_mean_index, weighted_mean_time, total_counts

# === PATHS ===
script_dir = Path(__file__).resolve().parent
data_dir = script_dir.parent / "data-photon-counts-SiPM" / data_directory

# === DISCOVER PEAK DIRECTORIES ===
peak_dirs = [subdir for subdir in data_dir.rglob("*") if subdir.is_dir() and subdir.name.startswith("peak")]

file_groups = {}
for peak_dir in peak_dirs:
    parts = peak_dir.name.split("_")
    first_peak = parts[0].replace("peak", "")
    second_peak = parts[1].replace("and", "")
    coincidence = f"Peak {first_peak} and {second_peak}"
    correlation_time = parts[2]
    state = next((word for word in ["filtered", "unfiltered", "raw"] if word in parts), "")

    data_files = list(peak_dir.glob("*.txt"))
    for file_path in data_files:
        if "AddBack" in file_path.name:
            channel_number = file_path.name.split("_")[1]
            group_key = (channel_number, "AddBack")
            file_groups.setdefault(group_key, []).append((file_path, correlation_time, coincidence, state))

# === PLOTTING & PEAK DATA COLLECTION ===
for (channel, structure), files in file_groups.items():
    plt.figure(figsize=(10, 6))

    for file_path, correlation_time, coincidence, state in files:
        match = re.search(r"Peak \d+ and (\d+)", coincidence)
        if match:
            second_peak_num = int(match.group(1))
            if second_peak_num not in include_second_peaks:
                continue
        else:
            continue

        data = np.loadtxt(file_path)
        if crop_data:
            data = data[crop_start_amount:-crop_end_amount]

        peak_value = np.max(data)
        peak_index = int(np.argmax(data))
        timestamp = peak_index * time_per_sample

        # ✅ Compute weighted mean for this curve
        weighted_mean_index, weighted_mean_time, total_counts = calculate_weighted_mean(data, time_per_sample)

        print(f"[{file_path.name}] Weighted Mean Index: {weighted_mean_index:.2f}, Time: {weighted_mean_time:.2f}, Total Counts: {total_counts:.2f}")

        peak_data.append({
            "time_ran":  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # ✅ timestampp,
            "correlation_time": correlation_time,
            "coincidence": coincidence,
            "state": state,
            "channel": channel,
            "structure": structure,
            "second_peak": second_peak_num,
            "peak_value": peak_value,
            "peak_index": peak_index,
            "file_used_in_analysis": file_path.name,
            "python_file_used_to_generate_this": script_name,
            "weighted_mean_index": weighted_mean_index,
            "weighted_mean_time": weighted_mean_time,
            "total_counts": total_counts,
            "timestamp": timestamp,
        })

        # Plot curve
        x_vals = np.arange(len(data))
        plt.plot(x_vals, data, label=f"{coincidence}, {correlation_time}", linewidth=3)

        # Plot weighted mean vertical line
        plt.axvline(x=weighted_mean_index, color='gray', linestyle='--', linewidth=2)

    plt.xlabel("Index", fontsize=font_size)
    plt.ylabel("Counts", fontsize=font_size)
    plt.title(f"{structure}, Channel {channel}", fontsize=font_size)
    plt.tick_params(axis='x', labelsize=font_size)
    plt.tick_params(axis='y', labelsize=font_size)
    plt.grid(True)

    handles, labels = plt.gca().get_legend_handles_labels()
    if handles:
        sorted_pairs = sorted(zip(handles, labels),
                              key=lambda x: (int(re.search(r"Peak \d+ and (\d+)", x[1]).group(1))
                                             if re.search(r"Peak \d+ and (\d+)", x[1]) else float('inf'),
                                             float(re.search(r",\s*([\d\.]+)", x[1]).group(1))
                                             if re.search(r",\s*([\d\.]+)", x[1]) else float('inf')))
        sorted_handles, sorted_labels = zip(*sorted_pairs)
        plt.legend(sorted_handles, sorted_labels, fontsize=font_size_legend)

    plt.tight_layout()
    plt.show()

# === FINAL OUTPUT CSV ===
output_file = script_dir / "processed_peak_data.csv"
peak_data_sorted = sorted(peak_data, key=lambda x: (x['channel'], x['state'] != 'filtered', x['second_peak']))

fieldnames = list(peak_data_sorted[0].keys())
with open(output_file, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(peak_data_sorted)

print(f"✅ Final peak data saved to {output_file}")

# import matplotlib
# matplotlib.use('TkAgg')  # For PyCharm interactivity
#
# from pathlib import Path
# import matplotlib.pyplot as plt
# import csv
# import re
# import numpy as np
# from datetime import datetime  # ✅ for timestamp
#
# script_name = Path(__file__).name  # ✅ For provenance tracking
#
# # === FILTER SETTINGS ===
# include_second_peaks = [3,4,5,6,7,8]
#
# # === SETTINGS ===
# crop_data = True
# crop_start_amount = 600
# crop_end_amount = 3100
# data_directory = "20250507_more_peaks_compare_coicdence"
# font_size = 24
# font_size_legend = 14
# vertical_lines = False
# time_per_sample = 1.0
#
# peak_data = []
#
# # === PATH SETUP ===
# script_dir = Path(__file__).resolve().parent
# data_dir = script_dir.parent / "data-photon-counts-SiPM" / data_directory
# weighted_csv_path = script_dir / "weighted_means.csv"
#
# print(f"Searching for subdirectories in: {data_dir}")
# peak_dirs = [subdir for subdir in data_dir.rglob("*") if subdir.is_dir() and subdir.name.startswith("peak")]
# print(f"Found peak directories: {[dir.name for dir in peak_dirs]}")
#
#
# file_groups = {}
# for peak_dir in peak_dirs:
#     folder_name = peak_dir.name
#     parts = folder_name.split("_")
#
#     first_peak = parts[0].replace("peak", "")
#     second_peak = parts[1].replace("and", "")
#     coincidence = f"Peak {first_peak} and {second_peak}"
#     correlation_time = parts[2]
#     state = next((word for word in ["filtered", "unfiltered", "raw"] if word in parts), "")
#
#     data_files = list(peak_dir.glob("*.txt"))
#     for file_path in data_files:
#         if "AddBack" in file_path.name:
#             channel_number = file_path.name.split("_")[1]
#             group_key = (channel_number, "AddBack")
#             file_groups.setdefault(group_key, []).append((file_path, correlation_time, coincidence, state))
#
# # === LOAD Weighted Means CSV & ADD SCRIPT NAME ===
# weighted_rows = []
# with open(weighted_csv_path, 'r') as wf:
#     reader = csv.DictReader(wf)
#     for row in reader:
#         row["weighted_mean_index"] = float(row["Weighted Mean Index"])
#         row["generated_by"] = script_name  # ✅ provenance
#         weighted_rows.append(row)
#
# # === OVERWRITE weighted_means.csv ===
# fieldnames = list(weighted_rows[0].keys())
# with open(weighted_csv_path, 'w', newline='') as wf:
#     writer = csv.DictWriter(wf, fieldnames=fieldnames)
#     writer.writeheader()
#     writer.writerows(weighted_rows)
# print(f"✅ Updated {weighted_csv_path} with 'generated_by' column ({script_name})")
#
# # === PLOTTING & PEAK DATA COLLECTION ===
# for (channel, structure), files in file_groups.items():
#     plt.figure(figsize=(10, 6))
#     for file_path, correlation_time, coincidence, state in files:
#         match = re.search(r"Peak \d+ and (\d+)", coincidence)
#         if match:
#             second_peak_num = int(match.group(1))
#             if second_peak_num not in include_second_peaks:
#                 continue
#         else:
#             continue
#
#         with open(file_path, 'r') as file:
#             data = [float(line.strip()) for line in file if line.strip()]
#             if crop_data:
#                 data = data[crop_start_amount:-crop_end_amount]
#
#         peak_value = max(data)
#         peak_index = data.index(peak_value)
#         timestamp = peak_index * time_per_sample
#
#         peak_data.append({
#             "time_ran": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # ✅ timestamp
#             "correlation_time": correlation_time,
#             "coincidence": coincidence,
#             "second_peak": second_peak_num,  # ✅ new column
#             "state": state,
#             "channel": channel,
#             "structure": structure,
#             "peak_value": peak_value,
#             "peak_index": peak_index,
#             "data_file_used_in_analysis": file_path.name,
#             "csv_this_is_generated_by": script_name,
#
#         })
#
#         x_vals = list(range(len(data)))
#         curve, = plt.plot(x_vals, data, label=f"{coincidence}, {correlation_time}", linewidth=3)
#         color = curve.get_color()
#
#         for row in weighted_rows:
#             if (row["File"] == file_path.name and
#                 row["Coincidence"] == coincidence and
#                 row["Correlation Time"] == correlation_time and
#                 row["State"] == state):
#                 plt.axvline(x=row["weighted_mean_index"], color=color, linestyle='--', linewidth=3)
#
#     plt.xlabel("Index", fontsize=font_size)
#     plt.ylabel("Counts", fontsize=font_size)
#     plt.title(f"{structure}, Channel {channel}", fontsize=font_size)
#     plt.tick_params(axis='x', labelsize=font_size)
#     plt.tick_params(axis='y', labelsize=font_size)
#     plt.grid(True)
#
#     handles, labels = plt.gca().get_legend_handles_labels()
#     if handles:
#         sorted_pairs = sorted(zip(handles, labels),
#                               key=lambda x: (int(re.search(r"Peak \d+ and (\d+)", x[1]).group(1))
#                                              if re.search(r"Peak \d+ and (\d+)", x[1]) else float('inf'),
#                                              float(re.search(r",\s*([\d\.]+)", x[1]).group(1))
#                                              if re.search(r",\s*([\d\.]+)", x[1]) else float('inf')))
#         sorted_handles, sorted_labels = zip(*sorted_pairs)
#         plt.legend(sorted_handles, sorted_labels, fontsize=font_size_legend)
#
#     plt.tight_layout()
#     plt.show()
#
# # === FINAL SORT & SAVE PEAK DATA CSV ===
# output_file = script_dir / "processed_peak_data.csv"
# peak_data_sorted = sorted(peak_data, key=lambda x: (x['channel'], x['second_peak'], x['state'] != 'filtered'))
#
# fieldnames = list(peak_data_sorted[0].keys())
# with open(output_file, 'w', newline='') as f:
#     writer = csv.DictWriter(f, fieldnames=fieldnames)
#     writer.writeheader()
#     writer.writerows(peak_data_sorted)
#
# print(f"✅ Final peak data saved to {output_file}")
