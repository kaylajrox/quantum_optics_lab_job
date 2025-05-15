import matplotlib
matplotlib.use('TkAgg')  # For PyCharm interactivity

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# Define the path to the CSV file
script_dir = Path(__file__).resolve().parent
file_path = script_dir / 'peak_summary_weighted_means_counts.csv'

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
        plt.plot(group['Correlation Time (ns)'], group['Total Counts'], marker='o', label=coincidence)

    plt.xlabel('Correlation Time (ns)')
    plt.ylabel('Total Counts')
    plt.title(title)
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
# import matplotlib
# matplotlib.use('TkAgg')  # For PyCharm interactivity
#
# from pathlib import Path
# import pandas as pd
# import matplotlib.pyplot as plt
#
# # Define the path to the CSV file
# script_dir = Path(__file__).resolve().parent  # Directory of the current script
# file_path = script_dir  / 'peak_summary_weighted_means_counts.csv'
#
# # Load the peak summary CSV file
# data = pd.read_csv(file_path)
#
# # Convert correlation_time to numeric for sorting (e.g., remove 'ns' and convert to int)
# data['Correlation Time'] = data['Correlation Time'].str.replace('ns', '').astype(int)
#
#
# print(data['Correlation Time'])
# # Separate filtered and unfiltered data
# filtered_data = data[data['State'] == 'filtered']
# unfiltered_data = data[data['State'] == 'unfiltered']
#
# # Function to plot data
# def plot_peak_indices(data, title):
#     plt.figure(figsize=(10, 6))
#     for coincidence, group in data.groupby('Correlation Time'):
#         # Sort by correlation time for proper plotting
#         group = group.sort_values('Correlation Time')
#         plt.plot(group['Correlation Time'], group['Total Counts'], marker='o', label=coincidence)
#
#     plt.xlabel('Correlation Time (ns)')
#     plt.ylabel('Peak Index')
#     plt.title(title)
#     plt.legend(title='Coincidence')
#     plt.grid(True)
#     plt.show()
#
# # Plot for filtered data
# plot_peak_indices(filtered_data, 'Peak Index vs Correlation Time (Filtered)')
#
# # Plot for unfiltered data
# plot_peak_indices(unfiltered_data, 'Peak Index vs Correlation Time (Unfiltered)')
#
