import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict
from scipy.signal import find_peaks
import math

# Set the root directory
root_dir = '../photon_counts_data/20250403'
crop_off = 3700
vertical_lines = False

# Dictionaries to hold photon_counts_data grouped by duration and channel
ch0_by_duration = defaultdict(list)
ch1_by_duration = defaultdict(list)

# Regex to extract duration from folder names (e.g., '20s' from '1_2V_20s')
duration_pattern = re.compile(r'(\d+)s$')

# Function to extract voltage from filename like "65_5_gain"
def extract_voltage_and_title(file_name):
    match = re.match(r"(\d+)_?(\d+)_gain", file_name)
    if match:
        return f"{float(f'{match.group(1)}.{match.group(2)}')}V"
    return file_name  # fallback

# Function to find peaks and return distances between them
def find_and_label_peaks(data, crop_off):
    data_cropped = data[:-crop_off]
    x = np.arange(len(data_cropped))
    peaks, _ = find_peaks(data_cropped, height=0.5, distance=15)
    distances = [x[peaks[i]] - x[peaks[i - 1]] for i in range(1, len(peaks))]
    return distances

# Walk through directory to organize files by duration
for subdir, _, files in os.walk(root_dir):
    match = duration_pattern.search(os.path.basename(subdir))
    if match:
        duration_key = match.group(0)  # e.g. "20s"
        for file in sorted(files):
            file_path = os.path.join(subdir, file)
            try:
                if file.startswith("CH0") or file.startswith("CH1"):
                    data = np.loadtxt(file_path, delimiter=',')
                    label = os.path.relpath(file_path, root_dir)
                    if file.startswith("CH0"):
                        ch0_by_duration[duration_key].append((data, label))
                    else:
                        ch1_by_duration[duration_key].append((data, label))
            except Exception as e:
                print(f"Error loading {file_path}: {e}")

# Function to process a data_dict (CH0 or CH1) and save per-duration CSVs
def generate_distance_tables_by_duration(data_dict, prefix):
    for duration, data_list in sorted(data_dict.items()):
        table_dict = {}
        max_len = 0

        for data, label in data_list:
            voltage = extract_voltage_and_title(label)
            distances = find_and_label_peaks(data, crop_off)
            table_dict[voltage] = distances
            max_len = max(max_len, len(distances))

        # Pad shorter lists with NaN
        for voltage in table_dict:
            padding = [np.nan] * (max_len - len(table_dict[voltage]))
            table_dict[voltage] += padding

        # Create and save the DataFrame
        df = pd.DataFrame(table_dict)
        df.index += 1  # Label rows starting from 1 (distance #1, #2, ...)
        df.index.name = "distance between subsequent peaks"
        csv_filename = f"{prefix}_distances_{duration}.csv"
        df.to_csv(csv_filename)
        print(f"Saved {csv_filename}")

# Generate CSVs for CH0 and CH1
generate_distance_tables_by_duration(ch0_by_duration, "CH0")
generate_distance_tables_by_duration(ch1_by_duration, "CH1")




# import matplotlib
# matplotlib.use('TkAgg')  # For PyCharm interactivity
#
# import os
# import re
# import numpy as np
# import matplotlib.pyplot as plt
# import math
# from collections import defaultdict
# from scipy.signal import find_peaks
#
# # Set the root directory
# # root_dir = 'photon_counts_data/20250402_pulse_height_vary'
# root_dir = 'photon_counts_data/20250403'
# crop_off = 3700
# vertical_lines = False
#
# # Dictionaries to hold photon_counts_data grouped by duration (like '20s', '60s') and channel
# ch0_by_duration = defaultdict(list)
# ch1_by_duration = defaultdict(list)
#
# # Regex to extract duration from folder names (e.g., '20s' from '1_2V_20s')
# duration_pattern = re.compile(r'(\d+)s$')
#
#
# # Function to extract voltage and format the title
# def extract_voltage_and_title(file_name):
#     match = re.match(r"(\d+)_?(\d+)_gain", file_name)
#     if match:
#         voltage = float(f"{match.group(1)}.{match.group(2)}")  # Create voltage like 65.5V
#         return f"{voltage}V gain"
#     return file_name  # Default to the filename if not matching the pattern
#
#
# def find_and_label_peaks(photon_counts_data, ax, label, crop_off, vertical_lines=vertical_lines):
#     # Apply cropping
#     data_cropped = photon_counts_data[:-crop_off]
#     x = np.arange(len(data_cropped))
#
#     # Find peaks
#     peaks, properties = find_peaks(data_cropped, height=0.5, distance=15)  # Adjust height and distance as needed
#
#     # Plot the photon_counts_data and peaks
#     ax.plot(x, data_cropped, label=label, alpha=0.7)
#     ax.scatter(x[peaks], data_cropped[peaks], color='red', label='Peaks')
#
#     # Add a dashed vertical line at each peak
#     if vertical_lines == True:
#         for peak in peaks:
#             ax.axvline(x=peak, color='red', linestyle='--', linewidth=1)  # Dashed red vertical line
#
#     # Label each peak
#     for i, idx in enumerate(peaks):
#         ax.text(x[idx], data_cropped[idx] + 100, f'{i + 1}', ha='center', va='bottom', fontsize=9, color='red')
#
#     ax.set_xlabel("Index")
#     ax.set_ylabel("Value")
#     ax.grid(True)
#
#     # Calculate and print the horizontal distance between consecutive peaks
#     distance = []
#     for i in range(1, len(peaks)):
#         distance.append(x[peaks[i]] - x[peaks[i - 1]])  # Properly append distances
#
#     return distance, peaks, data_cropped  # Return the peaks and cropped photon_counts_data for optional printing
#
# # Walk through the directory tree
# for subdir, _, files in os.walk(root_dir):
#     match = duration_pattern.search(os.path.basename(subdir))
#     if match:
#         duration_key = match.group(0)  # e.g. "20s", "60s"
#         for file in sorted(files):
#             file_path = os.path.join(subdir, file)
#             try:
#                 if file.startswith("CH0"):
#                     photon_counts_data = np.loadtxt(file_path, delimiter=',')
#                     label = os.path.relpath(file_path, root_dir)
#                     ch0_by_duration[duration_key].append((photon_counts_data, label))
#                 elif file.startswith("CH1"):
#                     photon_counts_data = np.loadtxt(file_path, delimiter=',')
#                     label = os.path.relpath(file_path, root_dir)
#                     ch1_by_duration[duration_key].append((photon_counts_data, label))
#             except Exception as e:
#                 print(f"Error loading {file_path}: {e}")
#
#
# def plot_grouped_subplots(data_dict, title_prefix, n_cols=3):
#     for duration, data_list in sorted(data_dict.items()):
#         n_plots = len(data_list)
#         n_rows = math.ceil(n_plots / n_cols)
#
#         fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 4 * n_rows))
#         axes = axes.flatten()
#
#         for idx, (photon_counts_data, label) in enumerate(data_list):
#             ax = axes[idx]
#             # Extract voltage-based title from the label
#             title = extract_voltage_and_title(label)
#
#             # Find peaks and label them on the plot
#             distance, peaks, cropped_data = find_and_label_peaks(photon_counts_data, ax, title, crop_off)
#
#             # Print distances with the title of the subplot (which includes the voltage)
#             for i in range(1, len(peaks)):
#                 print(f"Gain {title} - Duration {duration} - Distance between Peak {i} and Peak {i + 1}: {distance[i - 1]} units")
#
#             # Set the title for the plot
#             ax.set_title(title, fontsize=8)
#
#         # Remove empty subplots if they exist
#         for j in range(idx + 1, len(axes)):
#             fig.delaxes(axes[j])
#
#         fig.suptitle(f"{title_prefix} - Duration: {duration}", fontsize=16)
#         plt.tight_layout(rect=[0, 0, 1, 0.96])
#         plt.show()
#
#
# # Plot CH0 and CH1 grouped by duration
# plot_grouped_subplots(ch0_by_duration, "CH0 Files")
# plot_grouped_subplots(ch1_by_duration, "CH1 Files")
#
#
