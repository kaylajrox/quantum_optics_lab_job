import matplotlib
matplotlib.use('TkAgg')

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import re
import matplotlib.ticker as ticker

# === CONFIG ===
repo_root = Path(__file__).resolve().parents[1]
coic_data_dir = repo_root / "data-photon-counts-SiPM" / "20250507_more_peaks_compare_coicdence"
crop_start_amount = 100
crop_end_amount = 3150
font_size = 20

# === Peaks to EXCLUDE ===
exclude_peak_numbers = ["5", "9"]

# === Plot Toggles ===
plot_unfiltered = False
plot_raw = False

# === Data storage ===
data_store = {
    'Filtered': {'CH0': [], 'CH1': []},
    'Unfiltered': {'CH0': [], 'CH1': []},
    'Raw': {'CH0': [], 'CH1': []},
}

# === Label counts ===
label_counts = {}

# === Extract peak numbers ===
def extract_peak_numbers(folder_name):
    match = re.search(r"peak(\d+)_and(\d+)", folder_name)
    if match:
        return match.group(1), match.group(2)
    return None, None

# === Iterate directories ===
for subfolder in sorted(coic_data_dir.iterdir()):
    if not subfolder.is_dir():
        continue

    peak1, peak2 = extract_peak_numbers(subfolder.name)
    if not peak1:
        print(f"[SKIPPED] Could not parse peak numbers from {subfolder.name}")
        continue

    # Exclude peaks logic
    if peak1 in exclude_peak_numbers or peak2 in exclude_peak_numbers:
        print(f"[SKIPPED] {subfolder.name} — peaks excluded: {exclude_peak_numbers}")
        continue

    # Filter state detection
    name_lower = subfolder.name.lower()
    if "filtered" in name_lower:
        filter_state = "Filtered"
    elif "unfiltered" in name_lower:
        filter_state = "Unfiltered"
    else:
        print(f"[SKIPPED] {subfolder.name} — no 'filtered'/'unfiltered' keyword found, skipping")
        continue

    print(f"[PROCESSING] {subfolder.name} | Peak {peak1} & {peak2} | {filter_state}")

    for file_path in sorted(subfolder.glob("*.txt")):
        filename = file_path.name

        if filename.startswith("Data"):
            continue

        try:
            data = np.loadtxt(file_path)
            indices_cropped = np.arange(len(data))[crop_start_amount:-crop_end_amount]
            data_cropped = data[crop_start_amount:-crop_end_amount]
        except Exception as e:
            print(f"[ERROR] Could not load {file_path}: {e}")
            continue

        # Build and uniquify label
        label = f"Peak {peak1} & {peak2}"
        channel = "CH0" if "CH0@" in filename else "CH1"
        label_key = (filter_state, channel, label)

        count = label_counts.get(label_key, 0) + 1
        label_counts[label_key] = count

        if count > 1:
            label = f"{label} ({count})"

        data_store[filter_state][channel].append((indices_cropped, data_cropped, label))

# === Plot helper ===
def plot_channel(data_list, title_text):
    if not data_list:
        print(f"[SKIPPED] {title_text} — no data found")
        return

    plt.figure(figsize=(12, 7))

    for indices, values, label in data_list:
        plt.plot(indices, values, lw=2, label=label)

    plt.xlabel("Index", fontsize=font_size)
    plt.ylabel("Counts", fontsize=font_size)
    plt.title(title_text, fontsize=font_size)
    plt.gca().xaxis.set_major_formatter(ticker.FormatStrFormatter('%.0f'))
    plt.tick_params(axis='x', labelsize=font_size)
    plt.tick_params(axis='y', labelsize=font_size)
    plt.grid(True, linestyle='-', linewidth=0.75, alpha=0.7)
    plt.legend(fontsize=font_size-2, loc='best')
    plt.tight_layout()
    plt.show()

# === Grouped by Instance plotting ===
def plot_channel_grouped_by_instance(data_list, title_base):
    grouped = {}
    for indices, values, label in data_list:
        match = re.search(r"\((\d+)\)$", label)
        instance = match.group(1) if match else "1"

        if instance not in grouped:
            grouped[instance] = []
        grouped[instance].append((indices, values, label))

    for instance, curves in grouped.items():
        title = f"{title_base} — Instance {instance}"
        plot_channel(curves, title)

# === Plot Filtered grouped ===
plot_channel_grouped_by_instance(data_store['Filtered']['CH0'], "CH0 Curves (Filtered)")
plot_channel_grouped_by_instance(data_store['Filtered']['CH1'], "CH1 Curves (Filtered)")

# === Plot Unfiltered grouped ===
if plot_unfiltered:
    plot_channel_grouped_by_instance(data_store['Unfiltered']['CH0'], "CH0 Curves (Unfiltered)")
    plot_channel_grouped_by_instance(data_store['Unfiltered']['CH1'], "CH1 Curves (Unfiltered)")

# === Plot Raw grouped ===
if plot_raw:
    plot_channel_grouped_by_instance(data_store['Raw']['CH0'], "CH0 Curves (Raw)")
    plot_channel_grouped_by_instance(data_store['Raw']['CH1'], "CH1 Curves (Raw)")
