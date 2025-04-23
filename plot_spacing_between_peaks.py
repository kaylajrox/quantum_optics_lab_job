import matplotlib
matplotlib.use('TkAgg')  # For PyCharm interactivity

import pandas as pd
import matplotlib.pyplot as plt

# Independent crop values
crop_off_by_pulse = {
    1.3: 0,  # Crop 2 from 1.3V
    1.6: 2   # Crop 1 from 1.6V
}

# Load data
df = pd.read_csv('combined_peak_data.csv')
df['Index Difference'] = pd.to_numeric(df['Index Difference'], errors='coerce')
df = df[df['Channel (from filename)'] == 'CH1']

gain_voltages = sorted(df['Gain Voltage (from filename)'].unique())

# Plot per gain voltage
for gain_v in gain_voltages:
    plt.figure(figsize=(8, 6))

    for pulse_height, color in zip([1.3, 1.6], ['green', 'orange']):
        subset = df[
            (df['Gain Voltage (from filename)'] == gain_v) &
            (df['Pulse Height (from filename)'] == pulse_height)
        ].copy()

        subset = subset.dropna(subset=['Index Difference'])

        crop_off = crop_off_by_pulse.get(pulse_height, 0)
        if crop_off > 0 and len(subset) > crop_off:
            subset = subset.iloc[:-crop_off]

        plt.plot(
            subset['Peak Number'],
            subset['Index Difference'],
            marker='o',
            linestyle='-',
            label=f'{pulse_height}V Pulse',
            color=color
        )

    plt.title(f'CH1 — Peak Spacing vs. Peak Number (Gain = {gain_v} V)')
    plt.xlabel('Peak Number')
    plt.ylabel('Index Difference (Spacing)')
    plt.grid(True)
    plt.legend(title='Pulse Height')
    plt.tight_layout()
    plt.show()





# import matplotlib
# matplotlib.use('TkAgg')  # For PyCharm interactivity
#
#
# import pandas as pd
# import matplotlib.pyplot as plt
#
# # Load combined peak data
# df = pd.read_csv('combined_peak_data.csv')
#
# # Convert spacing values to numeric (ignore "N/A" for first peak)
# df['Index Difference'] = pd.to_numeric(df['Index Difference'], errors='coerce')
#
# # Filter for CH1 only
# df = df[df['Channel (from filename)'] == 'CH1']
#
# # Get sorted list of unique gain voltages for CH1
# gain_voltages = sorted(df['Gain Voltage (from filename)'].unique())
#
# # Plot one figure per gain voltage
# for gain_v in gain_voltages:
#     plt.figure(figsize=(8, 6))
#
#     for pulse_height, color in zip([1.3, 1.6], ['green', 'orange']):
#         # Filter for current gain and pulse height
#         subset = df[
#             (df['Gain Voltage (from filename)'] == gain_v) &
#             (df['Pulse Height (from filename)'] == pulse_height)
#         ].copy()
#
#         # Drop the first peak since its spacing is NaN
#         subset = subset.dropna(subset=['Index Difference'])
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
#
#
#     plt.title(f'CH1 — Peak Spacing vs. Peak Number (Gain = {gain_v} V)')
#     plt.xlabel('Peak Number')
#     plt.ylabel('Index Difference (Spacing)')
#     plt.grid(True)
#     plt.legend(title='Pulse Height')
#     plt.tight_layout()
#     plt.show()
