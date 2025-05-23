import matplotlib
from holoviews.plotting.bokeh.styles import font_size

matplotlib.use('TkAgg')  # For PyCharm interactivity

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# TODO check if all variables from each script are supposed to be the same
font_size= 24


# Define the path to the CSV file
script_dir = Path(__file__).resolve().parent.parent
file_path = script_dir / 'processed_peak_data.csv'

# Load CSV
data = pd.read_csv(file_path)

# Convert correlation time (e.g., "100ns") to integer
data['correlation_time'] = data['correlation_time'].str.replace('ns', '', regex=False).astype(int)

# Separate by state
filtered_data = data[data['state'] == 'filtered']
unfiltered_data = data[data['state'] == 'unfiltered']

# Plot function
def plot_total_counts(df, title):
    plt.figure(figsize=(10, 6))
    for coincidence, group in df.groupby('coincidence'):
        group = group.sort_values('correlation_time')
        plt.plot(group['correlation_time'], group['total_counts'], marker='o', label=coincidence, linewidth=2)

    plt.xlabel('Correlation Time (ns)',fontsize=font_size)
    plt.ylabel('total_counts',fontsize=font_size)
    plt.tick_params(axis='x', labelsize=font_size)
    plt.tick_params(axis='y', labelsize=font_size)
    plt.title(title,fontsize=font_size)
    plt.legend(title='coincidence')
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