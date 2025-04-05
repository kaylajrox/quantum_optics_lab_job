import os
import pandas as pd
import matplotlib.pyplot as plt

# Path to the top-level 'photon_counts_data' folder
root_dir = "photon_counts_data"

for folder in os.listdir(root_dir):
    if folder.startswith("SiPM_TTL_"):
        match_id = folder.split("SiPM_TTL_")[-1]
        raw_path = os.path.join(root_dir, folder, "DAQ", match_id, "RAW")

        if not os.path.exists(raw_path):
            print(f"No RAW folder found for {folder}")
            continue

        csv_files = [f for f in os.listdir(raw_path)
                     if f.lower().endswith(".csv") and "dark" not in f.lower()]

        if len(csv_files) < 2:
            print(f"Not enough CSVs in {raw_path}")
            continue

        csv_paths = sorted([os.path.join(raw_path, f) for f in csv_files])

        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        fig.suptitle(f"{folder} - RAW", fontsize=14)

        for i, file_path in enumerate(csv_paths[:2]):
            try:
                df = pd.read_csv(file_path, sep=';')
                ax = axes[i]
                ax.plot(df["TIMETAG"], df["ENERGY"], linewidth=0.8)
                ax.set_title(os.path.basename(file_path), fontsize=10)
                ax.set_xlabel("TIMETAG")
                ax.set_ylabel("ENERGY")
            except Exception as e:
                print(f"Error reading {file_path}: {e}")

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.show()
