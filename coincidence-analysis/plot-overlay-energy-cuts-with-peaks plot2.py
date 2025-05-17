import matplotlib
matplotlib.use('TkAgg')  # For PyCharm interactivity

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import re

# === CONFIG ===
repo_root = Path(__file__).resolve().parents[1]
coic_data_dir = repo_root / "data-photon-counts-SiPM" / "20250507_more_peaks_compare_coicdence"
crop_start_amount = 100
crop_end_amount = 3000

# === Function to extract peak numbers from folder name ===
def extract_peak_numbers(folder_name):
    match = re.search(r"peak(\d+)_and(\d+)", folder_name)
    if match:
        return match.group(1), match.group(2)
    else:
        return None, None

# === Data storage ===
all_addback_data = []
all_ch0_data = []
all_ch1_data = []

# === Iterate over subfolders ===
for subfolder in sorted(coic_data_dir.iterdir()):
    if not subfolder.is_dir():
        continue

    # Only filtered folders
    if "filtered" not in subfolder.name:
        continue

    peak1, peak2 = extract_peak_numbers(subfolder.name)
    if not peak1:
        print(f"[SKIPPED] Could not parse peak numbers from {subfolder.name}")
        continue

    print(f"[PROCESSING] {subfolder.name} | Peak {peak1} & {peak2}")

    # === Iterate over data files in subfolder ===
    for file_path in sorted(subfolder.glob("*.txt")):
        try:
            data = np.loadtxt(file_path)
            data_cropped = data[crop_start_amount:-crop_end_amount]
            indices = np.arange(len(data_cropped))
        except Exception as e:
            print(f"[ERROR] Could not load {file_path}: {e}")
            continue

        filename = file_path.name
        label = f"Peak {peak1} & {peak2}"

        if "@AddBack" in filename:
            all_addback_data.append((indices, data_cropped, label))
        elif "CH0@" in filename:
            all_ch0_data.append((indices, data_cropped, label))
        elif "CH1@" in filename:
            all_ch1_data.append((indices, data_cropped, label))

# === Split AddBack into >5000 and <=5000 groups ===
addback_high = []
addback_low = []

for indices, values, label in all_addback_data:
    if np.max(values) > 5100:
        addback_high.append((indices, values, label))
    else:
        addback_low.append((indices, values, label))

# === Plot AddBack curves with max > 5100 ===
if addback_high:
    plt.figure(figsize=(12, 7))
    for indices, values, label in addback_high:
        plt.plot(indices, values, lw=2, label=label)
    plt.xlabel("Index")
    plt.ylabel("Value")
    plt.title("AddBack Curves (Max > 5100, Filtered)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

# === Plot AddBack curves with max <= 5000 ===
if addback_low:
    plt.figure(figsize=(12, 7))
    for indices, values, label in addback_low:
        plt.plot(indices, values, lw=2, label=label)
    plt.xlabel("Index")
    plt.ylabel("Value")
    plt.title("AddBack Curves (Max <= 5100, Filtered)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

# === Plot all CH0 curves together ===
if all_ch0_data:
    plt.figure(figsize=(12, 7))
    for indices, values, label in all_ch0_data:
        plt.plot(indices, values, lw=2, label=label)
    plt.xlabel("Index")
    plt.ylabel("Value")
    plt.title("All CH0 Curves (Filtered)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

# === Plot all CH1 curves together ===
if all_ch1_data:
    plt.figure(figsize=(12, 7))
    for indices, values, label in all_ch1_data:
        plt.plot(indices, values, lw=2, label=label)
    plt.xlabel("Index")
    plt.ylabel("Value")
    plt.title("All CH1 Curves (Filtered)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()



# import matplotlib
# matplotlib.use('TkAgg')  # For PyCharm interactivity
#
# import numpy as np
# import matplotlib.pyplot as plt
# from pathlib import Path
# import re
#
# # === CONFIG ===
# repo_root = Path(__file__).resolve().parents[1]
# coic_data_dir = repo_root / "data-photon-counts-SiPM" / "20250507_more_peaks_compare_coicdence"
# crop_start_amount = 100
# crop_end_amount = 3000
#
# # === Function to extract peak numbers ===
# def extract_peak_numbers(folder_name):
#     match = re.search(r"peak(\d+)_and(\d+)", folder_name)
#     if match:
#         return match.group(1), match.group(2)
#     else:
#         return None, None
#
# # === Data storage ===
# all_addback_data = []
# all_ch0_data = []
# all_ch1_data = []
#
# # === Iterate over subfolders ===
# for subfolder in sorted(coic_data_dir.iterdir()):
#     if not subfolder.is_dir():
#         continue
#
#     # Only filtered folders
#     if "filtered" not in subfolder.name:
#         continue
#
#     peak1, peak2 = extract_peak_numbers(subfolder.name)
#     if not peak1:
#         print(f"[SKIPPED] Could not parse peak numbers from {subfolder.name}")
#         continue
#
#     print(f"[PROCESSING] {subfolder.name} | Peak {peak1} & {peak2}")
#
#     # === Iterate over files in subfolder ===
#     for file_path in sorted(subfolder.glob("*.txt")):
#         try:
#             data = np.loadtxt(file_path)
#             data_cropped = data[crop_start_amount:-crop_end_amount]
#             indices = np.arange(len(data_cropped))
#         except Exception as e:
#             print(f"[ERROR] Could not load {file_path}: {e}")
#             continue
#
#         filename = file_path.name
#         label = f"Peak {peak1} & {peak2}"
#
#         if "@AddBack" in filename:
#             all_addback_data.append((indices, data_cropped, label))
#         elif "CH0@" in filename:
#             all_ch0_data.append((indices, data_cropped, label))
#         elif "CH1@" in filename:
#             all_ch1_data.append((indices, data_cropped, label))
#
# # === Plot AddBack ===
# if all_addback_data:
#     plt.figure(figsize=(12, 7))
#     for indices, values, label in all_addback_data:
#         plt.plot(indices, values, lw=2, label=label)
#     plt.xlabel("Index")
#     plt.ylabel("Value")
#     plt.title(f"All AddBack Curves (Filtered)")
#     plt.grid(True)
#     plt.legend()
#     plt.tight_layout()
#     plt.show()
#
# # === Plot CH0 ===
# if all_ch0_data:
#     plt.figure(figsize=(12, 7))
#     for indices, values, label in all_ch0_data:
#         plt.plot(indices, values, lw=2, label=label)
#     plt.xlabel("Index")
#     plt.ylabel("Value")
#     plt.title(f"All CH0 Curves (Filtered)")
#     plt.grid(True)
#     plt.legend()
#     plt.tight_layout()
#     plt.show()
#
# # === Plot CH1 ===
# if all_ch1_data:
#     plt.figure(figsize=(12, 7))
#     for indices, values, label in all_ch1_data:
#         plt.plot(indices, values, lw=2, label=label)
#     plt.xlabel("Index")
#     plt.ylabel("Value")
#     plt.title(f"All CH1 Curves (Filtered)")
#     plt.grid(True)
#     plt.legend()
#     plt.tight_layout()
#     plt.show()
