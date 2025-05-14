'''
How It Works
--------------------------------
Data Loading:
Reads the source file (../results_combined_peak_data.csv) and ensures numeric types for Peak Number, Peak Index, and Peak Counts.
Drops rows with missing values in these columns.

==================================================
Grouping:
-Groups data by Channel (from filename), Gain Voltage (from filename), and Pulse Height (from filename).
Calculations:
--------------------------------------------
Calculations for each group:
-Sorts data by Peak Number.
-Calculates slopes between consecutive peaks (Peak Index differences divided by Peak Number differences).
-Computes the average slope and standard deviation of slopes.

======================================
Output Writing:
-Writes summary data to ../results_spacing_from_slope.csv.
-Writes detailed data (including individual peak information) to ../results_detailed_peak_data.csv

=======================================

Usage
-Place the source file (results_combined_peak_data.csv) in the appropriate directory.
-Run the script:
-python plot_index_vs_peak_num_detailed_analysis_table.py
-The output files will be generated in the parent directory:
-results_spacing_from_slope.csv
-results_detailed_peak_data.csv

============================================================
'''



import pandas as pd
import numpy as np
from datetime import datetime
import csv

# Load the combined peak data
source_file = '../results_combined_peak_data.csv'
df = pd.read_csv(source_file)
df.columns = df.columns.str.strip()

# Setup original summary output
summary_csv = '../results_spacing_from_slope.csv'
detailed_csv = '../results_detailed_peak_data.csv'

# Ensure numeric types for sorting and calculations
df['Peak Number'] = pd.to_numeric(df['Peak Number'], errors='coerce')
df['Peak Index'] = pd.to_numeric(df['Peak Index'], errors='coerce')
df['Peak Counts'] = pd.to_numeric(df['Peak Counts'], errors='coerce')
df = df.dropna(subset=['Peak Number', 'Peak Index', 'Peak Counts'])

with open(summary_csv, mode='w', newline='') as f_summary, open(detailed_csv, mode='w', newline='') as f_detailed:
    summary_writer = csv.writer(f_summary)
    detailed_writer = csv.writer(f_detailed)

    # Write headers
    summary_writer.writerow([
        'Current time of data made', 'Channel', 'Pulse Height (V)',
        'Gain Voltage (V)', 'Average Spacing', 'Standard Deviation', 'Source File'
    ])
    detailed_writer.writerow([
        'Current time of data made', 'Channel', 'Pulse Height (V)',
        'Gain Voltage (V)', 'Peak Number', 'Peak Index',
        'Peak Counts', 'Average Spacing', 'Standard Deviation', 'Source File'
    ])

    # Grouping and writing
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
                counts = df_pulse['Peak Counts'].values

                if len(x) >= 2:
                    slopes = np.diff(y) / np.diff(x)
                    avg_slope = np.mean(slopes)
                    slope_std = np.std(slopes)
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                    # Write summary row
                    summary_writer.writerow([timestamp, ch, pulse_height, gain, avg_slope, slope_std, source_file])

                    # Write detailed rows
                    for i in range(len(df_pulse)):
                        detailed_writer.writerow([
                            timestamp, ch, pulse_height, gain,
                            x[i], y[i], counts[i], avg_slope, slope_std, source_file
                        ])


# import pandas as pd
# import numpy as np
# from datetime import datetime
# import csv
#
#
#
# # Load the combined peak data
# df = pd.read_csv('../results_combined_peak_data.csv')
# df.columns = df.columns.str.strip()
#
# # Setup original summary output
# summary_csv = '../results_spacing_from_slope.csv'
# detailed_csv = '../results_detailed_peak_data.csv'
#
# # Ensure numeric types for sorting and calculations
# df['Peak Number'] = pd.to_numeric(df['Peak Number'], errors='coerce')
# df['Peak Index'] = pd.to_numeric(df['Peak Index'], errors='coerce')
# df['Peak Counts'] = pd.to_numeric(df['Peak Counts'], errors='coerce')
# df = df.dropna(subset=['Peak Number', 'Peak Index', 'Peak Counts'])
#
#
# with open(summary_csv, mode='w', newline='') as f_summary, open(detailed_csv, mode='w', newline='') as f_detailed:
#     summary_writer = csv.writer(f_summary)
#     detailed_writer = csv.writer(f_detailed)
#
#     # Write headers
#     summary_writer.writerow([
#         'Current time of data made', 'Channel', 'Pulse Height (V)',
#         'Gain Voltage (V)', 'Average Spacing', 'Standard Deviation'
#     ])
#     detailed_writer.writerow([
#         'Current time of data made', 'Channel', 'Pulse Height (V)',
#         'Gain Voltage (V)', 'Peak Number', 'Peak Index',
#         'Peak Counts', 'Average Spacing', 'Standard Deviation'
#     ])
#
#     # Grouping and writing
#     for ch in df['Channel (from filename)'].unique():
#         df_ch = df[df['Channel (from filename)'] == ch]
#         gain_voltages = sorted(df_ch['Gain Voltage (from filename)'].unique())
#
#         for gain in gain_voltages:
#             df_gain = df_ch[df_ch['Gain Voltage (from filename)'] == gain]
#
#             for pulse_height in sorted(df_gain['Pulse Height (from filename)'].unique()):
#                 df_pulse = df_gain[df_gain['Pulse Height (from filename)'] == pulse_height]
#                 df_pulse = df_pulse.sort_values('Peak Number')
#
#                 x = df_pulse['Peak Number'].values
#                 y = df_pulse['Peak Index'].values
#                 counts = df_pulse['Peak Counts'].values
#
#                 if len(x) >= 2:
#                     slopes = np.diff(y) / np.diff(x)
#                     avg_slope = np.mean(slopes)
#                     slope_std = np.std(slopes)
#                     timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#
#                     # Write summary row
#                     summary_writer.writerow([timestamp, ch, pulse_height, gain, avg_slope, slope_std])
#
#                     # Write detailed rows
#                     for i in range(len(df_pulse)):
#                         detailed_writer.writerow([
#                             timestamp, ch, pulse_height, gain,
#                             x[i], y[i], counts[i], avg_slope, slope_std
#                         ])
#
#
#
#
# # import matplotlib
# # matplotlib.use('TkAgg')  # For PyCharm interactivity
# #
# # import pandas as pd
# # import matplotlib.pyplot as plt
# # import numpy as np
# # from datetime import datetime
# # import csv
# #
# # # Load data
# # df = pd.read_csv('../results_combined_peak_data.csv')
# # df.columns = df.columns.str.strip()
# # df['Peak Number'] = pd.to_numeric(df['Peak Number'], errors='coerce')
# # df['Peak Index'] = pd.to_numeric(df['Peak Index'], errors='coerce')
# # df = df.dropna(subset=['Peak Number', 'Peak Index'])
# #
# # # Setup output file
# # csv_filename = '../results_spacing_from_slope.csv'
# # with open(csv_filename, mode='w', newline='') as file:
# #     writer = csv.writer(file)
# #     writer.writerow([
# #         'Current time of data made', 'Channel', 'Pulse Height (V)',
# #         'Gain Voltage (V)', 'Average Spacing', 'Standard Deviation'
# #     ])
# #
# #     pulse_color_map = {
# #         1.0: 'black', 1.1: 'darkblue', 1.3: 'green',
# #         1.6: 'orange', 2.0: 'deeppink', 2.3: 'red'
# #     }
# #
# #     for ch in df['Channel (from filename)'].unique():
# #         df_ch = df[df['Channel (from filename)'] == ch]
# #         gain_voltages = sorted(df_ch['Gain Voltage (from filename)'].unique())
# #
# #         for gain in gain_voltages:
# #             plt.figure(figsize=(8, 6))
# #             df_gain = df_ch[df_ch['Gain Voltage (from filename)'] == gain]
# #
# #             print(f"\n=== CHANNEL: {ch} | GAIN VOLTAGE: {gain} V ===")
# #
# #             for pulse_height in sorted(df_gain['Pulse Height (from filename)'].unique()):
# #                 df_pulse = df_gain[df_gain['Pulse Height (from filename)'] == pulse_height]
# #                 df_pulse = df_pulse.sort_values('Peak Number')
# #
# #                 x = df_pulse['Peak Number'].values
# #                 y = df_pulse['Peak Index'].values
# #                 color = pulse_color_map.get(pulse_height, 'gray')
# #
# #                 print(f"\n→ Pulse Height = {pulse_height} V")
# #
# #                 if len(x) >= 2:
# #                     slopes = np.diff(y) / np.diff(x)
# #                     avg_slope = np.mean(slopes)
# #                     slope_std = np.std(slopes)
# #                     timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
# #
# #                     for i, s in enumerate(slopes, start=1):
# #                         print(f"   Slope between Peak {i} & {i+1}: {s:.2f}")
# #                     print(f"   ↪ Average Slope: {avg_slope:.2f}")
# #                     print(f"   ↪ Std Dev of Slopes: {slope_std:.2f}")
# #
# #                     # Save to CSV
# #                     writer.writerow([timestamp, ch, pulse_height, gain, avg_slope, slope_std])
# #
# #                     # Fit line
# #                     coeffs = np.polyfit(x, y, deg=1)
# #                     x_fit = np.linspace(min(x), max(x), 300)
# #                     y_fit = np.polyval(coeffs, x_fit)
# #                     plt.plot(x_fit, y_fit, linestyle='--', color=color, label=f'{pulse_height}V fit')
# #
# #                     # Annotate
# #                     eqn_str = f'y = {coeffs[0]:.2f}x + {coeffs[1]:.1f}'
# #                     plt.text(x_fit[-1]+0.3, y_fit[-1], eqn_str, fontsize=12, color=color, va='center')
# #                 else:
# #                     print("   ⚠ Not enough data points to compute slope or fit.")
# #
# #                 plt.plot(x, y, marker='o', linestyle='-', color=color, label=f'{pulse_height}V pulse')
# #
# #             plt.title(f'{ch} — Peak Index vs. Peak Number (Gain = {gain} V)')
# #             plt.xlabel('Peak Number')
# #             plt.ylabel('Peak Index')
# #             plt.grid(True)
# #             plt.legend(title='Pulse Height')
# #             plt.tight_layout()
# #             plt.show()
# #
# # print(f"\n✅ Slope results written to: {csv_filename}")
# #
