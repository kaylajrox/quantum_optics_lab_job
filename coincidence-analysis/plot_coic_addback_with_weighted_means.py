import matplotlib
matplotlib.use('TkAgg')  # For PyCharm interactivity

from pathlib import Path
import matplotlib.pyplot as plt
import csv
import re
import numpy as np

# === FILTER SETTINGS: Include only these second peaks ===
include_second_peaks = [3,4,5,6,7,8]

# =============================== SETTINGS ===============================
crop_data = True
crop_start_amount = 600
crop_end_amount = 3100
data_directory = "20250507_more_peaks_compare_coicdence"
font_size = 24
font_size_legend = 14
vertical_lines = False
time_per_sample = 1.0

peak_data = []

# ========================== FILE DISCOVERY ==============================

script_dir = Path(__file__).resolve().parent
print(script_dir)
data_dir = script_dir.parent / "data-photon-counts-SiPM" / data_directory

print(data_dir)
weighted_csv_path = script_dir / "weighted_means.csv"

print(f"Searching for subdirectories in: {data_dir}")
peak_dirs = [subdir for subdir in data_dir.rglob("*") if subdir.is_dir() and subdir.name.startswith("peak")]
print(f"Found peak directories: {[dir.name for dir in peak_dirs]}")

file_groups = {}

for peak_dir in peak_dirs:
    print(f"\nProcessing directory: {peak_dir}")
    folder_name = peak_dir.name
    parts = folder_name.split("_")

    first_peak = parts[0].replace("peak", "")
    second_peak = parts[1].replace("and", "")
    coincidence = f"Peak {first_peak} and {second_peak}"
    correlation_time = parts[2]
    state = next((word for word in ["filtered", "unfiltered", "raw"] if word in parts), "")

    data_files = list(peak_dir.glob("*.txt"))
    print(f"Found files: {[file.name for file in data_files]}")

    for file_path in data_files:
        if "AddBack" in file_path.name:
            channel_number = file_path.name.split("_")[1]
            group_key = (channel_number, "AddBack")
            file_groups.setdefault(group_key, []).append((file_path, correlation_time, coincidence, state))

# ===================== LOAD WEIGHTED MEANS FROM CSV =====================
weighted_rows = []
with open(weighted_csv_path, 'r') as wf:
    reader = csv.DictReader(wf)
    for row in reader:
        row["weighted_mean_index"] = float(row["Weighted Mean Index"])
        row["coincidence"] = row["Coincidence"]
        row["correlation_time"] = row["Correlation Time"]
        row["state"] = row["State"]
        row["file"] = row["File"]
        weighted_rows.append(row)

# ========================== PLOTTING & ANALYSIS ==========================

for (channel, structure), files in file_groups.items():
    print(f"\nPlotting group: {structure}, Channel {channel}")
    plt.figure(figsize=(10, 6))

    for file_path, correlation_time, coincidence, state in files:
        match = re.search(r"Peak \d+ and (\d+)", coincidence)
        if match:
            second_peak_num = int(match.group(1))
            if second_peak_num not in include_second_peaks:
                print(f"Skipping {coincidence} (second peak {second_peak_num} not in include list)")
                continue
        else:
            print(f"Could not extract second peak from label: {coincidence}")
            continue

        print(f"Loading file: {file_path}")
        with open(file_path, 'r') as file:
            data = [float(line.strip()) for line in file if line.strip()]
            print(f"Loaded {len(data)} data points")
            if crop_data:
                data = data[crop_start_amount:-crop_end_amount]
                print(f"Cropped to {len(data)} points")

            # === Histogram-style "area" under the curve ===
            total_counts = sum(data)

            # Extract peak number from the coincidence label
            match_peak = re.search(r"Peak \d+ and (\d+)", coincidence)
            second_peak = match_peak.group(1) if match_peak else "?"

            print(
                f"Channel {channel}, Peak {second_peak}, {state}, {correlation_time}: Total Counts = {total_counts:.2f}")

        peak_value = max(data)
        peak_index = data.index(peak_value)
        timestamp = peak_index * time_per_sample

        print(f"Peak: {peak_value:.2f} at index {peak_index}, time = {timestamp:.2f}")

        peak_data.append({
            "timestamp": timestamp,
            "correlation_time": correlation_time,
            "coincidence": coincidence,
            "state": state,
            "channel": channel,
            "structure": structure,
            "peak_value": peak_value,
            "peak_index": peak_index,
            "file": file_path.name,

        })

        x_vals = list(range(len(data)))
        curve, = plt.plot(x_vals, data, label=f"{coincidence}, {correlation_time}", linewidth=3)
        color = curve.get_color()

        # === Plot vertical line at weighted mean ===
        for row in weighted_rows:
            if (row["file"] == file_path.name and
                row["coincidence"] == coincidence and
                row["correlation_time"] == correlation_time and
                row["state"] == state):
                plt.axvline(x=row["weighted_mean_index"], color=color, linestyle='--',linewidth=3)

    plt.xlabel("Index", fontsize=font_size)
    plt.ylabel("Counts", fontsize=font_size)
    plt.title(f"{structure}, Channel {channel} ({state})", fontsize=font_size)
    plt.tick_params(axis='x', labelsize=font_size)
    plt.tick_params(axis='y', labelsize=font_size)
    plt.grid(True)

    handles, labels = plt.gca().get_legend_handles_labels()

    def get_sort_key(label):
        match_peak = re.search(r"Peak \d+ and (\d+)", label)
        second_peak = int(match_peak.group(1)) if match_peak else float('inf')

        match_time = re.search(r",\s*([\d\.]+)", label)
        corr_time = float(match_time.group(1)) if match_time else float('inf')

        return (second_peak, corr_time)

    if handles:
        sorted_pairs = sorted(zip(handles, labels), key=lambda x: get_sort_key(x[1]))
        sorted_handles, sorted_labels = zip(*sorted_pairs)
        plt.legend(sorted_handles, sorted_labels, fontsize=font_size_legend)

    plt.tight_layout()
    plt.show()
    print(f"Finished plotting group: {structure}, Channel {channel} ({state})")

