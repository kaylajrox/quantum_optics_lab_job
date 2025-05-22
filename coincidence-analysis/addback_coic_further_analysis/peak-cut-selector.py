import matplotlib
matplotlib.use('TkAgg')  # For PyCharm interactivity

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import re
import matplotlib.ticker as ticker

# === CONFIGURATION ===
exclude_peak_numbers = ["5", "7", "9"]
crop_start_amount = 100
crop_end_amount = 3000
font_size = 20
baseline_multiplier_cap = 10

repo_root = Path(__file__).resolve().parents[2]
coic_data_dir = repo_root / "data-photon-counts-SiPM" / "20250507_more_peaks_compare_coicdence"
baseline_data_dir = repo_root / "data-photon-counts-SiPM" / "20250507_baseline_data_for_coic_comparison" / "65_7_gain_1_6_pulse_60s"

plot_unfiltered = False
plot_raw = False

# === Storage ===
data_store = {'Filtered': {'CH0': [], 'CH1': []}, 'Unfiltered': {'CH0': [], 'CH1': []}, 'Raw': {'CH0': [], 'CH1': []}}
baseline_store = {'CH0': [], 'CH1': []}
label_counts = {}
global_plot_index = 0

# === DEBUG ===
print(f"[DEBUG] Baseline directory path: {baseline_data_dir}")

# === Load Baseline Files ===
for file_path in baseline_data_dir.glob("*.txt"):
    filename = file_path.name
    print(f"[DEBUG] Checking file: {filename}")

    if not filename.startswith("CH0@") and not filename.startswith("CH1@"):
        print(f"[SKIPPED] {filename} — does not start with CH0@ or CH1@")
        continue

    try:
        data = np.loadtxt(file_path)
        indices_cropped = np.arange(len(data))[crop_start_amount:-crop_end_amount]
        data_cropped = data[crop_start_amount:-crop_end_amount]
    except Exception as e:
        print(f"[ERROR] Could not load baseline {file_path}: {e}")
        continue

    channel = "CH0" if "CH0@" in filename else "CH1"
    label = f"Baseline ({channel})"
    baseline_store[channel].append((indices_cropped, data_cropped, label))
    print(f"[LOADED] Baseline for {channel} from {filename}")

# === Post-loading summary ===
print(f"[SUMMARY] Loaded baseline curves:")
for ch in baseline_store:
    print(f"  {ch}: {len(baseline_store[ch])} curves")

# === Extract peak numbers ===
def extract_peaks(folder):
    m = re.search(r"peak(\d+)_and(\d+)", folder)
    return (m.group(1), m.group(2)) if m else (None, None)

# === Load Coincidence Data ===
for subfolder in sorted(coic_data_dir.iterdir()):
    if not subfolder.is_dir():
        continue

    peak1, peak2 = extract_peaks(subfolder.name)
    if not peak1 or peak1 in exclude_peak_numbers or peak2 in exclude_peak_numbers:
        print(f"[SKIPPED] {subfolder.name}")
        continue

    name_lower = subfolder.name.lower()
    if "filtered" in name_lower:
        filter_state = "Filtered"
    elif "unfiltered" in name_lower:
        filter_state = "Unfiltered"
    else:
        print(f"[SKIPPED] {subfolder.name} (missing filter status)")
        continue

    print(f"[PROCESSING] {subfolder.name} — Peaks {peak1} & {peak2} — {filter_state}")
    for file_path in sorted(subfolder.glob("*.txt")):
        fname = file_path.name
        if fname.startswith("Data"):
            continue
        try:
            data = np.loadtxt(file_path)
            data_cropped = data[crop_start_amount:-crop_end_amount]
            indices = np.arange(len(data_cropped))
            label = f"Peak {peak1} & {peak2}"
            ch = "CH0" if "CH0@" in fname else "CH1"
            key = (filter_state, ch, label)
            label_counts[key] = label_counts.get(key, 0) + 1
            if label_counts[key] > 1:
                label += f" ({label_counts[key]})"
            data_store[filter_state][ch].append((indices, data_cropped, label))
        except Exception as e:
            print(f"[ERROR] Could not load {file_path}: {e}")

# === Compute Scaling Factor ===
def get_scaling_factor(baseline, curves):
    max_baseline = np.max(baseline)
    max_signal = max(np.max(y) for _, y, _ in curves)
    return min((max_signal / max_baseline) if max_baseline else 1, baseline_multiplier_cap)

# === Group & Plot ===
def plot_grouped(data_list, title_prefix, ch):
    global global_plot_index
    grouped = {}

    for x, y, label in data_list:
        instance = re.search(r"\((\d+)\)$", label)
        key = instance.group(1) if instance else "1"
        grouped.setdefault(key, []).append((x, y, label))

    for instance, curves in grouped.items():
        global_plot_index += 1
        title = f"{title_prefix} — Instance {instance}"
        plt.figure(figsize=(12, 7))
        for x, y, label in curves:
            plt.plot(x, y, lw=2, label=label)

        # Always overlay baseline if available
        print(f"[INFO] Plot #{global_plot_index}: Overlaying {len(baseline_store[ch])} baselines for {ch}")
        for bx, by, blabel in baseline_store[ch]:
            scale = get_scaling_factor(by, curves)
            print(f"[INFO]   {blabel} scaled ×{scale:.2f}")
            plt.plot(bx, by * scale, linestyle="--", color="orange", lw=2, label=f"{blabel} ×{scale:.1f}")

        plt.xlabel("Index", fontsize=font_size)
        plt.ylabel("Counts", fontsize=font_size)
        plt.title(title, fontsize=font_size)
        plt.grid(True, linestyle='-', linewidth=0.75, alpha=0.7)
        plt.gca().xaxis.set_major_formatter(ticker.FormatStrFormatter('%.0f'))
        plt.tick_params(axis='x', labelsize=font_size)
        plt.tick_params(axis='y', labelsize=font_size)
        plt.legend(fontsize=font_size-2)
        plt.tight_layout()
        plt.show()

# === EXECUTE PLOTS ===
plot_grouped(data_store['Filtered']['CH0'], "CH0 Curves (Filtered)", "CH0")
plot_grouped(data_store['Filtered']['CH1'], "CH1 Curves (Filtered)", "CH1")

if plot_unfiltered:
    plot_grouped(data_store['Unfiltered']['CH0'], "CH0 Curves (Unfiltered)", "CH0")
    plot_grouped(data_store['Unfiltered']['CH1'], "CH1 Curves (Unfiltered)", "CH1")

if plot_raw:
    plot_grouped(data_store['Raw']['CH0'], "CH0 Curves (Raw)", "CH0")
    plot_grouped(data_store['Raw']['CH1'], "CH1 Curves (Raw)", "CH1")




# import matplotlib
# matplotlib.use('TkAgg')  # For PyCharm interactivity
#
# import numpy as np
# import matplotlib.pyplot as plt
# from pathlib import Path
# import re
# import matplotlib.ticker as ticker
#
# # === CONFIGURATION ===
# exclude_peak_numbers = ["5", "7", "9"]
# crop_start_amount = 100
# crop_end_amount = 3000
# font_size = 20
# baseline_multiplier_cap = 10
#
# repo_root = Path(__file__).resolve().parents[1]
# coic_data_dir = repo_root / "data-photon-counts-SiPM" / "20250507_more_peaks_compare_coicdence"
# baseline_data_dir = repo_root / "data-photon-counts-SiPM" / "20250507_baseline_data_for_coic_comparison"
#
# plot_unfiltered = False
# plot_raw = False
#
# # === Storage ===
# data_store = {'Filtered': {'CH0': [], 'CH1': []}, 'Unfiltered': {'CH0': [], 'CH1': []}, 'Raw': {'CH0': [], 'CH1': []}}
# baseline_store = {'CH0': [], 'CH1': []}
# label_counts = {}
# global_plot_index = 0
#
# # === Load Baseline Files ===
# for file_path in baseline_data_dir.glob("*.txt"):
#     fname = file_path.name
#     if not fname.startswith("CH0@") and not fname.startswith("CH1@"):
#         continue
#     try:
#         data = np.loadtxt(file_path)
#         data_cropped = data[crop_start_amount:-crop_end_amount]
#         indices = np.arange(len(data_cropped))
#         ch = "CH0" if "CH0@" in fname else "CH1"
#         baseline_store[ch].append((indices, data_cropped, f"Baseline ({ch})"))
#     except Exception as e:
#         print(f"[ERROR] Could not load baseline {file_path}: {e}")
#
# print("Loaded baseline files:")
# for ch in baseline_store:
#     print(f"{ch}: {len(baseline_store[ch])} curves")
#
#
# # === Extract peak numbers ===
# def extract_peaks(folder):
#     m = re.search(r"peak(\d+)_and(\d+)", folder)
#     return (m.group(1), m.group(2)) if m else (None, None)
#
# # === Load Coincidence Data ===
# for subfolder in sorted(coic_data_dir.iterdir()):
#     if not subfolder.is_dir():
#         continue
#
#     peak1, peak2 = extract_peaks(subfolder.name)
#     if not peak1 or peak1 in exclude_peak_numbers or peak2 in exclude_peak_numbers:
#         print(f"[SKIPPED] {subfolder.name}")
#         continue
#
#     name_lower = subfolder.name.lower()
#     if "filtered" in name_lower:
#         filter_state = "Filtered"
#     elif "unfiltered" in name_lower:
#         filter_state = "Unfiltered"
#     else:
#         print(f"[SKIPPED] {subfolder.name} (missing filter status)")
#         continue
#
#     print(f"[PROCESSING] {subfolder.name} — Peaks {peak1} & {peak2} — {filter_state}")
#     for file_path in sorted(subfolder.glob("*.txt")):
#         fname = file_path.name
#         if fname.startswith("Data"):
#             continue
#         try:
#             data = np.loadtxt(file_path)
#             data_cropped = data[crop_start_amount:-crop_end_amount]
#             indices = np.arange(len(data_cropped))
#             label = f"Peak {peak1} & {peak2}"
#             ch = "CH0" if "CH0@" in fname else "CH1"
#             key = (filter_state, ch, label)
#             label_counts[key] = label_counts.get(key, 0) + 1
#             if label_counts[key] > 1:
#                 label += f" ({label_counts[key]})"
#             data_store[filter_state][ch].append((indices, data_cropped, label))
#         except Exception as e:
#             print(f"[ERROR] Could not load {file_path}: {e}")
#
# # === Compute Scaling Factor ===
# def get_scaling_factor(baseline, curves):
#     max_baseline = np.max(baseline)
#     max_signal = max(np.max(y) for _, y, _ in curves)
#     return min((max_signal / max_baseline) if max_baseline else 1, baseline_multiplier_cap)
#
# # === Group & Plot ===
# def plot_grouped(data_list, title_prefix, ch):
#     global global_plot_index
#     grouped = {}
#
#     for x, y, label in data_list:
#         instance = re.search(r"\((\d+)\)$", label)
#         key = instance.group(1) if instance else "1"
#         grouped.setdefault(key, []).append((x, y, label))
#
#     for instance, curves in grouped.items():
#         global_plot_index += 1
#         title = f"{title_prefix} — Instance {instance}"
#         plt.figure(figsize=(12, 7))
#         for x, y, label in curves:
#             plt.plot(x, y, lw=2, label=label)
#
#         # Always overlay baseline
#         for bx, by, blabel in baseline_store[ch]:
#             scale = get_scaling_factor(by, curves)
#             print(f"[INFO] Overlaying baseline on plot #{global_plot_index} with scale ×{scale:.2f}")
#             plt.plot(
#                 bx,
#                 by * scale,
#                 lw=2,
#                 linestyle='--',
#                 color='orange',
#                 label=f"{blabel} ×{scale:.1f}"
#             )
#
#         plt.xlabel("Index", fontsize=font_size)
#         plt.ylabel("Counts", fontsize=font_size)
#         plt.title(title, fontsize=font_size)
#         plt.grid(True, linestyle='-', linewidth=0.75, alpha=0.7)
#         plt.gca().xaxis.set_major_formatter(ticker.FormatStrFormatter('%.0f'))
#         plt.tick_params(axis='x', labelsize=font_size)
#         plt.tick_params(axis='y', labelsize=font_size)
#         plt.legend(fontsize=font_size-2)
#         plt.tight_layout()
#         plt.show()
#
# # === EXECUTE PLOTS ===
# plot_grouped(data_store['Filtered']['CH0'], "CH0 Curves (Filtered)", "CH0")
# plot_grouped(data_store['Filtered']['CH1'], "CH1 Curves (Filtered)", "CH1")
#
# if plot_unfiltered:
#     plot_grouped(data_store['Unfiltered']['CH0'], "CH0 Curves (Unfiltered)", "CH0")
#     plot_grouped(data_store['Unfiltered']['CH1'], "CH1 Curves (Unfiltered)", "CH1")
#
# if plot_raw:
#     plot_grouped(data_store['Raw']['CH0'], "CH0 Curves (Raw)", "CH0")
#     plot_grouped(data_store['Raw']['CH1'], "CH1 Curves (Raw)", "CH1")
#
#
#
# # import matplotlib
# # matplotlib.use('TkAgg')
# #
# # import numpy as np
# # import matplotlib.pyplot as plt
# # from pathlib import Path
# # import re
# # import matplotlib.ticker as ticker
# #
# # # === Peaks to EXCLUDE ===
# # exclude_peak_numbers = ["5", "7", "9"]
# #
# # # === CONFIG ===
# # repo_root = Path(__file__).resolve().parents[1]
# # coic_data_dir = repo_root / "data-photon-counts-SiPM" / "20250507_more_peaks_compare_coicdence"
# # baseline_data_dir = repo_root / "data-photon-counts-SiPM" / "20250507_baseline_data_for_coic_comparison"
# # crop_start_amount = 100
# # crop_end_amount = 3000
# # font_size = 20
# #
# # # === Baseline scaling config ===
# # baseline_multiplier = 5
# #
# # # === Plot Toggles ===
# # plot_unfiltered = False
# # plot_raw = False
# #
# # # === Data storage ===
# # data_store = {
# #     'Filtered': {'CH0': [], 'CH1': []},
# #     'Unfiltered': {'CH0': [], 'CH1': []},
# #     'Raw': {'CH0': [], 'CH1': []},
# # }
# #
# # # === Load Baseline Data ===
# # baseline_store = {'CH0': [], 'CH1': []}
# #
# # for file_path in baseline_data_dir.glob("*.txt"):
# #     filename = file_path.name
# #     if not filename.startswith("CH0@") and not filename.startswith("CH1@"):
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
# #
# # # === Label counts ===
# # label_counts = {}
# #
# # # === Extract peak numbers ===
# # def extract_peak_numbers(folder_name):
# #     match = re.search(r"peak(\d+)_and(\d+)", folder_name)
# #     if match:
# #         return match.group(1), match.group(2)
# #     return None, None
# #
# # # === Iterate directories ===
# # for subfolder in sorted(coic_data_dir.iterdir()):
# #     if not subfolder.is_dir():
# #         continue
# #
# #     peak1, peak2 = extract_peak_numbers(subfolder.name)
# #     if not peak1:
# #         print(f"[SKIPPED] Could not parse peak numbers from {subfolder.name}")
# #         continue
# #
# #     if peak1 in exclude_peak_numbers or peak2 in exclude_peak_numbers:
# #         print(f"[SKIPPED] {subfolder.name} — peaks excluded: {exclude_peak_numbers}")
# #         continue
# #
# #     name_lower = subfolder.name.lower()
# #     if "filtered" in name_lower:
# #         filter_state = "Filtered"
# #     elif "unfiltered" in name_lower:
# #         filter_state = "Unfiltered"
# #     else:
# #         print(f"[SKIPPED] {subfolder.name} — no 'filtered'/'unfiltered' keyword found, skipping")
# #         continue
# #
# #     print(f"[PROCESSING] {subfolder.name} | Peak {peak1} & {peak2} | {filter_state}")
# #
# #     for file_path in sorted(subfolder.glob("*.txt")):
# #         filename = file_path.name
# #         if filename.startswith("Data"):
# #             continue
# #
# #         try:
# #             data = np.loadtxt(file_path)
# #             indices_cropped = np.arange(len(data))[crop_start_amount:-crop_end_amount]
# #             data_cropped = data[crop_start_amount:-crop_end_amount]
# #         except Exception as e:
# #             print(f"[ERROR] Could not load {file_path}: {e}")
# #             continue
# #
# #         label = f"Peak {peak1} & {peak2}"
# #         channel = "CH0" if "CH0@" in filename else "CH1"
# #         label_key = (filter_state, channel, label)
# #
# #         count = label_counts.get(label_key, 0) + 1
# #         label_counts[label_key] = count
# #
# #         if count > 1:
# #             label = f"{label} ({count})"
# #
# #         data_store[filter_state][channel].append((indices_cropped, data_cropped, label))
# #
# # # === Baseline scale estimation ===
# # def get_scaling_factor(baseline_values, coincidence_curves):
# #     max_baseline = np.max(baseline_values)
# #     max_signal = max(np.max(values) for _, values, _ in coincidence_curves)
# #     return max_signal / max_baseline if max_baseline != 0 else 1
# #
# # # === Global plot counter ===
# # global_plot_index = 0
# #
# # # === Grouped plotting with conditional baseline overlay ===
# # def plot_channel_grouped_by_instance(data_list, title_base, channel):
# #     global global_plot_index
# #     grouped = {}
# #
# #     for indices, values, label in data_list:
# #         match = re.search(r"\((\d+)\)$", label)
# #         instance = match.group(1) if match else "1"
# #         if instance not in grouped:
# #             grouped[instance] = []
# #         grouped[instance].append((indices, values, label))
# #
# #     for instance, curves in grouped.items():
# #         global_plot_index += 1
# #         title = f"{title_base} — Instance {instance}"
# #         plt.figure(figsize=(12, 7))
# #
# #         for indices, values, label in curves:
# #             plt.plot(indices, values, lw=2, label=label)
# #
# #         if global_plot_index == 4:
# #             for b_indices, b_values, b_label in baseline_store[channel]:
# #                 scaling_factor = get_scaling_factor(b_values, curves)
# #                 scaling_factor = min(scaling_factor, 10)
# #                 print(f"[INFO] Overlaying baseline on plot #{global_plot_index} with scale ×{scaling_factor:.2f}")
# #                 plt.plot(
# #                     b_indices,
# #                     b_values * scaling_factor,
# #                     lw=2,
# #                     linestyle='--',
# #                     color='orange',
# #                     label=f"{b_label} ×{scaling_factor:.1f}"
# #                 )
# #
# #         plt.xlabel("Index", fontsize=font_size)
# #         plt.ylabel("Counts", fontsize=font_size)
# #         plt.title(title, fontsize=font_size)
# #         plt.gca().xaxis.set_major_formatter(ticker.FormatStrFormatter('%.0f'))
# #         plt.tick_params(axis='x', labelsize=font_size)
# #         plt.tick_params(axis='y', labelsize=font_size)
# #         plt.grid(True, linestyle='-', linewidth=0.75, alpha=0.7)
# #         plt.legend(fontsize=font_size - 2, loc='best')
# #         plt.tight_layout()
# #         plt.show()
# #
# # # === Plot execution ===
# # plot_channel_grouped_by_instance(data_store['Filtered']['CH0'], "CH0 Curves (Filtered)", "CH0")
# # plot_channel_grouped_by_instance(data_store['Filtered']['CH1'], "CH1 Curves (Filtered)", "CH1")
# #
# # if plot_unfiltered:
# #     plot_channel_grouped_by_instance(data_store['Unfiltered']['CH0'], "CH0 Curves (Unfiltered)", "CH0")
# #     plot_channel_grouped_by_instance(data_store['Unfiltered']['CH1'], "CH1 Curves (Unfiltered)", "CH1")
# #
# # if plot_raw:
# #     plot_channel_grouped_by_instance(data_store['Raw']['CH0'], "CH0 Curves (Raw)", "CH0")
# #     plot_channel_grouped_by_instance(data_store['Raw']['CH1'], "CH1 Curves (Raw)", "CH1")
# #
# #
# #
# # # import matplotlib
# # # matplotlib.use('TkAgg')
# # #
# # # import numpy as np
# # # import matplotlib.pyplot as plt
# # # from pathlib import Path
# # # import re
# # # import matplotlib.ticker as ticker
# # #
# # # # === Peaks to EXCLUDE ===
# # # exclude_peak_numbers = ["5","7", "9"]
# # #
# # #
# # #
# # #
# # # # === CONFIG ===
# # # repo_root = Path(__file__).resolve().parents[1]
# # # coic_data_dir = repo_root / "data-photon-counts-SiPM" / "20250507_more_peaks_compare_coicdence"
# # # baseline_data_dir = repo_root / "data-photon-counts-SiPM" / "20250507_baseline_data_for_coic_comparison"
# # # crop_start_amount = 100
# # # crop_end_amount = 3150
# # # font_size = 20
# # # # === CONFIG ===
# # # baseline_multiplier = 5  # <-- Scale baseline to match coincidence profile shape
# # #
# # #
# # # # === Plot Toggles ===
# # # plot_unfiltered = False
# # # plot_raw = False
# # #
# # # # === Data storage ===
# # # data_store = {
# # #     'Filtered': {'CH0': [], 'CH1': []},
# # #     'Unfiltered': {'CH0': [], 'CH1': []},
# # #     'Raw': {'CH0': [], 'CH1': []},
# # # }
# # #
# # # # === Load Baseline Data ===
# # # baseline_store = {'CH0': [], 'CH1': []}
# # #
# # # for file_path in baseline_data_dir.glob("*.txt"):
# # #     filename = file_path.name
# # #     if not filename.startswith("CH0@") and not filename.startswith("CH1@"):
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
# # #
# # #
# # # # === Label counts ===
# # # label_counts = {}
# # #
# # # # === Extract peak numbers ===
# # # def extract_peak_numbers(folder_name):
# # #     match = re.search(r"peak(\d+)_and(\d+)", folder_name)
# # #     if match:
# # #         return match.group(1), match.group(2)
# # #     return None, None
# # #
# # # # === Iterate directories ===
# # # for subfolder in sorted(coic_data_dir.iterdir()):
# # #     if not subfolder.is_dir():
# # #         continue
# # #
# # #     peak1, peak2 = extract_peak_numbers(subfolder.name)
# # #     if not peak1:
# # #         print(f"[SKIPPED] Could not parse peak numbers from {subfolder.name}")
# # #         continue
# # #
# # #     # Exclude peaks logic
# # #     if peak1 in exclude_peak_numbers or peak2 in exclude_peak_numbers:
# # #         print(f"[SKIPPED] {subfolder.name} — peaks excluded: {exclude_peak_numbers}")
# # #         continue
# # #
# # #     # Filter state detection
# # #     name_lower = subfolder.name.lower()
# # #     if "filtered" in name_lower:
# # #         filter_state = "Filtered"
# # #     elif "unfiltered" in name_lower:
# # #         filter_state = "Unfiltered"
# # #     else:
# # #         print(f"[SKIPPED] {subfolder.name} — no 'filtered'/'unfiltered' keyword found, skipping")
# # #         continue
# # #
# # #     print(f"[PROCESSING] {subfolder.name} | Peak {peak1} & {peak2} | {filter_state}")
# # #
# # #     for file_path in sorted(subfolder.glob("*.txt")):
# # #         filename = file_path.name
# # #
# # #         if filename.startswith("Data"):
# # #             continue
# # #
# # #         try:
# # #             data = np.loadtxt(file_path)
# # #             indices_cropped = np.arange(len(data))[crop_start_amount:-crop_end_amount]
# # #             data_cropped = data[crop_start_amount:-crop_end_amount]
# # #         except Exception as e:
# # #             print(f"[ERROR] Could not load {file_path}: {e}")
# # #             continue
# # #
# # #         # Build and uniquify label
# # #         label = f"Peak {peak1} & {peak2}"
# # #         channel = "CH0" if "CH0@" in filename else "CH1"
# # #         label_key = (filter_state, channel, label)
# # #
# # #         count = label_counts.get(label_key, 0) + 1
# # #         label_counts[label_key] = count
# # #
# # #         if count > 1:
# # #             label = f"{label} ({count})"
# # #
# # #         data_store[filter_state][channel].append((indices_cropped, data_cropped, label))
# # # def get_scaling_factor(baseline_values, coincidence_curves):
# # #     """Estimate a scale to bring baseline closer to the range of coincidence curves."""
# # #     max_baseline = np.max(baseline_values)
# # #     max_signal = max(np.max(values) for _, values, _ in coincidence_curves)
# # #
# # #     if max_baseline == 0:
# # #         return 1  # Avoid division by zero
# # #
# # #     return max_signal / max_baseline
# # #
# # # # === Plot helper ===
# # # def plot_channel(data_list, title_text):
# # #     if not data_list:
# # #         print(f"[SKIPPED] {title_text} — no data found")
# # #         return
# # #
# # #     plt.figure(figsize=(12, 7))
# # #
# # #     for indices, values, label in data_list:
# # #         plt.plot(indices, values, lw=2, label=label)
# # #
# # #     plt.xlabel("Index", fontsize=font_size)
# # #     plt.ylabel("Counts", fontsize=font_size)
# # #     plt.title(title_text, fontsize=font_size)
# # #     plt.gca().xaxis.set_major_formatter(ticker.FormatStrFormatter('%.0f'))
# # #     plt.tick_params(axis='x', labelsize=font_size)
# # #     plt.tick_params(axis='y', labelsize=font_size)
# # #     plt.grid(True, linestyle='-', linewidth=0.75, alpha=0.7)
# # #     plt.legend(fontsize=font_size-2, loc='best')
# # #     plt.tight_layout()
# # #     plt.show()
# # #
# # # def plot_channel_grouped_by_instance(data_list, title_base, channel):
# # #     grouped = {}
# # #     for indices, values, label in data_list:
# # #         match = re.search(r"\((\d+)\)$", label)
# # #         instance = match.group(1) if match else "1"
# # #
# # #         if instance not in grouped:
# # #             grouped[instance] = []
# # #         grouped[instance].append((indices, values, label))
# # #
# # #     for instance, curves in grouped.items():
# # #         title = f"{title_base} — Instance {instance}"
# # #
# # #         plt.figure(figsize=(12, 7))
# # #
# # #         # Plot coincidence data
# # #         for indices, values, label in curves:
# # #             plt.plot(indices, values, lw=2, label=label)
# # #
# # #         # Determine adaptive baseline scaling
# # #         for b_indices, b_values, b_label in baseline_store[channel]:
# # #             scaling_factor = get_scaling_factor(b_values, curves)
# # #
# # #             # Optional: Cap scaling to avoid extreme blow-up
# # #             scaling_factor = min(scaling_factor, 10)
# # #
# # #             plt.plot(
# # #                 b_indices,
# # #                 b_values * scaling_factor,
# # #                 lw=2,
# # #                 linestyle='--',
# # #                 color='orange',
# # #                 label=f"{b_label} ×{scaling_factor:.1f}"
# # #             )
# # #
# # #         plt.xlabel("Index", fontsize=font_size)
# # #         plt.ylabel("Counts", fontsize=font_size)
# # #         plt.title(title, fontsize=font_size)
# # #         plt.gca().xaxis.set_major_formatter(ticker.FormatStrFormatter('%.0f'))
# # #         plt.tick_params(axis='x', labelsize=font_size)
# # #         plt.tick_params(axis='y', labelsize=font_size)
# # #         plt.grid(True, linestyle='-', linewidth=0.75, alpha=0.7)
# # #         plt.legend(fontsize=font_size - 2, loc='best')
# # #         plt.tight_layout()
# # #         plt.show()
# # #
# # #
# # # # === Plot Filtered grouped ===
# # # plot_channel_grouped_by_instance(data_store['Filtered']['CH0'], "CH0 Curves (Filtered)", "CH0")
# # # plot_channel_grouped_by_instance(data_store['Filtered']['CH1'], "CH1 Curves (Filtered)", "CH1")
# # #
# # # # === Plot Unfiltered grouped ===
# # # if plot_unfiltered:
# # #     plot_channel_grouped_by_instance(data_store['Unfiltered']['CH0'], "CH0 Curves (Unfiltered)", "CH0")
# # #     plot_channel_grouped_by_instance(data_store['Unfiltered']['CH1'], "CH1 Curves (Unfiltered)", "CH1")
# # #
# # # # === Plot Raw grouped ===
# # # if plot_raw:
# # #     plot_channel_grouped_by_instance(data_store['Raw']['CH0'], "CH0 Curves (Raw)", "CH0")
# # #     plot_channel_grouped_by_instance(data_store['Raw']['CH1'], "CH1 Curves (Raw)", "CH1")
