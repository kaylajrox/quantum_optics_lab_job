import matplotlib
matplotlib.use('TkAgg')  # For PyCharm interactivity

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load the combined CSV
df = pd.read_csv('results_combined_peak_data.csv')
df.columns = df.columns.str.strip()

df['Peak Number'] = pd.to_numeric(df['Peak Number'], errors='coerce')
df['Peak Index'] = pd.to_numeric(df['Peak Index'], errors='coerce')
df = df.dropna(subset=['Peak Number', 'Peak Index'])

# Optional: consistent color map
pulse_color_map = {
    1.0: 'black',
    1.1: 'darkblue',
    1.3: 'green',
    1.6: 'orange',
    2.0: 'deeppink',
    2.3: 'red'
}

# Group by channel
for ch in df['Channel (from filename)'].unique():
    df_ch = df[df['Channel (from filename)'] == ch]
    gain_voltages = sorted(df_ch['Gain Voltage (from filename)'].unique())

    for gain in gain_voltages:
        plt.figure(figsize=(8, 6))
        df_gain = df_ch[df_ch['Gain Voltage (from filename)'] == gain]

        print(f"\n=== CHANNEL: {ch} | GAIN VOLTAGE: {gain} V ===")

        for pulse_height in sorted(df_gain['Pulse Height (from filename)'].unique()):
            df_pulse = df_gain[df_gain['Pulse Height (from filename)'] == pulse_height]
            df_pulse = df_pulse.sort_values('Peak Number')

            x = df_pulse['Peak Number'].values
            y = df_pulse['Peak Index'].values
            color = pulse_color_map.get(pulse_height, 'gray')

            print(f"\n→ Pulse Height = {pulse_height} V")

            if len(x) >= 2:
                # Individual slopes
                slopes = np.diff(y) / np.diff(x)
                avg_slope = np.mean(slopes)
                slope_std = np.std(slopes)

                for i, s in enumerate(slopes, start=1):
                    print(f"   Slope between Peak {i} & {i+1}: {s:.2f}")

                print(f"   ↪ Average Slope: {avg_slope:.2f}")
                print(f"   ↪ Std Dev of Slopes: {slope_std:.2f}")

                # Fit linear model
                coeffs = np.polyfit(x, y, deg=1)
                x_fit = np.linspace(min(x), max(x), 300)
                y_fit = np.polyval(coeffs, x_fit)

                # Plot fit
                plt.plot(x_fit, y_fit, linestyle='--', color=color, label=f'{pulse_height}V fit')

                # Annotate equation
                eqn_str = f'y = {coeffs[0]:.2f}x + {coeffs[1]:.1f}'
                x_pos = x_fit[-1] + 0.2
                y_pos = y_fit[-1]
                plt.text(x_pos, y_pos, eqn_str, fontsize=11, color=color, va='center')

            else:
                print("   ⚠ Not enough data points to compute slope or fit.")

            # Plot data points with solid lines
            plt.plot(x, y, marker='o', linestyle='-', color=color, label=f'{pulse_height}V pulse')

        plt.title(f'{ch} — Peak Index vs. Peak Number (Gain = {gain} V)')
        plt.xlabel('Peak Number')
        plt.ylabel('Peak Index')
        plt.grid(True)
        plt.legend(title='Pulse Height')
        plt.tight_layout()
        plt.show()
