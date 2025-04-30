import matplotlib
matplotlib.use('TkAgg')  # For PyCharm interactivity

import pandas as pd
import matplotlib.pyplot as plt
from combine_data_from_separate_directories_into_single_database import *

# crop off
crop_off = 0

# Load the summary CSV
summary_df = pd.read_csv('results_first_peaks_summary_old.csv')

# Optional: sort to keep everything organized
summary_df = summary_df.sort_values(
    by=['Channel (from filename)', 'Pulse Height (from filename)', 'Gain Voltage (from filename)']
)

# Define color mapping for pulse heights
pulse_color_map = {
    1.3: 'green',
    1.6: 'orange'
}

# Separate plots for each channel
for channel in ['CH0', 'CH1']:
    plt.figure(figsize=(8, 6))

    for pulse_height in [1.3, 1.6]:
        # Filter the relevant data
        filtered = summary_df[
            (summary_df['Channel (from filename)'] == channel) &
            (summary_df['Pulse Height (from filename)'] == pulse_height)
        ]
        if crop_off > 0:
            filtered = filtered.iloc[:-crop_off]

        plt.plot(
            filtered['Gain Voltage (from filename)'],
            filtered['Peak Index'],
            marker='o',
            linestyle='-',
            label=f'{pulse_height}V Pulse',
            color=pulse_color_map[pulse_height]
        )


    plt.title(f'First Peak Index vs. Gain Voltage ({channel})')
    plt.xlabel('Gain Voltage (V)')
    plt.ylabel('Peak 1 Index')
    plt.grid(True, which='major', linestyle='-', linewidth=0.5)
    plt.legend(title='Pulse Height')
    plt.tight_layout()
    plt.show()
