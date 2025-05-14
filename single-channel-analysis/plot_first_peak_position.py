import matplotlib
matplotlib.use('TkAgg')  # For PyCharm interactivity

from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

# Crop-off setting
crop_off = 0

# ✅ Your custom pulse color map
pulse_color_map = {
    1.0: 'black',
    1.1: 'darkblue',
    1.3: 'green',
    1.6: 'orange',
    2.0: 'deeppink',
    2.3: 'red',
}

# Load the summary CSV
summary_df = pd.read_csv('../results_first_peaks_summary.csv')

# Sort for consistent plotting
summary_df = summary_df.sort_values(
    by=['Channel (from filename)', 'Pulse Height (from filename)', 'Gain Voltage (from filename)']
)

# Add timestamp
current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
summary_df['Timestamp'] = current_time

# ✅ Reorder columns to place Timestamp first
cols = ['Timestamp'] + [col for col in summary_df.columns if col != 'Timestamp']
summary_df = summary_df[cols]

# ✅ Save updated table
summary_df.to_csv('results_first_peaks_summary.csv', index=False)
print("✅ Saved updated summary with timestamp as first column.")

# Detect all pulse heights
all_pulses = sorted(summary_df['Pulse Height (from filename)'].unique())

# Plot for each channel
for channel in summary_df['Channel (from filename)'].unique():
    plt.figure(figsize=(8, 6))

    for pulse in all_pulses:
        filtered = summary_df[
            (summary_df['Channel (from filename)'] == channel) &
            (summary_df['Pulse Height (from filename)'] == pulse)
        ]

        if crop_off > 0:
            filtered = filtered.iloc[:-crop_off]

        if not filtered.empty:
            color = pulse_color_map.get(pulse, 'gray')  # fallback to gray if not in map
            plt.plot(
                filtered['Gain Voltage (from filename)'],
                filtered['Peak Index'],
                marker='o',
                linestyle='-',
                label=f'{pulse}V Pulse',
                color=color
            )

    plt.title(f'First Peak Index vs. Gain Voltage ({channel})')
    plt.xlabel('Gain Voltage (V)')
    plt.ylabel('Peak 1 Index')
    plt.grid(True)
    plt.legend(title='Pulse Height')
    plt.tight_layout()
    plt.show()
