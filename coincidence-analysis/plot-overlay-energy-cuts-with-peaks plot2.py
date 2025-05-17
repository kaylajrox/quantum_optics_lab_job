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

# === Plot Toggles ===
plot_unfiltered = False
plot_raw = False

# === Data storage ===
data_store = {
    'Filtered': {'CH0': [], 'CH1': []},
    'Unfiltered': {'CH0': [], 'CH1': []},
    'Raw': {'CH0': [], 'CH1': []},
}

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

    name_lower = subfolder.name.lower()
    if "filtered" in name_lower:
        filter_state = "Filtered"
    elif "unfiltered" in name_lower:
        filter_state = "Unfiltered"
    else:
        filter_state = "Raw"

    print(f"[PROCESSING] {subfolder.name} | Peak {peak1} & {peak2} | {filter_state}")

    for file_path in sorted(subfolder.glob("*.txt")):
        filename = file_path.name

        if filename.startswith("Data"):
            print(f"[SKIPPED] {filename} (CSV-like file)")
            continue

        try:
            data = np.loadtxt(file_path)
            indices_cropped = np.arange(len(data))[crop_start_amount:-crop_end_amount]
            data_cropped = data[crop_start_amount:-crop_end_amount]
        except Exception as e:
            print(f"[ERROR] Could not load {file_path}: {e}")
            continue

        label = f"Peak {peak1} & {peak2}"

        if "CH0@" in filename:
            data_store[filter_state]['CH0'].append((indices_cropped, data_cropped, label))
        elif "CH1@" in filename:
            data_store[filter_state]['CH1'].append((indices_cropped, data_cropped, label))

# === Deduplicate peak labels ===
def deduplicate_peak_labels(data_list):
    seen = set()
    deduped = []
    for indices, values, label in data_list:
        if label not in seen:
            deduped.append((indices, values, label))
            seen.add(label)
    return deduped

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

# === Always plot Filtered ===
plot_channel(deduplicate_peak_labels(data_store['Filtered']['CH0']), "CH0 Curves (Filtered)")
plot_channel(deduplicate_peak_labels(data_store['Filtered']['CH1']), "CH1 Curves (Filtered)")

# === Conditionally plot Unfiltered ===
if plot_unfiltered:
    plot_channel(deduplicate_peak_labels(data_store['Unfiltered']['CH0']), "CH0 Curves (Unfiltered)")
    plot_channel(deduplicate_peak_labels(data_store['Unfiltered']['CH1']), "CH1 Curves (Unfiltered)")

# === Conditionally plot Raw ===
if plot_raw:
    plot_channel(deduplicate_peak_labels(data_store['Raw']['CH0']), "CH0 Curves (Raw)")
    plot_channel(deduplicate_peak_labels(data_store['Raw']['CH1']), "CH1 Curves (Raw)")
