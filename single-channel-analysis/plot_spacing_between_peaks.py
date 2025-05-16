import matplotlib
matplotlib.use('TkAgg')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path
import matplotlib.ticker as ticker

def plot_spacing_between_peaks():
    # === Paths Setup ===
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent
    results_dir = repo_root / 'results-from-generated-data'
    data_file = results_dir / 'results_spacing_from_slope.csv'

    # === Load Data ===
    print(f"\n🟢 Loading data from file: {data_file}")
    if not data_file.exists():
        raise FileNotFoundError(f"❌ File does not exist: {data_file}")

    df = pd.read_csv(data_file)
    df.columns = df.columns.str.strip()  # Clean headers

    print("\n📊 Full DataFrame Preview (first 10 rows):")
    print(df['Fitted Slope'])

    # === Explicit Column Mapping ===
    channel_col = 'Channel'
    gain_col = 'Gain Voltage (V)'
    pulse_col = 'Pulse Height (V)'
    spacing_col = 'Average Spacing'
    std_col = 'Standard Deviation'

    # === Plotting ===
    font_size = 24

    for ch in df[channel_col].unique():
        df_ch = df[df[channel_col] == ch]

        print(f"\n==== SANITY CHECK: Channel = {ch} ====")
        for gain in sorted(df_ch[gain_col].unique()):
            df_gain = df_ch[df_ch[gain_col] == gain]
            pulse_heights = df_gain[pulse_col].unique()
            spacings = df_gain[spacing_col].values
            print(f"Gain Voltage {gain}: {len(pulse_heights)} pulses -> Pulse Heights: {pulse_heights}")
            print(f"    Spacing values used: {spacings}")

        # Group by Gain Voltage to compute mean/std for plotting
        grouped = df_ch.groupby(gain_col)[spacing_col].agg(['mean', 'std']).reset_index()

        print("\n🟡 Grouped Mean & Std being plotted:")
        print(grouped)

        x = grouped[gain_col].values
        y = grouped['mean'].values
        yerr = grouped['std'].values

        plt.figure(figsize=(10, 6))
        plt.errorbar(x, y, yerr=yerr, fmt='o-', capsize=4, label=f'{ch} (mean ± std)', color='black')

        # Annotating points
        x_offset = 0.015
        y_offset = 1
        for i, (xi, yi) in enumerate(zip(x, y)):
            is_last = i == len(x) - 1
            adjusted_x = xi - x_offset if is_last else xi + x_offset
            plt.text(adjusted_x, yi + y_offset, f'{yi:.2f}', fontsize=14, ha='center', va='bottom', color='black')

        # Linear Fit
        if len(np.unique(x)) >= 2:
            coeffs = np.polyfit(x, y, deg=1)
            x_fit = np.linspace(min(x), max(x), 300)
            y_fit = np.polyval(coeffs, x_fit)
            plt.plot(x_fit, y_fit, 'r--', label=f'Linear Fit: y = {coeffs[0]:.3f}x + {coeffs[1]:.2f}')
            plt.text(x_fit[-1]-0.15, y_fit[-1]-1, f'y = {coeffs[0]:.3f}x + {coeffs[1]:.2f}',
                     fontsize=16, color='red', ha='right', va='bottom')
        else:
            print(f"⚠ Not enough points to fit line for {ch}.")

        plt.title(f'{ch} — Average Spacing vs. Gain Voltage', fontsize=font_size)
        plt.xlabel('Gain Voltage (V)', fontsize=font_size)
        plt.ylabel('Average Spacing (Slope)', fontsize=font_size)
        plt.gca().xaxis.set_major_formatter(ticker.FormatStrFormatter('%.1f'))
        plt.tick_params(axis='x', labelsize=font_size)
        plt.tick_params(axis='y', labelsize=font_size)
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

if __name__ == '__main__':
    plot_spacing_between_peaks()

