import matplotlib
matplotlib.use('TkAgg')  # For PyCharm interactivity

import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file
df = pd.read_csv('results_spacing_from_slope.csv')

# Clean up column names
df.columns = df.columns.str.strip()

# Sort for consistent plotting
df = df.sort_values(by=["Channel", "Pulse Height (V)", "Gain Voltage (V)"])

# Save simplified slope-vs-gain data
slope_vs_gain_file = 'results_spacing_from_slope.csv'
df[["Channel", "Pulse Height (V)", "Gain Voltage (V)", "Average Spacing"]].to_csv(slope_vs_gain_file, index=False)
print(f"✅ Saved slope vs gain voltage to: {slope_vs_gain_file}")

# Plot: one figure per channel
for ch in df["Channel"].unique():
    df_ch = df[df["Channel"] == ch]
    plt.figure(figsize=(8, 6))

    for pulse in sorted(df_ch["Pulse Height (V)"].unique()):
        df_pulse = df_ch[df_ch["Pulse Height (V)"] == pulse]

        plt.errorbar(
            df_pulse["Gain Voltage (V)"],
            df_pulse["Average Spacing"],
            yerr=df_pulse["Spacing (from slope) Std Dev"],
            fmt='o-',
            capsize=5,
            label=f'{pulse}V pulse'
        )

    plt.title(f"{ch} — Average Spacing vs. Gain Voltage")
    plt.xlabel("Gain Voltage (V)")
    plt.ylabel("Average Spacing")
    plt.grid(True)
    plt.legend(title="Pulse Height")
    plt.tight_layout()
    plt.show()
