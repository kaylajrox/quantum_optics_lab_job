import matplotlib
from holoviews.plotting.bokeh.styles import font_size

matplotlib.use('TkAgg')  # For PyCharm interactivity

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# TODO check if all variables from each script are supposed to be the same
font_size= 24


# Define the path to the CSV file
script_dir = Path(__file__).resolve().parent
file_path = script_dir / 'processed_peak_data.csv'

# Load CSV
data = pd.read_csv(file_path)

# Convert correlation time (e.g., "100ns") to integer
data['Correlation Time (ns)'] = data['Correlation Time'].str.replace('ns', '', regex=False).astype(int)

# Separate by state
filtered_data = data[data['State'] == 'filtered']
unfiltered_data = data[data['State'] == 'unfiltered']

# Plot function
def plot_total_counts(df, title):
    plt.figure(figsize=(10, 6))
    for coincidence, group in df.groupby('Coincidence'):
        group = group.sort_values('Correlation Time (ns)')
        plt.plot(group['Correlation Time (ns)'], group['Total Counts'], marker='o', label=coincidence, linewidth=2)

    plt.xlabel('Correlation Time (ns)',fontsize=font_size)
    plt.ylabel('Total Counts',fontsize=font_size)
    plt.tick_params(axis='x', labelsize=font_size)
    plt.tick_params(axis='y', labelsize=font_size)
    plt.title(title,fontsize=font_size)
    plt.legend(title='Coincidence')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# Plot separately
plot_total_counts(filtered_data, "Total Counts vs Correlation Time (Filtered)")
plot_total_counts(unfiltered_data, "Total Counts vs Correlation Time (Unfiltered)")

#
#
# #todo which peak plot? coicidence ones is all I have
#