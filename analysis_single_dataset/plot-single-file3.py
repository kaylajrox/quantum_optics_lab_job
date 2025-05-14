import matplotlib
matplotlib.use('TkAgg')  # For PyCharm interactivity

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

crop_start_amount = 100
crop_end_amount = 3000

# === USER CONFIGURATION ===
coic_data_folder_name = "20250507_more_peaks_compare_coicdence"
peak_baseline_data_folder_name = "20250507_baseline_data_for_coic_comparison"

coic_baseline_data = "peak4_and4_750ns_correlation_window_65_7_gain_1_6_pulse_60s_filtered"
peak_baseline_data = "65_7_gain_1_6_pulse_60s"

filenames = [
    ("CH1@DT5720B_75_EspectrumF_peak_4_and4_750_ns_20250507_151921.txt", "CH1"),
    ("CH0@DT5720B_75_EspectrumF_peak_4_and4_750_ns_20250507_151921.txt", "CH0"),
    ("0@AddBack_EspectrumF_peak_4_and4_750_ns_20250507_151921.txt", "AddBack"),
    ("CH0@DT5720B_75_EspectrumR_65_7_gain_1_6V_pulse_60s_05_20250507_145259.txt", "CH0 original"),
    ("CH1@DT5720B_75_EspectrumR_65_7_gain_1_6V_pulse_60s_05_20250507_145259.txt", "CH1 original")
]

# === PATH SETUP ===
repo_root = Path(__file__).resolve().parents[1]
coic_directory = repo_root / "data-photon-counts-SiPM" / coic_data_folder_name / coic_baseline_data
peaks_to_compare_data_directory = repo_root / "data-photon-counts-SiPM" / peak_baseline_data_folder_name / peak_baseline_data

plot_data = []

for fname, label in filenames:
    if "original" in label:
        file_path = peaks_to_compare_data_directory / fname
    else:
        file_path = coic_directory / fname

    print(f"Loading from: {file_path}")

    assert file_path.exists(), f"File not found: {file_path}"
    data = np.loadtxt(file_path)
    data_cropped = data[crop_start_amount:-crop_end_amount]
    indices = np.arange(len(data_cropped))
    plot_data.append((indices, data_cropped, label))

# === PLOT ===
plt.figure(figsize=(10, 6))
for indices, values, label in plot_data:
    if "original" in label:
        plt.plot(indices, values * 5, lw=2, linestyle='--', label=label)
    else:
        plt.plot(indices, values, lw=2, label=label)

plt.xlabel("Index")
plt.ylabel("Value")
plt.title(f"Cropped Plot of {coic_baseline_data}")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
