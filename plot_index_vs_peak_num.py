
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import os

# Load the combined CSV
df = pd.read_csv('results_combined_peak_data.csv')
df.columns = df.columns.str.strip()

df['Peak Number'] = pd.to_numeric(df['Peak Number'], errors='coerce')
df['Peak Index'] = pd.to_numeric(df['Peak Index'], errors='coerce')
df = df.dropna(subset=['Peak Number', 'Peak Index'])

# Output CSV
slope_summary_file = 'results_spacing_from_slope.csv'

# Initialize storage for summary rows
slope_summary_rows = []

# Group by channel
for ch in df['Channel (from filename)'].unique():
    df_ch = df[df['Channel (from filename)'] == ch]
    gain_voltages = sorted(df_ch['Gain Voltage (from filename)'].unique())

    for gain in gain_voltages:
        df_gain = df_ch[df_ch['Gain Voltage (from filename)'] == gain]

        for pulse_height in sorted(df_gain['Pulse Height (from filename)'].unique()):
            df_pulse = df_gain[df_gain['Pulse Height (from filename)'] == pulse_height]
            df_pulse = df_pulse.sort_values('Peak Number')

            x = df_pulse['Peak Number'].values
            y = df_pulse['Peak Index'].values

            if len(x) >= 2:
                slopes = np.diff(y) / np.diff(x)
                avg_slope = np.mean(slopes)
                slope_std = np.std(slopes)
                timestamp_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                slope_summary_rows.append({
                    "Timestamp": timestamp_str,
                    "Channel": ch,
                    "Gain Voltage (V)": gain,
                    "Pulse Height (V)": pulse_height,
                    "Average Spacing": avg_slope,
                    "Spacing (from slope) Std Dev": slope_std
                })

# Convert to DataFrame and save
slope_summary_df = pd.DataFrame(slope_summary_rows)
slope_summary_df = slope_summary_df.sort_values(by=["Channel", "Gain Voltage (V)", "Pulse Height (V)"])

slope_summary_df.to_csv(slope_summary_file, index=False)
print(f"✅ Slope summary written to: {slope_summary_file}")


# import pandas as pd
# import matplotlib.pyplot as plt
# import numpy as np
#
# # Load the combined CSV
# df = pd.read_csv('results_combined_peak_data.csv')
# df.columns = df.columns.str.strip()
#
# df['Peak Number'] = pd.to_numeric(df['Peak Number'], errors='coerce')
# df['Peak Index'] = pd.to_numeric(df['Peak Index'], errors='coerce')
#
# df = df.dropna(subset=['Peak Number', 'Peak Index'])
#
# # Group by channel
# for ch in df['Channel (from filename)'].unique():
#     df_ch = df[df['Channel (from filename)'] == ch]
#     gain_voltages = sorted(df_ch['Gain Voltage (from filename)'].unique())
#
#     for gain in gain_voltages:
#         plt.figure(figsize=(8, 6))
#         df_gain = df_ch[df_ch['Gain Voltage (from filename)'] == gain]
#
#         print(f"\n=== {ch} | Gain Voltage = {gain} V ===")
#
#         for pulse_height in sorted(df_gain['Pulse Height (from filename)'].unique()):
#             df_pulse = df_gain[df_gain['Pulse Height (from filename)'] == pulse_height]
#             df_pulse = df_pulse.sort_values('Peak Number')
#
#             x = df_pulse['Peak Number'].values
#             y = df_pulse['Peak Index'].values
#
#             # Compute slopes
#             if len(x) >= 2:
#                 slopes = np.diff(y) / np.diff(x)
#                 avg_slope = np.mean(slopes)
#
#                 print(f"\nPulse Height = {pulse_height} V")
#                 print("Slopes between peaks:")
#                 for i, s in enumerate(slopes, start=1):
#                     print(f"  Slope {i}: {s:.2f}")
#
#                 slope_std = np.std(slopes)
#                 print(f"Average Slope: {avg_slope:.2f}")
#                 print(f"Standard Deviation of Slopes: {slope_std:.2f}")
#
#             else:
#                 print(f"\nPulse Height = {pulse_height} V — Not enough points to compute slope.")
#
#             # Plotting
#             plt.plot(x, y, marker='o', linestyle='-', label=f'{pulse_height}V pulse')
#
#         plt.title(f'{ch} — Peak Index vs. Peak Number (Gain = {gain} V)')
#         plt.xlabel('Peak Number')
#         plt.ylabel('Peak Index')
#         plt.grid(True)
#         plt.legend(title='Pulse Height')
#         plt.tight_layout()
#         plt.show()
