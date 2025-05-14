import matplotlib
matplotlib.use('TkAgg')  # For PyCharm interactivity

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# Define the path to the CSV file
script_dir = Path(__file__).resolve().parent  # Directory of the current script
file_path = script_dir  / 'peak_summary.csv'

# Load the peak summary CSV file
data = pd.read_csv(file_path)

# Convert correlation_time to numeric for sorting (e.g., remove 'ns' and convert to int)
data['correlation_time_ns'] = data['correlation_time'].str.replace('ns', '').astype(int)

# Separate filtered and unfiltered data
filtered_data = data[data['state'] == 'filtered']
unfiltered_data = data[data['state'] == 'unfiltered']

# Function to plot data
def plot_peak_indices(data, title):
    plt.figure(figsize=(10, 6))
    for coincidence, group in data.groupby('coincidence'):
        # Sort by correlation time for proper plotting
        group = group.sort_values('correlation_time_ns')
        plt.plot(group['correlation_time_ns'], group['peak_index'], marker='o', label=coincidence)

    plt.xlabel('Correlation Time (ns)')
    plt.ylabel('Peak Index')
    plt.title(title)
    plt.legend(title='Coincidence')
    plt.grid(True)
    plt.show()

# Plot for filtered data
plot_peak_indices(filtered_data, 'Peak Index vs Correlation Time (Filtered)')

# Plot for unfiltered data
plot_peak_indices(unfiltered_data, 'Peak Index vs Correlation Time (Unfiltered)')


# import pandas as pd
# import matplotlib.pyplot as plt
#
# # Load the peak summary CSV file
# file_path = 'coincidence-analysis/peak_summary.csv'
# data = pd.read_csv(file_path)
#
# # Convert correlation_time to numeric for sorting (e.g., remove 'ns' and convert to int)
# data['correlation_time_ns'] = data['correlation_time'].str.replace('ns', '').astype(int)
#
# # Separate filtered and unfiltered data
# filtered_data = data[data['state'] == 'filtered']
# unfiltered_data = data[data['state'] == 'unfiltered']
#
#
# # Function to plot data
# def plot_peak_indices(data, title):
#     plt.figure(figsize=(10, 6))
#     for coincidence, group in data.groupby('coincidence'):
#         # Sort by correlation time for proper plotting
#         group = group.sort_values('correlation_time_ns')
#         plt.plot(group['correlation_time_ns'], group['peak_index'], marker='o', label=coincidence)
#
#     plt.xlabel('Correlation Time (ns)')
#     plt.ylabel('Peak Index')
#     plt.title(title)
#     plt.legend(title='Coincidence')
#     plt.grid(True)
#     plt.show()
#
#
# # Plot for filtered data
# plot_peak_indices(filtered_data, 'Peak Index vs Correlation Time (Filtered)')
#
# # Plot for unfiltered data
# plot_peak_indices(unfiltered_data, 'Peak Index vs Correlation Time (Unfiltered)')