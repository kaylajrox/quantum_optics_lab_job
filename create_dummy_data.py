import pandas as pd
import numpy as np
from pathlib import Path

def create_dummy_peak_data(output_path: Path):
    n_peaks = 20

    data = {
        'Peak Number': np.arange(1, n_peaks + 1),
        'Peak Index': np.arange(1, n_peaks + 1),          # <-- Added Peak Index here
        'Pulse Height (V)': np.random.uniform(0.05, 0.5, size=n_peaks),
        'Gain Voltage (V)': np.full(n_peaks, 65.7),
        'Channel': np.random.choice(['CH0', 'CH1'], size=n_peaks),
        'Peak Position (s)': np.linspace(0.1, 10, n_peaks),
        'Peak Width (s)': np.random.uniform(0.01, 0.1, size=n_peaks),
        'Peak Slope': np.random.uniform(0.1, 5, size=n_peaks),
    }

    df = pd.DataFrame(data)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Created dummy peak data at: {output_path}")

if __name__ == "__main__":
    output_file = Path("results-from-generated-data/all_peaks_combined_sorted.csv")
    create_dummy_peak_data(output_file)
