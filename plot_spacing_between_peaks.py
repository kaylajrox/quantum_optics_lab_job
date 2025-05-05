import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')  # Optional: for interactivity in some IDEs

# Load the combined peak data
df = pd.read_csv('results_combined_peak_data.csv')
df.columns = df.columns.str.strip()

# Convert necessary columns to numeric
df['Peak Number'] = pd.to_numeric(df['Peak Number'], errors='coerce')
df['Peak Index'] = pd.to_numeric(df['Peak Index'], errors='coerce')
df = df.dropna(subset=['Peak Number', 'Peak Index'])

# Prepare output storage
results = []

# Group by channel and gain voltage
for ch in df['Channel (from filename)'].unique():
    df_ch = df[df['Channel (from filename)'] == ch]
    for gain in sorted(df_ch['Gain Voltage (from filename)'].unique()):
        df_gain = df_ch[df_ch['Gain Voltage (from filename)'] == gain]

        # Store slopes from all pulse heights at this gain voltage
        all_slopes = []

        for pulse_height in sorted(df_gain['Pulse Height (from filename)'].unique()):
            df_pulse = df_gain[df_gain['Pulse Height (from filename)'] == pulse_height]
            df_pulse = df_pulse.sort_values('Peak Number')

            x = df_pulse['Peak Number'].values
            y = df_pulse['Peak Index'].values

            if len(x) >= 2:
                slopes = np.diff(y) / np.diff(x)
                all_slopes.extend(slopes)

        if len(all_slopes) > 0:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            avg_slope = np.mean(all_slopes)
            std_slope = np.std(all_slopes)
            results.append({
                'Current time of data made': timestamp,
                'Channel': ch,
                'Gain Voltage (V)': gain,
                'Average Spacing': avg_slope,
                'Standard Deviation': std_slope
            })

# Save results to CSV
results_df = pd.DataFrame(results)
results_df.to_csv('results_spacing_from_slope.csv', index=False)
print("✅ Slope results saved to 'results_spacing_from_slope.csv'.")

# --- Plotting ---
for ch in results_df['Channel'].unique():
    df_ch = results_df[results_df['Channel'] == ch]
    x = df_ch['Gain Voltage (V)'].values
    y = df_ch['Average Spacing'].values
    yerr = df_ch['Standard Deviation'].values

    plt.figure(figsize=(8, 6))
    plt.errorbar(x, y, yerr=yerr, fmt='o-', capsize=4, label=f'{ch} (mean ± std)', color='black')

    # Linear fit
    coeffs = np.polyfit(x, y, deg=1)
    x_fit = np.linspace(min(x), max(x), 300)
    y_fit = np.polyval(coeffs, x_fit)
    plt.plot(x_fit, y_fit, 'r--', label=f'Linear Fit: y = {coeffs[0]:.3f}x + {coeffs[1]:.2f}')
    plt.text(x_fit[-1], y_fit[-1], f'y = {coeffs[0]:.3f}x + {coeffs[1]:.2f}',
             fontsize=12, color='red', ha='right', va='bottom')

    # Labels and layout
    plt.title(f'{ch} — Average Spacing vs. Gain Voltage')
    plt.xlabel('Gain Voltage (V)')
    plt.ylabel('Average Spacing (Slope)')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


# import pandas as pd
# import numpy as np
# from datetime import datetime
# import matplotlib.pyplot as plt
# import matplotlib
# matplotlib.use('TkAgg')  # Optional: for interactivity in some IDEs
#
# # Load the combined peak data
# df = pd.read_csv('results_combined_peak_data.csv')
# df.columns = df.columns.str.strip()
#
# # Convert necessary columns to numeric
# df['Peak Number'] = pd.to_numeric(df['Peak Number'], errors='coerce')
# df['Peak Index'] = pd.to_numeric(df['Peak Index'], errors='coerce')
# df = df.dropna(subset=['Peak Number', 'Peak Index'])
#
# # Prepare output storage
# results = []
#
# # Group by channel and gain voltage
# for ch in df['Channel (from filename)'].unique():
#     df_ch = df[df['Channel (from filename)'] == ch]
#     for gain in sorted(df_ch['Gain Voltage (from filename)'].unique()):
#         df_gain = df_ch[df_ch['Gain Voltage (from filename)'] == gain]
#
#         # Store slopes from all pulse heights at this gain voltage
#         all_slopes = []
#
#         for pulse_height in sorted(df_gain['Pulse Height (from filename)'].unique()):
#             df_pulse = df_gain[df_gain['Pulse Height (from filename)'] == pulse_height]
#             df_pulse = df_pulse.sort_values('Peak Number')
#
#             x = df_pulse['Peak Number'].values
#             y = df_pulse['Peak Index'].values
#
#             if len(x) >= 2:
#                 slopes = np.diff(y) / np.diff(x)
#                 all_slopes.extend(slopes)
#
#         if len(all_slopes) > 0:
#             timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#             avg_slope = np.mean(all_slopes)
#             std_slope = np.std(all_slopes)
#             results.append({
#                 'Current time of data made': timestamp,
#                 'Channel': ch,
#                 'Gain Voltage (V)': gain,
#                 'Average Spacing': avg_slope,
#                 'Standard Deviation': std_slope
#             })
#
# # Save results to CSV
# results_df = pd.DataFrame(results)
# results_df.to_csv('results_spacing_from_slope.csv', index=False)
# print("✅ Slope results saved to 'results_spacing_from_slope.csv'.")
#
# # --- Plotting ---
# for ch in results_df['Channel'].unique():
#     df_ch = results_df[results_df['Channel'] == ch]
#
#     plt.figure(figsize=(8, 6))
#     plt.errorbar(
#         df_ch['Gain Voltage (V)'],
#         df_ch['Average Spacing'],
#         yerr=df_ch['Standard Deviation'],
#         fmt='o-',
#         capsize=4,
#         label=f'{ch} (mean ± std)', color = 'black',
#     )
#
#     plt.title(f'{ch} — Average Spacing vs. Gain Voltage')
#     plt.xlabel('Gain Voltage (V)')
#     plt.ylabel('Average Spacing (Slope)')
#     plt.grid(True)
#     plt.legend()
#     plt.tight_layout()
#     plt.show()
