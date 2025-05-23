import matplotlib
matplotlib.use('TkAgg')  # Use TkAgg backend for interactivity in PyCharm

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import re
import matplotlib.ticker as ticker

#==============================================================================
#==============================================================================
#==================== USER DEFINED PARAMETERS   ===============================
#==============================================================================
#==============================================================================

# === DIRECTORY CONFIGURATION ===
repo_root = Path(__file__).resolve().parents[2]
coic_data_dir = repo_root / "data-photon-counts-SiPM" / "20250507_more_peaks_compare_coicdence"
baseline_data_dir = repo_root / "data-photon-counts-SiPM" / "20250507_baseline_data_for_coic_comparison" / "65_7_gain_1_6_pulse_60s"


# WARNING: CAN NEVER EXCLUDE PEAK 4 (ORIGINAL PEAK YOUR ARE COMPARING TO)
exclude_peak_numbers = ["1","2","5","7","9","10"]  # Peaks to exclude
crop_start_amount = 145  # How much to crop from start of signal
crop_end_amount = 3200  # How much to crop from end of signal
font_size = 24  # Font size for plots

# change this to compare overlay with smaller peak heights
baseline_multiplier_cap = 5  # Max allowed scaling of baseline overlay

# Flags to enable/disable plotting of data types
plot_unfiltered = False
plot_raw = False

#==============================================================================
#==============================================================================
#================================== Actual Code ===============================
#==============================================================================
#==============================================================================
# === DATA STORAGE ===
data_store = {
    'Filtered': {'CH0': [], 'CH1': []},
    'Unfiltered': {'CH0': [], 'CH1': []},
    'Raw': {'CH0': [], 'CH1': []},
    'AB Filtered': {'CH0': [], 'CH1': []},
}
baseline_store = {'CH0': [], 'CH1': []}
label_counts = {}  # Track duplicates
global_plot_index = 0

print(f"[DEBUG] Baseline directory path: {baseline_data_dir}")
print(f"[DEBUG] Coincidence directory path: {coic_data_dir}")

# === LOAD BASELINE FILES ===
for file_path in baseline_data_dir.glob("*.txt"):
    filename = file_path.name
    if not filename.startswith("CH0@") and not filename.startswith("CH1@"):
        continue
    try:
        data = np.loadtxt(file_path)
        # Perform cropping
        indices_cropped = np.arange(len(data))[crop_start_amount:-crop_end_amount]
        data_cropped = data[crop_start_amount:-crop_end_amount]

        # Check if cropped data is empty
        if data_cropped.size == 0:
            print(
                f"[WARNING] Cropped data is empty after applying crop_start_amount={crop_start_amount} and crop_end_amount={crop_end_amount}. Skipping file.")
        else:
            # Round data to the nearest integer
            data_cropped = np.round(data_cropped).astype(int)
            print(f"[DEBUG] Cropped data (rounded): {data_cropped[:10]}... (size: {data_cropped.size})")
        channel = "CH0" if "CH0@" in filename else "CH1"
        label = f"Baseline ({channel})"
        baseline_store[channel].append((indices_cropped, data_cropped, label))
        print(f"[LOADED] Baseline for {channel} from {filename}")
    except Exception as e:
        print(f"[ERROR] Could not load baseline {file_path}: {e}")


# === PEAK EXTRACTION FROM FOLDER NAME ===
def extract_peaks(folder_name):
    match = re.search(r"peak(\d+)_and(\d+)", folder_name)
    return (match.group(1), match.group(2)) if match else (None, None)


# === LOAD COINCIDENCE DATA ===
for subfolder in sorted(coic_data_dir.iterdir()):
    if not subfolder.is_dir():
        continue

    peak1, peak2 = extract_peaks(subfolder.name)
    if not peak1 or peak1 in exclude_peak_numbers or peak2 in exclude_peak_numbers:
        continue

    name_lower = subfolder.name.lower()

    # Determine filter state
    if "raw" in name_lower and not plot_raw:
        print(f"[SKIPPED] {subfolder.name} (raw data skipped)")
        continue
    elif "unfiltered" in name_lower:
        base_filter_state = "Unfiltered"
    elif "filtered" in name_lower:
        base_filter_state = "Filtered"
    else:
        print(f"[SKIPPED] {subfolder.name} (missing filter status)")
        continue

    print(f"[PROCESSING] {subfolder.name} — Peaks {peak1} & {peak2} — {base_filter_state}")

    for file_path in sorted(subfolder.glob("*.txt")):
        fname = file_path.name
        if fname.startswith("Data"):
            continue

        try:
            data = np.loadtxt(file_path)
            indices = np.arange(len(data))[crop_start_amount:-crop_end_amount]
            data_cropped = data[crop_start_amount:-crop_end_amount]

            ch = "CH0" if "CH0@" in fname else "CH1"
            filter_state = "AB Filtered" if fname.startswith("0@AddBack") else base_filter_state
            print(f"[DEBUG] File: {fname}, Channel: {ch}, Filter: {filter_state}")

            plot_label = f"Peak {peak1} & {peak2}"
            legend_key = (filter_state, ch, plot_label)
            label_counts[legend_key] = label_counts.get(legend_key, 0) + 1

            if label_counts[legend_key] > 1:
                plot_label += f" ({label_counts[legend_key]})"

            data_store[filter_state][ch].append((indices, data_cropped, plot_label))

        except Exception as e:
            print(f"[ERROR] Could not load {file_path}: {e}")


# === SCALE BASELINE TO MATCH SIGNAL ===
def get_scaling_factor(baseline, curves):
    if not curves:
        return 1  # fallback if empty
    max_baseline = np.max(baseline)
    max_signal = max(np.max(y) for _, y, _ in curves)
    return min((max_signal / max_baseline) if max_baseline else 1, baseline_multiplier_cap)


# === PLOTTING FUNCTION ===
def plot_grouped(data_list, title_prefix, ch):
    global global_plot_index

    if not data_list:
        print(f"[WARNING] Skipping plot for {title_prefix} — no data found.")
        return

    global_plot_index += 1
    title = title_prefix

    print(f"\n[INFO] === Plot #{global_plot_index} ({ch}) ===")
    print(f"[INFO] Plot title: {title}")
    print(f"[INFO] Number of curves: {len(data_list)}")

    plt.figure(figsize=(12, 7))

    # Sort curves by second peak number (extracted from label)
    def get_second_peak(label):
        match = re.search(r'Peak \d+ & (\d+)', label)
        return int(match.group(1)) if match else float('inf')

    # Sort before plotting
    for x, y, label in sorted(data_list, key=lambda item: get_second_peak(item[2])):
        plt.plot(x, y, lw=3, label=label)

    for bx, by, blabel in baseline_store[ch]:
        scale = get_scaling_factor(by, data_list)
        print(f"[INFO]   Baseline: {blabel} scaled ×{scale:.2f}")
        plt.plot(bx, by * scale, color="orange", lw=2, label=f"{blabel} ×{scale:.1f}")

    plt.xlabel("Index", fontsize=font_size)
    plt.ylabel("Counts", fontsize=font_size)
    plt.title(title, fontsize=font_size)
    plt.grid(True, linestyle='-', linewidth=0.75, alpha=0.7)
    plt.gca().xaxis.set_major_formatter(ticker.FormatStrFormatter('%.0f'))
    plt.tick_params(axis='x', labelsize=font_size)
    plt.tick_params(axis='y', labelsize=font_size)
    plt.legend(fontsize=font_size - 7)
    plt.tight_layout()
    plt.show()


# === EXECUTE PLOTS ===
plot_grouped(data_store['Filtered']['CH0'], "CH0 Curves (Filtered)", "CH0")
plot_grouped(data_store['Filtered']['CH1'], "CH1 Curves (Filtered)", "CH1")
plot_grouped(data_store['AB Filtered']['CH0'], "CH0 Curves (AB Filtered)", "CH0")
plot_grouped(data_store['AB Filtered']['CH1'], "CH1 Curves (AB Filtered)", "CH1")



# import matplotlib
#
# matplotlib.use('TkAgg')  # Use TkAgg backend for interactivity in PyCharm
#
# import numpy as np
# import matplotlib.pyplot as plt
# from pathlib import Path
# import re
# import matplotlib.ticker as ticker
#
# # === CONFIGURATION ===
# exclude_peak_numbers = ["5", "7", "9"]  # Peaks to exclude
# crop_start_amount = 100  # How much to crop from start of signal
# crop_end_amount = 3000  # How much to crop from end of signal
# font_size = 20  # Font size for plots
# baseline_multiplier_cap = 10  # Max allowed scaling of baseline overlay
#
# # Paths to data directories
# repo_root = Path(__file__).resolve().parents[2]
# coic_data_dir = repo_root / "data-photon-counts-SiPM" / "20250507_more_peaks_compare_coicdence"
# baseline_data_dir = repo_root / "data-photon-counts-SiPM" / "20250507_baseline_data_for_coic_comparison" / "65_7_gain_1_6_pulse_60s"
#
# # Flags to enable/disable plotting of data types
# plot_unfiltered = False
# plot_raw = False
#
# # === DATA STORAGE ===
# data_store = {'Filtered': {'CH0': [], 'CH1': []}, 'Unfiltered': {'CH0': [], 'CH1': []}, 'Raw': {'CH0': [], 'CH1': []}}
# baseline_store = {'CH0': [], 'CH1': []}
# label_counts = {}  # Track duplicates
# global_plot_index = 0
#
# # === DEBUG PRINT ===
# print(f"[DEBUG] Baseline directory path: {baseline_data_dir}")
# print(f"[DEBUG] Coincidence directory path: {coic_data_dir}")
#
# # === LOAD BASELINE FILES ===
# for file_path in baseline_data_dir.glob("*.txt"):
#     filename = file_path.name
#     if not filename.startswith("CH0@") and not filename.startswith("CH1@"):
#         continue
#     try:
#         data = np.loadtxt(file_path)
#         indices_cropped = np.arange(len(data))[crop_start_amount:-crop_end_amount]
#         data_cropped = data[crop_start_amount:-crop_end_amount]
#         channel = "CH0" if "CH0@" in filename else "CH1"
#         label = f"Baseline ({channel})"
#         baseline_store[channel].append((indices_cropped, data_cropped, label))
#         print(f"[LOADED] Baseline for {channel} from {filename}")
#     except Exception as e:
#         print(f"[ERROR] Could not load baseline {file_path}: {e}")
#
#
# # === PEAK EXTRACTION FROM FOLDER NAME ===
# def extract_peaks(folder_name):
#     match = re.search(r"peak(\d+)_and(\d+)", folder_name)
#     return (match.group(1), match.group(2)) if match else (None, None)
#
#
# # === LOAD COINCIDENCE DATA ===
# for subfolder in sorted(coic_data_dir.iterdir()):
#     if not subfolder.is_dir():
#         continue
#
#     peak1, peak2 = extract_peaks(subfolder.name)
#     if not peak1 or peak1 in exclude_peak_numbers or peak2 in exclude_peak_numbers:
#         continue
#
#     name_lower = subfolder.name.lower()
#
#     # Determine filter state
#     if "raw" in name_lower and not plot_raw:
#         print(f"[SKIPPED] {subfolder.name} (raw data skipped)")
#         continue
#     elif "unfiltered" in name_lower:
#         filter_state = "Unfiltered"
#     elif "filtered" in name_lower:
#         filter_state = "Filtered"
#     else:
#         print(f"[SKIPPED] {subfolder.name} (missing filter status)")
#         continue
#
#     print(f"[PROCESSING] {subfolder.name} — Peaks {peak1} & {peak2} — {filter_state}")
#
#     for file_path in sorted(subfolder.glob("*.txt")):
#         fname = file_path.name
#
#         # ✅ Override filter state if the file is from AddBack
#         if fname.startswith("0@AddBack"):
#             filter_state = "AB Filtered"
#
#         if fname.startswith("Data"):
#             continue
#
#         try:
#             data = np.loadtxt(file_path)
#             indices = np.arange(len(data))[crop_start_amount:-crop_end_amount]
#             data_cropped = data[crop_start_amount:-crop_end_amount]
#
#
#             ch = "CH0" if "CH0@" in fname else "CH1"
#             print(f"[DEBUG] File: {fname}, Channel: {ch}, Label: {label}, Filter: {filter_state}")
#
#             #label = f"{filter_state} — Peak {peak1} & {peak2}"
#             plot_label = f"Peak {peak1} & {peak2}"
#             legend_key = (filter_state, ch, plot_label)
#             label_counts[legend_key] = label_counts.get(legend_key, 0) + 1
#
#             # Append number if repeated
#             if label_counts[legend_key] > 1:
#                 plot_label += f" ({label_counts[legend_key]})"
#
#             # Store the data using label for the legend only
#             data_store[filter_state][ch].append((indices, data_cropped, plot_label))
#
#         except Exception as e:
#             print(f"[ERROR] Could not load {file_path}: {e}")
#
#
# # === SCALE BASELINE TO MATCH SIGNAL ===
# def get_scaling_factor(baseline, curves):
#     max_baseline = np.max(baseline)
#     max_signal = max(np.max(y) for _, y, _ in curves)
#     return min((max_signal / max_baseline) if max_baseline else 1, baseline_multiplier_cap)
#
#
# # === PLOTTING FUNCTION ===
#
# # === PLOTTING FUNCTION ===
# def plot_grouped(data_list, title_prefix, ch):
#     global global_plot_index
#
#     # Increment global counter for plot tracking
#     global_plot_index += 1
#     title = title_prefix
#
#     print(f"\n[INFO] === Plot #{global_plot_index} ({ch}) ===")
#     print(f"[INFO] Plot title: {title}")
#     print(f"[INFO] Number of curves: {len(data_list)}")
#
#     plt.figure(figsize=(12, 7))
#
#     for x, y, label in data_list:
#         plt.plot(x, y, lw=2, label=label)
#
#         # Extract file name from label
#         m = re.search(r'\| File: (.+)', label)
#         source_file = m.group(1) if m else "Unknown"
#
#         # Extract filter state from beginning
#         filter_state = label.split('—')[0].strip()
#         try:
#             peaks_info = label.split('—')[1].split('|')[0].strip()
#         except IndexError:
#             peaks_info = label  # fallback if label does not contain '—'
#
#         print(f"[INFO]   {filter_state} | {peaks_info} | File: {source_file}")
#
#     # Overlay baseline data
#     for bx, by, blabel in baseline_store[ch]:
#         scale = get_scaling_factor(by, data_list)
#         print(f"[INFO]   Baseline: {blabel} scaled ×{scale:.2f}")
#         plt.plot(bx, by * scale, color="orange", lw=2, linestyle="--", label=f"{blabel} ×{scale:.1f}")
#
#     plt.xlabel("Index", fontsize=font_size)
#     plt.ylabel("Counts", fontsize=font_size)
#     plt.title(title, fontsize=font_size)
#     plt.grid(True, linestyle='-', linewidth=0.75, alpha=0.7)
#     plt.gca().xaxis.set_major_formatter(ticker.FormatStrFormatter('%.0f'))
#     plt.tick_params(axis='x', labelsize=font_size)
#     plt.tick_params(axis='y', labelsize=font_size)
#     plt.legend(fontsize=font_size - 2)
#     plt.tight_layout()
#     plt.show()
#
# # def plot_grouped(data_list, title_prefix, ch):
# #     global global_plot_index
# #
# #     # Grouping disabled — plot all at once
# #     global_plot_index += 1
# #     title = title_prefix
# #
# #
# #     plt.figure(figsize=(12, 7))
# #     for x, y, label in data_list:
# #         plt.plot(x, y, lw=2, label=label)
# #
# #     # Overlay baseline data
# #     for bx, by, blabel in baseline_store[ch]:
#
#
# # === EXECUTE PLOTS ===
# plot_grouped(data_store['Filtered']['CH0'], "CH0 Curves (Filtered)", "CH0")
# plot_grouped(data_store['Filtered']['CH1'], "CH1 Curves (Filtered)", "CH1")
#
# # # Use interactive plotting backend for PyCharm
# # import matplotlib
# # matplotlib.use('TkAgg')
# #
# # import numpy as np
# # import matplotlib.pyplot as plt
# # from pathlib import Path
# # import re
# # import matplotlib.ticker as ticker
# #
# # # === CONFIGURATION ===
# # exclude_peak_numbers = ["5", "7", "9"]  # Peaks to skip entirely
# # crop_start_amount = 100  # Number of initial points to crop from each data file
# # crop_end_amount = 3000   # Number of final points to crop
# # font_size = 20
# # baseline_multiplier_cap = 10  # Limit on how much we can scale the baseline
# #
# # # File locations — navigate 2 folders up from this file
# # repo_root = Path(__file__).resolve().parents[2]
# # coic_data_dir = repo_root / "data-photon-counts-SiPM" / "20250507_more_peaks_compare_coicdence"
# # baseline_data_dir = repo_root / "data-photon-counts-SiPM" / "20250507_baseline_data_for_coic_comparison" / "65_7_gain_1_6_pulse_60s"
# #
# # # Toggles
# # plot_unfiltered = False
# # plot_raw = False
# #
# # # === Data Storage ===
# # data_store = {
# #     'Filtered': {'CH0': [], 'CH1': []},
# #     'Unfiltered': {'CH0': [], 'CH1': []},
# #     'Raw': {'CH0': [], 'CH1': []}
# # }
# # baseline_store = {'CH0': [], 'CH1': []}
# # label_counts = {}  # Used to append (1), (2), etc. if label repeats
# # global_plot_index = 0
# #
# # print(f"[DEBUG] Baseline directory path: {baseline_data_dir}")
# # print(f"[DEBUG] Coincidence directory path: {coic_data_dir}")
# #
# # # === Load Baseline Files ===
# # for file_path in baseline_data_dir.glob("*.txt"):
# #     filename = file_path.name
# #     print(f"[DEBUG] Checking file: {filename}")
# #
# #     if not filename.startswith("CH0@") and not filename.startswith("CH1@"):
# #         print(f"[SKIPPED] {filename} — does not start with CH0@ or CH1@")
# #         continue
# #
# #     try:
# #         data = np.loadtxt(file_path)
# #         indices_cropped = np.arange(len(data))[crop_start_amount:-crop_end_amount]
# #         data_cropped = data[crop_start_amount:-crop_end_amount]
# #     except Exception as e:
# #         print(f"[ERROR] Could not load baseline {file_path}: {e}")
# #         continue
# #
# #     channel = "CH0" if "CH0@" in filename else "CH1"
# #     label = f"Baseline ({channel})"
# #     baseline_store[channel].append((indices_cropped, data_cropped, label))
# #     print(f"[LOADED] Baseline for {channel} from {filename}")
# #
# # # Summary after loading all baseline files
# # print("[SUMMARY] Loaded baseline curves:")
# # for ch in baseline_store:
# #     print(f"  {ch}: {len(baseline_store[ch])} curves")
# #
# # # === Extract Peak Numbers from folder names ===
# # def extract_peaks(folder):
# #     m = re.search(r"peak(\d+)_and(\d+)", folder)
# #     return (m.group(1), m.group(2)) if m else (None, None)
# #
# # # === Load Coincidence Data Files ===
# # for subfolder in sorted(coic_data_dir.iterdir()):
# #     if not subfolder.is_dir():
# #         continue
# #
# #     peak1, peak2 = extract_peaks(subfolder.name)
# #     if not peak1 or peak1 in exclude_peak_numbers or peak2 in exclude_peak_numbers:
# #         print(f"[SKIPPED] {subfolder.name}")
# #         continue
# #
# #     name_lower = subfolder.name.lower()
# #
# #     # Identify if folder is raw/unfiltered/filtered
# #     if "raw" in name_lower and not plot_raw:
# #         print(f"[SKIPPED] {subfolder.name} (raw data skipped)")
# #         continue
# #     elif "unfiltered" in name_lower:
# #         filter_state = "Unfiltered"
# #     elif "filtered" in name_lower:
# #         filter_state = "Filtered"
# #     else:
# #         print(f"[SKIPPED] {subfolder.name} (missing filter status)")
# #         continue
# #
# #     print(f"[PROCESSING] {subfolder.name} — Peaks {peak1} & {peak2} — {filter_state}")
# #
# #     for file_path in sorted(subfolder.glob("*.txt")):
# #         fname = file_path.name
# #         if fname.startswith("Data"):
# #             continue
# #
# #         try:
# #             data = np.loadtxt(file_path)
# #             indices = np.arange(len(data))[crop_start_amount:-crop_end_amount]  # keep real indices
# #             data_cropped = data[crop_start_amount:-crop_end_amount]
# #             label = f"Peak {peak1} & {peak2})"
# #             print(f"label: {label}")
# #             ch = "CH0" if "CH0@" in fname else "CH1"
# #             key = (filter_state, ch, label)
# #             label_counts[key] = label_counts.get(key, 0) + 1
# #             # Add instance number (1), (2), ... if repeated
# #             if label_counts[key] > 1:
# #                 label += f" ({label_counts[key]})"
# #             data_store[filter_state][ch].append((indices, data_cropped, label))
# #         except Exception as e:
# #             print(f"[ERROR] Could not load {file_path}: {e}")
# #
# # # === Compute scale to match baseline to signal ===
# # def get_scaling_factor(baseline, curves):
# #     max_baseline = np.max(baseline)
# #     max_signal = max(np.max(y) for _, y, _ in curves)
# #     return min((max_signal / max_baseline) if max_baseline else 1, baseline_multiplier_cap)
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# # # === Plotting function ===
# # def plot_grouped(data_list, title_prefix, ch):
# #     global global_plot_index
# #     grouped = {}
# #
# #     # Group by instance number (used to split repeated curves for same label)
# #     for x, y, label in data_list:
# #         instance = re.search(r"\((\d+)\)$", label)  # finds numbers like (2) at the end of label
# #         print(f"instance: {instance}")
# #         key = instance.group(1) if instance else "1"  # default to "1" if no match
# #         grouped.setdefault(key, []).append((x, y, label))
# #
# #     # Plot each instance group separately
# #     for instance, curves in grouped.items():
# #         global_plot_index += 1
# #         title = f"{title_prefix} — Instance {instance}"  # shown in plot title
# #         print(f"instance: {instance}")
# #         plt.figure(figsize=(12, 7))
# #
# #         for x, y, label in curves:
# #             plt.plot(x, y, lw=2, label=label)
# #             print(f"label: {label}")
# #
# #         # Overlay baseline
# #         print(f"[INFO] Plot #{global_plot_index}: Overlaying {len(baseline_store[ch])} baselines for {ch}")
# #         for bx, by, blabel in baseline_store[ch]:
# #             scale = get_scaling_factor(by, curves)
# #             print(f"[INFO]   {blabel} scaled ×{scale:.2f}")
# #             plt.plot(bx, by * scale, color="orange", lw=2, label=f"{blabel} ×{scale:.1f}")
# #
# #         # Axis and visual formatting
# #         plt.xlabel("Index", fontsize=font_size)
# #         plt.ylabel("Counts", fontsize=font_size)
# #         plt.title(title, fontsize=font_size)
# #         plt.grid(True, linestyle='-', linewidth=0.75, alpha=0.7)
# #         plt.gca().xaxis.set_major_formatter(ticker.FormatStrFormatter('%.0f'))
# #         plt.tick_params(axis='x', labelsize=font_size)
# #         plt.tick_params(axis='y', labelsize=font_size)
# #         plt.legend(fontsize=font_size-2)
# #         plt.tight_layout()
# #         plt.show()
# #
# # # === MAIN EXECUTION ===
# # plot_grouped(data_store['Filtered']['CH0'], "CH0 Curves (Filtered)", "CH0")
# # plot_grouped(data_store['Filtered']['CH1'], "CH1 Curves (Filtered)", "CH1")
# #
# #
# # # import matplotlib
# # # matplotlib.use('TkAgg')  # For PyCharm interactivity
# # #
# # # import numpy as np
# # # import matplotlib.pyplot as plt
# # # from pathlib import Path
# # # import re
# # # import matplotlib.ticker as ticker
# # #
# # # # === CONFIGURATION ===
# # # exclude_peak_numbers = ["5", "7", "9"]
# # # crop_start_amount = 100
# # # crop_end_amount = 3000
# # # font_size = 20
# # # baseline_multiplier_cap = 10
# # #
# # # repo_root = Path(__file__).resolve().parents[2]
# # # coic_data_dir = repo_root / "data-photon-counts-SiPM" / "20250507_more_peaks_compare_coicdence"
# # # baseline_data_dir = repo_root / "data-photon-counts-SiPM" / "20250507_baseline_data_for_coic_comparison" / "65_7_gain_1_6_pulse_60s"
# # #
# # # plot_unfiltered = False
# # # plot_raw = False
# # #
# # # #========================================================================
# # # #========================================================================
# # #
# # #
# # #
# # # # === Storage ===
# # # data_store = {'Filtered': {'CH0': [], 'CH1': []}, 'Unfiltered': {'CH0': [], 'CH1': []}, 'Raw': {'CH0': [], 'CH1': []}}
# # # baseline_store = {'CH0': [], 'CH1': []}
# # # label_counts = {}
# # # global_plot_index = 0
# # #
# # # # === DEBUG ===
# # # print(f"[DEBUG] Baseline directory path: {baseline_data_dir}")
# # # print(f"[DEBUG] Coincidence directory path: {coic_data_dir}")
# # #
# # # # === Load Baseline Files ===
# # # for file_path in baseline_data_dir.glob("*.txt"):
# # #     filename = file_path.name
# # #     print(f"[DEBUG] Checking file: {filename}")
# # #
# # #     if not filename.startswith("CH0@") and not filename.startswith("CH1@"):
# # #         print(f"[SKIPPED] {filename} — does not start with CH0@ or CH1@")
# # #         continue
# # #
# # #     try:
# # #         data = np.loadtxt(file_path)
# # #         indices_cropped = np.arange(len(data))[crop_start_amount:-crop_end_amount]
# # #         data_cropped = data[crop_start_amount:-crop_end_amount]
# # #     except Exception as e:
# # #         print(f"[ERROR] Could not load baseline {file_path}: {e}")
# # #         continue
# # #
# # #     channel = "CH0" if "CH0@" in filename else "CH1"
# # #     label = f"Baseline ({channel})"
# # #     baseline_store[channel].append((indices_cropped, data_cropped, label))
# # #     print(f"[LOADED] Baseline for {channel} from {filename}")
# # #
# # # # === Post-loading summary ===
# # # print(f"[SUMMARY] Loaded baseline curves:")
# # # for ch in baseline_store:
# # #     print(f"  {ch}: {len(baseline_store[ch])} curves")
# # #
# # # # === Extract peak numbers ===
# # # def extract_peaks(folder):
# # #     m = re.search(r"peak(\d+)_and(\d+)", folder)
# # #     return (m.group(1), m.group(2)) if m else (None, None)
# # #
# # # # === Load Coincidence Data ===
# # # for subfolder in sorted(coic_data_dir.iterdir()):
# # #     if not subfolder.is_dir():
# # #         continue
# # #
# # #     peak1, peak2 = extract_peaks(subfolder.name)
# # #     if not peak1 or peak1 in exclude_peak_numbers or peak2 in exclude_peak_numbers:
# # #         print(f"[SKIPPED] {subfolder.name}")
# # #         continue
# # #
# # #     name_lower = subfolder.name.lower()
# # #
# # #     if "raw" in name_lower and not plot_raw:
# # #         print(f"[SKIPPED] {subfolder.name} (raw data skipped)")
# # #         continue
# # #     elif "unfiltered" in name_lower:
# # #         filter_state = "Unfiltered"
# # #     elif "filtered" in name_lower:
# # #         filter_state = "Filtered"
# # #     else:
# # #         print(f"[SKIPPED] {subfolder.name} (missing filter status)")
# # #         continue
# # #
# # #     print(f"[PROCESSING] {subfolder.name} — Peaks {peak1} & {peak2} — {filter_state}")
# # #     for file_path in sorted(subfolder.glob("*.txt")):
# # #         fname = file_path.name
# # #         if fname.startswith("Data"):
# # #             continue
# # #         try:
# # #             data = np.loadtxt(file_path)
# # #             indices = np.arange(len(data))[crop_start_amount:-crop_end_amount]  # retain original index range
# # #             data_cropped = data[crop_start_amount:-crop_end_amount]
# # #             label = f"Peak {peak1} & {peak2}"
# # #             ch = "CH0" if "CH0@" in fname else "CH1"
# # #             key = (filter_state, ch, label)
# # #             label_counts[key] = label_counts.get(key, 0) + 1
# # #             if label_counts[key] > 1:
# # #                 label += f" ({label_counts[key]})"
# # #             data_store[filter_state][ch].append((indices, data_cropped, label))
# # #         except Exception as e:
# # #             print(f"[ERROR] Could not load {file_path}: {e}")
# # #
# # #
# # # # === Compute Scaling Factor ===
# # # def get_scaling_factor(baseline, curves):
# # #     max_baseline = np.max(baseline)
# # #     max_signal = max(np.max(y) for _, y, _ in curves)
# # #     return min((max_signal / max_baseline) if max_baseline else 1, baseline_multiplier_cap)
# # #
# # # # === Group & Plot ===
# # # def plot_grouped(data_list, title_prefix, ch):
# # #     global global_plot_index
# # #     grouped = {}
# # #
# # #     for x, y, label in data_list:
# # #         instance = re.search(r"\((\d+)\)$", label)
# # #         key = instance.group(1) if instance else "1"
# # #         grouped.setdefault(key, []).append((x, y, label))
# # #
# # #     for instance, curves in grouped.items():
# # #         global_plot_index += 1
# # #         title = f"{title_prefix} — Instance {instance}"
# # #         plt.figure(figsize=(12, 7))
# # #         for x, y, label in curves:
# # #             plt.plot(x, y, lw=2, label=label)
# # #
# # #         # Always overlay baseline if available
# # #         print(f"[INFO] Plot #{global_plot_index}: Overlaying {len(baseline_store[ch])} baselines for {ch}")
# # #         for bx, by, blabel in baseline_store[ch]:
# # #             scale = get_scaling_factor(by, curves)
# # #             print(f"[INFO]   {blabel} scaled ×{scale:.2f}")
# # #             plt.plot(bx, by * scale, color="orange", lw=2, label=f"{blabel} ×{scale:.1f}")
# # #
# # #         plt.xlabel("Index", fontsize=font_size)
# # #         plt.ylabel("Counts", fontsize=font_size)
# # #         plt.title(title, fontsize=font_size)
# # #         plt.grid(True, linestyle='-', linewidth=0.75, alpha=0.7)
# # #         plt.gca().xaxis.set_major_formatter(ticker.FormatStrFormatter('%.0f'))
# # #         plt.tick_params(axis='x', labelsize=font_size)
# # #         plt.tick_params(axis='y', labelsize=font_size)
# # #         plt.legend(fontsize=font_size-2)
# # #         plt.tight_layout()
# # #         plt.show()
# # #
# # # # === EXECUTE PLOTS ===
# # # plot_grouped(data_store['Filtered']['CH0'], "CH0 Curves (Filtered)", "CH0")
# # # plot_grouped(data_store['Filtered']['CH1'], "CH1 Curves (Filtered)", "CH1")
