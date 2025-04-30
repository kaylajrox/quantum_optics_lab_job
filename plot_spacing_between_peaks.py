import pandas as pd
import matplotlib.pyplot as plt

# Load the slope summary
df = pd.read_csv('results_spacing_from_slope.csv')

# Clean up just in case
df.columns = df.columns.str.strip()

# Sort and group
df = df.sort_values(by=["Channel", "Pulse Height (V)", "Gain Voltage (V)"])

# Save simplified slope-vs-gain data
slope_vs_gain_file = 'results_slope_vs_gain_voltage.csv'
df[["Channel", "Pulse Height (V)", "Gain Voltage (V)", "Average Spacing"]].to_csv(slope_vs_gain_file, index=False)
print(f"✅ Saved slope vs gain voltage to: {slope_vs_gain_file}")

# Plot: One figure per channel
for ch in df["Channel"].unique():
    df_ch = df[df["Channel"] == ch]
    plt.figure(figsize=(8, 6))

    for pulse in sorted(df_ch["Pulse Height (V)"].unique()):
        df_pulse = df_ch[df_ch["Pulse Height (V)"] == pulse]
        plt.plot(
            df_pulse["Gain Voltage (V)"],
            df_pulse["Average Spacing"],
            marker='o',
            linestyle='-',
            label=f'{pulse}V pulse'
        )

    plt.title(f"{ch} — Average Slope vs. Gain Voltage")
    plt.xlabel("Gain Voltage (V)")
    plt.ylabel("Average Spacing")
    plt.grid(True)
    plt.legend(title="Pulse Height")
    plt.tight_layout()
    plt.show()



# import matplotlib
# matplotlib.use('TkAgg')  # For PyCharm interactivity
#
# import pandas as pd
# import matplotlib.pyplot as plt
#
# # Independent crop values
# crop_off_by_pulse = {
#     1.3: 0,  # Crop 2 from 1.3V
#     1.6: 0   # Crop 1 from 1.6V
# }
#
# CH_num = 'CH1'  # Channel to plot
#
# # Load data
# df = pd.read_csv('results_combined_peak_data_old.csv')
# df['Index Difference'] = pd.to_numeric(df['Index Difference'], errors='coerce')
# df = df[df['Channel (from filename)'] == CH_num]
#
# gain_voltages = sorted(df['Gain Voltage (from filename)'].unique())
#
# # Plot per gain voltage
# for gain_v in gain_voltages:
#     plt.figure(figsize=(8, 6))
#
#     for pulse_height, color in zip([1.3, 1.6], ['green', 'orange']):
#         subset = df[
#             (df['Gain Voltage (from filename)'] == gain_v) &
#             (df['Pulse Height (from filename)'] == pulse_height)
#         ].copy()
#
#         subset = subset.dropna(subset=['Index Difference'])
#
#         crop_off = crop_off_by_pulse.get(pulse_height, 0)
#         if crop_off > 0 and len(subset) > crop_off:
#             subset = subset.iloc[:-crop_off]
#
#         plt.plot(
#             subset['Peak Number'],
#             subset['Index Difference'],
#             marker='o',
#             linestyle='-',
#             label=f'{pulse_height}V Pulse',
#             color=color
#         )
#
#     plt.title(f'{CH_num} — Peak Spacing vs. Peak Number Difference (Gain = {gain_v} V)')
#     plt.xlabel('Spacing between Peak Number')
#     plt.ylabel('Index Difference (Spacing)')
#     plt.grid(True)
#     plt.legend(title='Pulse Height')
#     plt.tight_layout()
#     plt.show()
#
#
