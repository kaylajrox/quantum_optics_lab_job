import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict
from scipy.signal import find_peaks
import math

# Set the root directory
root_dir = 'photon_counts_data/20250403'
crop_off = 3700
vertical_lines = False

# Dictionaries to hold photon_counts_data grouped by duration and channel
ch0_by_duration = defaultdict(list)
ch1_by_duration = defaultdict(list)

# Regex to extract duration from folder names (e.g., '20s' from '1_2V_20s')
duration_pattern = re.compile(r'(\d+)s$')


# Function to extract voltage and format the title
def extract_voltage_and_title(file_name):
    match = re.match(r"(\d+)_?(\d+)_gain", file_name)
    if match:
        voltage = float(f"{match.group(1)}.{match.group(2)}")  # Create voltage like 65.5V
        return f"{voltage}V gain"
    return file_name  # Default to the filename if not matching the pattern


def find_and_label_peaks(data, ax, label, crop_off, vertical_lines=vertical_lines):
    # Apply cropping
    data_cropped = data[:-crop_off]
    x = np.arange(len(data_cropped))

    # Find peaks
    peaks, _ = find_peaks(data_cropped, height=0.5, distance=15)

    # Plot the photon_counts_data and peaks
    ax.plot(x, data_cropped, label=label, alpha=0.7)
    ax.scatter(x[peaks], data_cropped[peaks], color='red', label='Peaks')

    # Add vertical lines if enabled
    if vertical_lines:
        for peak in peaks:
            ax.axvline(x=peak, color='red', linestyle='--', linewidth=1)

    # Label each peak
    for i, idx in enumerate(peaks):
        ax.text(x[idx], data_cropped[idx] + 100, f'{i + 1}', ha='center', va='bottom', fontsize=9, color='red')

    ax.set_xlabel("Index")
    ax.set_ylabel("Value")
    ax.grid(True)

    # Calculate and return the horizontal distance between consecutive peaks
    distance = []
    for i in range(1, len(peaks)):
        distance.append(x[peaks[i]] - x[peaks[i - 1]])

    return distance, peaks, data_cropped


# Walk through the directory tree
for subdir, _, files in os.walk(root_dir):
    match = duration_pattern.search(os.path.basename(subdir))
    if match:
        duration_key = match.group(0)
        for file in sorted(files):
            file_path = os.path.join(subdir, file)
            try:
                if file.startswith("CH0"):
                    data = np.loadtxt(file_path, delimiter=',')
                    label = os.path.relpath(file_path, root_dir)
                    ch0_by_duration[duration_key].append((data, label))
                elif file.startswith("CH1"):
                    data = np.loadtxt(file_path, delimiter=',')
                    label = os.path.relpath(file_path, root_dir)
                    ch1_by_duration[duration_key].append((data, label))
            except Exception as e:
                print(f"Error loading {file_path}: {e}")


def plot_grouped_subplots(data_dict, title_prefix, n_cols=3):
    distance_dict = defaultdict(list)

    for duration, data_list in sorted(data_dict.items()):
        n_plots = len(data_list)
        n_rows = math.ceil(n_plots / n_cols)

        fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 4 * n_rows))
        axes = axes.flatten()

        for idx, (data, label) in enumerate(data_list):
            ax = axes[idx]
            title = extract_voltage_and_title(label)
            distance, peaks, cropped_data = find_and_label_peaks(data, ax, title, crop_off)
            distance_dict[title].append(distance)
            print(distance)
            ax.set_title(title, fontsize=8)

        for j in range(idx + 1, len(axes)):
            fig.delaxes(axes[j])

        fig.suptitle(f"{title_prefix} - Duration: {duration}", fontsize=16)
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.show()

    return distance_dict


# Get the distance photon_counts_data for CH0 and CH1 grouped by duration
ch0_distances = plot_grouped_subplots(ch0_by_duration, "CH0 Files")
ch1_distances = plot_grouped_subplots(ch1_by_duration, "CH1 Files")

# Combine distances from both CH0 and CH1 into a single dictionary
all_distances = {**ch0_distances, **ch1_distances}

# Flatten and normalize distance arrays for table
voltage_columns = {}
flattened_distances = {}
max_len = 0

for voltage, list_of_lists in all_distances.items():
    flat = [item for sublist in list_of_lists for item in sublist]
    flattened_distances[voltage] = flat
    max_len = max(max_len, len(flat))

for voltage, flat in flattened_distances.items():
    padded = flat + [np.nan] * (max_len - len(flat))
    voltage_columns[voltage] = padded

# Create DataFrame
df_distances = pd.DataFrame(voltage_columns)

# Add label column if it doesn't already exist
if "distance between subsequent peaks" in df_distances.columns:
    df_distances.drop(columns=["distance between subsequent peaks"], inplace=True)

df_distances.insert(0, "distance between subsequent peaks", range(1, len(df_distances) + 1))

# Save the DataFrame as CSV
df_distances.to_csv("distance_table.csv", index=False)
print("Table saved as 'distance_table.csv'")




# import os
# import re
# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
# from collections import defaultdict
# from scipy.signal import find_peaks
# import math
#
# # Set the root directory
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
#     # Calculate and return the horizontal distance between consecutive peaks
#     distance = []
#     for i in range(1, len(peaks)):
#         distance.append(x[peaks[i]] - x[peaks[i - 1]])
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
#     distance_dict = defaultdict(list)  # To store distances by voltage
#
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
#             # Store distances in the dictionary under the appropriate voltage title
#             distance_dict[title].append(distance)
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
#     return distance_dict  # Return the dictionary of distances
#
#
# # Get the distance photon_counts_data for CH0 and CH1 grouped by duration
# ch0_distances = plot_grouped_subplots(ch0_by_duration, "CH0 Files")
# ch1_distances = plot_grouped_subplots(ch1_by_duration, "CH1 Files")
#
# # Combine distances from both CH0 and CH1 into a single dictionary
# all_distances = {**ch0_distances, **ch1_distances}
#
# # Flatten and transpose the list of distances per voltage
# voltage_columns = {}
#
# # First flatten each list of lists and find the maximum length
# flattened_distances = {}
# max_len = 0
#
# for voltage, list_of_lists in all_distances.items():
#     flat = [item for sublist in list_of_lists for item in sublist]
#     flattened_distances[voltage] = flat
#     max_len = max(max_len, len(flat))
#
# # Pad each list with NaN so they all have the same length
# for voltage, flat in flattened_distances.items():
#     padded = flat + [np.nan] * (max_len - len(flat))
#     voltage_columns[voltage] = padded
#
# # Create the DataFrame from padded columns
# df_distances = pd.DataFrame(voltage_columns)
#
# # Remove the label column first if it already exists
# if "distance between subsequent peaks" in df_distances.columns:
#     df_distances.drop(columns=["distance between subsequent peaks"], inplace=True)
#
# # Now insert it
# df_distances.insert(0, "distance between subsequent peaks", range(1, len(df_distances) + 1))
#
# # Create a graphical table using matplotlib
# fig, ax = plt.subplots(figsize=(10, 6))
#
# # Hide axes
# ax.axis('off')
#
# # Create the table
# table = ax.table(cellText=df_distances.values,
#                 colLabels=df_distances.columns,
#                 loc='center',
#                 cellLoc='center',
#                 colColours=['#f1f1f1']*len(df_distances.columns),  # Add background color to headers
#                 rowColours=['#f1f1f1']*(df_distances.shape[0]),  # Background color for rows
#                 colWidths=[0.2]*df_distances.shape[1])  # Column widths
#
# # Style the table: Change font size and adjust other aesthetics
# table.auto_set_font_size(False)
# table.set_fontsize(10)
# table.scale(1.2, 1.2)  # Scale the table size
#
# # Save the table as an image
# plt.tight_layout()
# plt.savefig("distance_table.png", dpi=300)  # Save as PNG file
# plt.show()
#
# print("Table saved as 'distance_table.png'")
#
#
#
# # import matplotlib
# # matplotlib.use('TkAgg')  # For PyCharm interactivity
# #
# # import os
# # import re
# # import numpy as np
# # import matplotlib.pyplot as plt
# # import math
# # import pandas as pd
# # from collections import defaultdict
# # from scipy.signal import find_peaks
# #
# # # Set the root directory
# # root_dir = 'photon_counts_data/20250403'
# # crop_off = 3700
# # vertical_lines = False
# #
# # # Dictionaries to hold photon_counts_data grouped by duration (like '20s', '60s') and channel
# # ch0_by_duration = defaultdict(list)
# # ch1_by_duration = defaultdict(list)
# #
# # # Regex to extract duration from folder names (e.g., '20s' from '1_2V_20s')
# # duration_pattern = re.compile(r'(\d+)s$')
# #
# #
# # # Function to extract voltage and format the title
# # def extract_voltage_and_title(file_name):
# #     match = re.match(r"(\d+)_?(\d+)_gain", file_name)
# #     if match:
# #         voltage = float(f"{match.group(1)}.{match.group(2)}")  # Create voltage like 65.5V
# #         return f"{voltage}V gain"
# #     return file_name  # Default to the filename if not matching the pattern
# #
# #
# # def find_and_label_peaks(photon_counts_data, ax, label, crop_off, vertical_lines=vertical_lines):
# #     # Apply cropping
# #     data_cropped = photon_counts_data[:-crop_off]
# #     x = np.arange(len(data_cropped))
# #
# #     # Find peaks
# #     peaks, properties = find_peaks(data_cropped, height=0.5, distance=15)  # Adjust height and distance as needed
# #
# #     # Plot the photon_counts_data and peaks
# #     ax.plot(x, data_cropped, label=label, alpha=0.7)
# #     ax.scatter(x[peaks], data_cropped[peaks], color='red', label='Peaks')
# #
# #     # Add a dashed vertical line at each peak
# #     if vertical_lines == True:
# #         for peak in peaks:
# #             ax.axvline(x=peak, color='red', linestyle='--', linewidth=1)  # Dashed red vertical line
# #
# #     # Label each peak
# #     for i, idx in enumerate(peaks):
# #         ax.text(x[idx], data_cropped[idx] + 100, f'{i + 1}', ha='center', va='bottom', fontsize=9, color='red')
# #
# #     ax.set_xlabel("Index")
# #     ax.set_ylabel("Value")
# #     ax.grid(True)
# #
# #     # Calculate and return the horizontal distance between consecutive peaks
# #     distance = []
# #     for i in range(1, len(peaks)):
# #         distance.append(x[peaks[i]] - x[peaks[i - 1]])
# #
# #     return distance, peaks, data_cropped  # Return the peaks and cropped photon_counts_data for optional printing
# #
# # # Walk through the directory tree
# # for subdir, _, files in os.walk(root_dir):
# #     match = duration_pattern.search(os.path.basename(subdir))
# #     if match:
# #         duration_key = match.group(0)  # e.g. "20s", "60s"
# #         for file in sorted(files):
# #             file_path = os.path.join(subdir, file)
# #             try:
# #                 if file.startswith("CH0"):
# #                     photon_counts_data = np.loadtxt(file_path, delimiter=',')
# #                     label = os.path.relpath(file_path, root_dir)
# #                     ch0_by_duration[duration_key].append((photon_counts_data, label))
# #                 elif file.startswith("CH1"):
# #                     photon_counts_data = np.loadtxt(file_path, delimiter=',')
# #                     label = os.path.relpath(file_path, root_dir)
# #                     ch1_by_duration[duration_key].append((photon_counts_data, label))
# #             except Exception as e:
# #                 print(f"Error loading {file_path}: {e}")
# #
# #
# # def plot_grouped_subplots(data_dict, title_prefix, n_cols=3):
# #     distance_dict = defaultdict(list)  # To store distances by voltage
# #
# #     for duration, data_list in sorted(data_dict.items()):
# #         n_plots = len(data_list)
# #         n_rows = math.ceil(n_plots / n_cols)
# #
# #         fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 4 * n_rows))
# #         axes = axes.flatten()
# #
# #         for idx, (photon_counts_data, label) in enumerate(data_list):
# #             ax = axes[idx]
# #             # Extract voltage-based title from the label
# #             title = extract_voltage_and_title(label)
# #
# #             # Find peaks and label them on the plot
# #             distance, peaks, cropped_data = find_and_label_peaks(photon_counts_data, ax, title, crop_off)
# #
# #             # Store distances in the dictionary under the appropriate voltage title
# #             distance_dict[title].append(distance)
# #
# #             # Set the title for the plot
# #             ax.set_title(title, fontsize=8)
# #
# #         # Remove empty subplots if they exist
# #         for j in range(idx + 1, len(axes)):
# #             fig.delaxes(axes[j])
# #
# #         fig.suptitle(f"{title_prefix} - Duration: {duration}", fontsize=16)
# #         plt.tight_layout(rect=[0, 0, 1, 0.96])
# #         plt.show()
# #
# #     return distance_dict  # Return the dictionary of distances
# #
# #
# # # Get the distance photon_counts_data for CH0 and CH1 grouped by duration
# # ch0_distances = plot_grouped_subplots(ch0_by_duration, "CH0 Files")
# # ch1_distances = plot_grouped_subplots(ch1_by_duration, "CH1 Files")
# #
# # # Combine distances from both CH0 and CH1 into a single dictionary
# # all_distances = {**ch0_distances, **ch1_distances}
# #
# # # Convert the distances dictionary into a pandas DataFrame
# # # Make sure that each voltage title has the same number of rows (pad with NaN if necessary)
# # max_peaks = max(len(distances) for distances in all_distances.values())
# #
# # # Create a DataFrame with the appropriate dimensions
# # data_for_table = {}
# #
# # # Add each voltage title as a column
# # for voltage, distances in all_distances.items():
# #     # Pad the list of distances with NaN to ensure all columns have the same length
# #     padded_distances = distances + [np.nan] * (max_peaks - len(distances))
# #     data_for_table[voltage] = padded_distances
# #
# # # Create DataFrame
# # df_distances = pd.DataFrame(data_for_table)
# #
# # # Print the table
# # print("\nDistance Table:")
# # print(df_distances)
# #
# #
# #
# #
# # #
# # # import matplotlib
# # # matplotlib.use('TkAgg')  # For PyCharm interactivity
# # #
# # # import os
# # # import re
# # # import numpy as np
# # # import matplotlib.pyplot as plt
# # # import math
# # # from collections import defaultdict
# # # from scipy.signal import find_peaks
# # #
# # # # Set the root directory
# # # # root_dir = 'photon_counts_data/20250402_pulse_height_vary'
# # # root_dir = 'photon_counts_data/20250403'
# # # crop_off = 3700
# # # vertical_lines = False
# # #
# # # # Dictionaries to hold photon_counts_data grouped by duration (like '20s', '60s') and channel
# # # ch0_by_duration = defaultdict(list)
# # # ch1_by_duration = defaultdict(list)
# # #
# # # # Regex to extract duration from folder names (e.g., '20s' from '1_2V_20s')
# # # duration_pattern = re.compile(r'(\d+)s$')
# # #
# # #
# # # # Function to extract voltage and format the title
# # # def extract_voltage_and_title(file_name):
# # #     match = re.match(r"(\d+)_?(\d+)_gain", file_name)
# # #     if match:
# # #         voltage = float(f"{match.group(1)}.{match.group(2)}")  # Create voltage like 65.5V
# # #         return f"{voltage}V gain"
# # #     return file_name  # Default to the filename if not matching the pattern
# # #
# # #
# # # def find_and_label_peaks(photon_counts_data, ax, label, crop_off, vertical_lines=vertical_lines):
# # #     # Apply cropping
# # #     data_cropped = photon_counts_data[:-crop_off]
# # #     x = np.arange(len(data_cropped))
# # #
# # #     # Find peaks
# # #     peaks, properties = find_peaks(data_cropped, height=0.5, distance=15)  # Adjust height and distance as needed
# # #
# # #     # Plot the photon_counts_data and peaks
# # #     ax.plot(x, data_cropped, label=label, alpha=0.7)
# # #     ax.scatter(x[peaks], data_cropped[peaks], color='red', label='Peaks')
# # #
# # #     # Add a dashed vertical line at each peak
# # #     if vertical_lines == True:
# # #         for peak in peaks:
# # #             ax.axvline(x=peak, color='red', linestyle='--', linewidth=1)  # Dashed red vertical line
# # #
# # #     # Label each peak
# # #     for i, idx in enumerate(peaks):
# # #         ax.text(x[idx], data_cropped[idx] + 100, f'{i + 1}', ha='center', va='bottom', fontsize=9, color='red')
# # #
# # #     ax.set_xlabel("Index")
# # #     ax.set_ylabel("Value")
# # #     ax.grid(True)
# # #
# # #     # Calculate and print the horizontal distance between consecutive peaks
# # #     distance = []
# # #     for i in range(1, len(peaks)):
# # #         distance.append(x[peaks[i]] - x[peaks[i - 1]])  # Properly append distances
# # #
# # #     return distance, peaks, data_cropped  # Return the peaks and cropped photon_counts_data for optional printing
# # #
# # # # Walk through the directory tree
# # # for subdir, _, files in os.walk(root_dir):
# # #     match = duration_pattern.search(os.path.basename(subdir))
# # #     if match:
# # #         duration_key = match.group(0)  # e.g. "20s", "60s"
# # #         for file in sorted(files):
# # #             file_path = os.path.join(subdir, file)
# # #             try:
# # #                 if file.startswith("CH0"):
# # #                     photon_counts_data = np.loadtxt(file_path, delimiter=',')
# # #                     label = os.path.relpath(file_path, root_dir)
# # #                     ch0_by_duration[duration_key].append((photon_counts_data, label))
# # #                 elif file.startswith("CH1"):
# # #                     photon_counts_data = np.loadtxt(file_path, delimiter=',')
# # #                     label = os.path.relpath(file_path, root_dir)
# # #                     ch1_by_duration[duration_key].append((photon_counts_data, label))
# # #             except Exception as e:
# # #                 print(f"Error loading {file_path}: {e}")
# # #
# # #
# # # def plot_grouped_subplots(data_dict, title_prefix, n_cols=3):
# # #     for duration, data_list in sorted(data_dict.items()):
# # #         n_plots = len(data_list)
# # #         n_rows = math.ceil(n_plots / n_cols)
# # #
# # #         fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 4 * n_rows))
# # #         axes = axes.flatten()
# # #
# # #         for idx, (photon_counts_data, label) in enumerate(data_list):
# # #             ax = axes[idx]
# # #             # Extract voltage-based title from the label
# # #             title = extract_voltage_and_title(label)
# # #
# # #             # Find peaks and label them on the plot
# # #             distance, peaks, cropped_data = find_and_label_peaks(photon_counts_data, ax, title, crop_off)
# # #
# # #             # Print distances with the title of the subplot (which includes the voltage)
# # #             for i in range(1, len(peaks)):
# # #                 print(f"Gain {title} - Duration {duration} - Distance between Peak {i} and Peak {i + 1}: {distance[i - 1]} units")
# # #
# # #             # Set the title for the plot
# # #             ax.set_title(title, fontsize=8)
# # #
# # #         # Remove empty subplots if they exist
# # #         for j in range(idx + 1, len(axes)):
# # #             fig.delaxes(axes[j])
# # #
# # #         fig.suptitle(f"{title_prefix} - Duration: {duration}", fontsize=16)
# # #         plt.tight_layout(rect=[0, 0, 1, 0.96])
# # #         plt.show()
# # #
# # #
# # # # Plot CH0 and CH1 grouped by duration
# # # plot_grouped_subplots(ch0_by_duration, "CH0 Files")
# # # plot_grouped_subplots(ch1_by_duration, "CH1 Files")
# # #
# # #
# # #
# # # # # import matplotlib
# # # # # matplotlib.use('TkAgg')  # For PyCharm interactivity
# # # # #
# # # # # import os
# # # # # import re
# # # # # import numpy as np
# # # # # import matplotlib.pyplot as plt
# # # # # import math
# # # # # from collections import defaultdict
# # # # # from scipy.signal import find_peaks
# # # # # import pandas as pd  # Import pandas for creating the table
# # # # #
# # # # # # Set the root directory
# # # # # root_dir = 'photon_counts_data/20250403'
# # # # # crop_off = 3950
# # # # #
# # # # # # Dictionaries to hold photon_counts_data grouped by duration (like '20s', '60s') and channel
# # # # # ch0_by_duration = defaultdict(list)
# # # # # ch1_by_duration = defaultdict(list)
# # # # #
# # # # # # Regex to extract duration from folder names (e.g., '20s' from '1_2V_20s')
# # # # # duration_pattern = re.compile(r'(\d+)s$')
# # # # #
# # # # #
# # # # # # Function to extract voltage and format the title
# # # # # def extract_voltage_and_title(file_name):
# # # # #     match = re.match(r"(\d+)_?(\d+)_gain", file_name)
# # # # #     if match:
# # # # #         voltage = float(f"{match.group(1)}.{match.group(2)}")  # Create voltage like 65.5V
# # # # #         return f"{voltage}V gain"
# # # # #     return file_name  # Default to the filename if not matching the pattern
# # # # #
# # # # #
# # # # # # Function to find and label peaks with dashed vertical lines and return distances
# # # # # def find_and_label_peaks(photon_counts_data, ax, label, crop_off):
# # # # #     # Apply cropping
# # # # #     data_cropped = photon_counts_data[:-crop_off]
# # # # #     x = np.arange(len(data_cropped))
# # # # #
# # # # #     # Find peaks
# # # # #     peaks, properties = find_peaks(data_cropped, height=0.5, distance=15)  # Adjust height and distance as needed
# # # # #
# # # # #     # Plot the photon_counts_data and peaks
# # # # #     ax.plot(x, data_cropped, label=label, alpha=0.7)
# # # # #     ax.scatter(x[peaks], data_cropped[peaks], color='red', label='Peaks')
# # # # #
# # # # #     # Add a dashed vertical line at each peak
# # # # #     for peak in peaks:
# # # # #         ax.axvline(x=peak, color='red', linestyle='--', linewidth=1)  # Dashed red vertical line
# # # # #
# # # # #     # Label each peak
# # # # #     for i, idx in enumerate(peaks):
# # # # #         ax.text(x[idx], data_cropped[idx] + 100, f'{i + 1}', ha='center', va='bottom', fontsize=9, color='red')
# # # # #
# # # # #     ax.set_xlabel("Index")
# # # # #     ax.set_ylabel("Value")
# # # # #     ax.grid(True)
# # # # #
# # # # #     # Calculate and return the horizontal distance between consecutive peaks
# # # # #     distances = []
# # # # #     for i in range(1, len(peaks)):
# # # # #         distance = x[peaks[i]] - x[peaks[i - 1]]
# # # # #         distances.append(distance)
# # # # #
# # # # #     return distances  # Return the list of distances
# # # # #
# # # # #
# # # # # # Function to create a table of distances for each channel
# # # # # def create_distance_table(distances_dict, n_channels):
# # # # #     # Create a list of column names (subplot titles for each channel)
# # # # #     columns = [f"Channel {i + 1} ({title})" for i, (title, _) in enumerate(distances_dict.items())]
# # # # #
# # # # #     # Create the first row as "Distance from Peak[i] to Peak[i-1]"
# # # # #     table_data = [["Distance from Peak[i] to Peak[i-1]"] + [None] * n_channels]
# # # # #
# # # # #     # Find the maximum number of distances to normalize the table
# # # # #     max_distances = max(len(distances) for distances in distances_dict.values())
# # # # #
# # # # #     # Fill the table with distances for each channel
# # # # #     for i in range(max_distances):
# # # # #         row = [f"Distance {i + 1}"]  # First column is the distance number
# # # # #         for title, distances in distances_dict.items():
# # # # #             # If there is a distance for this channel, add it, otherwise add None
# # # # #             row.append(distances[i] if i < len(distances) else None)
# # # # #         table_data.append(row)
# # # # #
# # # # #     # Create a pandas DataFrame from the table photon_counts_data
# # # # #     df = pd.DataFrame(table_data[1:], columns=columns)
# # # # #     return df
# # # # #
# # # # #
# # # # # # Walk through the directory tree
# # # # # distances_dict = {}  # This will hold the distances for each channel
# # # # # for subdir, _, files in os.walk(root_dir):
# # # # #     match = duration_pattern.search(os.path.basename(subdir))
# # # # #     if match:
# # # # #         duration_key = match.group(0)  # e.g. "20s", "60s"
# # # # #         for file in sorted(files):
# # # # #             file_path = os.path.join(subdir, file)
# # # # #             try:
# # # # #                 if file.startswith("CH0"):
# # # # #                     photon_counts_data = np.loadtxt(file_path, delimiter=',')
# # # # #                     label = os.path.relpath(file_path, root_dir)
# # # # #                     title = extract_voltage_and_title(label)
# # # # #                     distances = find_and_label_peaks(photon_counts_data, None, title, crop_off)
# # # # #                     distances_dict[title] = distances
# # # # #                 elif file.startswith("CH1"):
# # # # #                     photon_counts_data = np.loadtxt(file_path, delimiter=',')
# # # # #                     label = os.path.relpath(file_path, root_dir)
# # # # #                     title = extract_voltage_and_title(label)
# # # # #                     distances = find_and_label_peaks(photon_counts_data, None, title, crop_off)
# # # # #                     distances_dict[title] = distances
# # # # #             except Exception as e:
# # # # #                 print(f"Error loading {file_path}: {e}")
# # # # #
# # # # # # Now create the table of distances
# # # # # df_distances = create_distance_table(distances_dict, n_channels=len(distances_dict))
# # # # #
# # # # # # Print the table
# # # # # print("\nDistance Between Peaks Table:")
# # # # # print(df_distances)
# # # #
# # # # import matplotlib
# # # # matplotlib.use('TkAgg')  # For PyCharm interactivity
# # # #
# # # # import os
# # # # import re
# # # # import numpy as np
# # # # import matplotlib.pyplot as plt
# # # # import math
# # # # from collections import defaultdict
# # # # from scipy.signal import find_peaks
# # # #
# # # # # Set the root directory
# # # # # root_dir = 'photon_counts_data/20250402_pulse_height_vary'
# # # # root_dir = 'photon_counts_data/20250403'
# # # # crop_off = 3700
# # # # vertical_lines = False
# # # #
# # # #
# # # # # Dictionaries to hold photon_counts_data grouped by duration (like '20s', '60s') and channel
# # # # ch0_by_duration = defaultdict(list)
# # # # ch1_by_duration = defaultdict(list)
# # # #
# # # # # Regex to extract duration from folder names (e.g., '20s' from '1_2V_20s')
# # # # duration_pattern = re.compile(r'(\d+)s$')
# # # #
# # # #
# # # # # Function to extract voltage and format the title
# # # # def extract_voltage_and_title(file_name):
# # # #     match = re.match(r"(\d+)_?(\d+)_gain", file_name)
# # # #     if match:
# # # #         voltage = float(f"{match.group(1)}.{match.group(2)}")  # Create voltage like 65.5V
# # # #         return f"{voltage}V gain"
# # # #     return file_name  # Default to the filename if not matching the pattern
# # # #
# # # #
# # # # def find_and_label_peaks(photon_counts_data, ax, label, crop_off,vertical_lines=vertical_lines):
# # # #     # Apply cropping
# # # #     data_cropped = photon_counts_data[:-crop_off]
# # # #     x = np.arange(len(data_cropped))
# # # #
# # # #     # Find peaks
# # # #     peaks, properties = find_peaks(data_cropped, height=0.5, distance=15)  # Adjust height and distance as needed
# # # #
# # # #     # Plot the photon_counts_data and peaks
# # # #     ax.plot(x, data_cropped, label=label, alpha=0.7)
# # # #     ax.scatter(x[peaks], data_cropped[peaks], color='red', label='Peaks')
# # # #
# # # #     # Add a dashed vertical line at each peak
# # # #     if vertical_lines == True:
# # # #         for peak in peaks:
# # # #             ax.axvline(x=peak, color='red', linestyle='--', linewidth=1)  # Dashed red vertical line
# # # #
# # # #     # Label each peak
# # # #     for i, idx in enumerate(peaks):
# # # #         ax.text(x[idx], data_cropped[idx] + 100, f'{i + 1}', ha='center', va='bottom', fontsize=9, color='red')
# # # #
# # # #     ax.set_xlabel("Index")
# # # #     ax.set_ylabel("Value")
# # # #     ax.grid(True)
# # # #
# # # #     # Calculate and print the horizontal distance between consecutive peaks
# # # #     distance = []
# # # #     for i in range(1, len(peaks)):
# # # #         distance[i] = x[peaks[i]] - x[peaks[i - 1]]
# # # #     #    print(f"Distance between Peak {i} and Peak {i + 1}: {distance} units")
# # # #
# # # #     return distance,peaks, data_cropped  # Return the peaks and cropped photon_counts_data for optional printing
# # # #
# # # # # Walk through the directory tree
# # # # for subdir, _, files in os.walk(root_dir):
# # # #     match = duration_pattern.search(os.path.basename(subdir))
# # # #     if match:
# # # #         duration_key = match.group(0)  # e.g. "20s", "60s"
# # # #         for file in sorted(files):
# # # #             file_path = os.path.join(subdir, file)
# # # #             try:
# # # #                 if file.startswith("CH0"):
# # # #                     photon_counts_data = np.loadtxt(file_path, delimiter=',')
# # # #                     label = os.path.relpath(file_path, root_dir)
# # # #                     ch0_by_duration[duration_key].append((photon_counts_data, label))
# # # #                 elif file.startswith("CH1"):
# # # #                     photon_counts_data = np.loadtxt(file_path, delimiter=',')
# # # #                     label = os.path.relpath(file_path, root_dir)
# # # #                     ch1_by_duration[duration_key].append((photon_counts_data, label))
# # # #             except Exception as e:
# # # #                 print(f"Error loading {file_path}: {e}")
# # # #
# # # #
# # # # def plot_grouped_subplots(data_dict, title_prefix, n_cols=3):
# # # #     for duration, data_list in sorted(data_dict.items()):
# # # #         n_plots = len(data_list)
# # # #         n_rows = math.ceil(n_plots / n_cols)
# # # #
# # # #         fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 4 * n_rows))
# # # #         axes = axes.flatten()
# # # #
# # # #         for idx, (photon_counts_data, label) in enumerate(data_list):
# # # #             ax = axes[idx]
# # # #             # Extract voltage-based title from the label
# # # #             title = extract_voltage_and_title(label)
# # # #
# # # #             # Find peaks and label them on the plot
# # # #             peaks, cropped_data, distance = find_and_label_peaks(photon_counts_data, ax, title, crop_off)
# # # #
# # # #             for i in range(1, len(peaks)):
# # # #                 print(f"Gain {title}V Distance between Peak {i} and Peak {i + 1}: {distance} units")
# # # #
# # # #             # Set the title for the plot
# # # #             ax.set_title(title, fontsize=8)
# # # #
# # # #         # Remove empty subplots if they exist
# # # #         for j in range(idx + 1, len(axes)):
# # # #             fig.delaxes(axes[j])
# # # #
# # # #         fig.suptitle(f"{title_prefix} - Duration: {duration}", fontsize=16)
# # # #         plt.tight_layout(rect=[0, 0, 1, 0.96])
# # # #         plt.show()
# # # #
# # # #
# # # # # Plot CH0 and CH1 grouped by duration
# # # # plot_grouped_subplots(ch0_by_duration, "CH0 Files")
# # # # plot_grouped_subplots(ch1_by_duration, "CH1 Files")
# # # #
# # # #
# # # # # import matplotlib
# # # # # matplotlib.use('TkAgg')  # For PyCharm interactivity
# # # # #
# # # # # import os
# # # # # import re
# # # # # import numpy as np
# # # # # import matplotlib.pyplot as plt
# # # # # import math
# # # # # from collections import defaultdict
# # # # # from scipy.signal import find_peaks
# # # # # import pandas as pd  # Import pandas for creating the table
# # # # #
# # # # # # Set the root directory
# # # # # root_dir = 'photon_counts_data/20250403'
# # # # # crop_off = 3950
# # # # #
# # # # # # Dictionaries to hold photon_counts_data grouped by duration (like '20s', '60s') and channel
# # # # # ch0_by_duration = defaultdict(list)
# # # # # ch1_by_duration = defaultdict(list)
# # # # #
# # # # # # Regex to extract duration from folder names (e.g., '20s' from '1_2V_20s')
# # # # # duration_pattern = re.compile(r'(\d+)s$')
# # # # #
# # # # #
# # # # # # Function to extract voltage and format the title
# # # # # def extract_voltage_and_title(file_name):
# # # # #     match = re.match(r"(\d+)_?(\d+)_gain", file_name)
# # # # #     if match:
# # # # #         voltage = float(f"{match.group(1)}.{match.group(2)}")  # Create voltage like 65.5V
# # # # #         return f"{voltage}V gain"
# # # # #     return file_name  # Default to the filename if not matching the pattern
# # # # #
# # # # #
# # # # # # Function to find and label peaks with dashed vertical lines and return distances
# # # # # def find_and_label_peaks(photon_counts_data, ax, label, crop_off):
# # # # #     # Apply cropping
# # # # #     data_cropped = photon_counts_data[:-crop_off]
# # # # #     x = np.arange(len(data_cropped))
# # # # #
# # # # #     # Find peaks
# # # # #     peaks, properties = find_peaks(data_cropped, height=0.5, distance=15)  # Adjust height and distance as needed
# # # # #
# # # # #     # Plot the photon_counts_data and peaks
# # # # #     ax.plot(x, data_cropped, label=label, alpha=0.7)
# # # # #     ax.scatter(x[peaks], data_cropped[peaks], color='red', label='Peaks')
# # # # #
# # # # #     # Add a dashed vertical line at each peak
# # # # #     for peak in peaks:
# # # # #         ax.axvline(x=peak, color='red', linestyle='--', linewidth=1)  # Dashed red vertical line
# # # # #
# # # # #     # Label each peak
# # # # #     for i, idx in enumerate(peaks):
# # # # #         ax.text(x[idx], data_cropped[idx] + 100, f'{i + 1}', ha='center', va='bottom', fontsize=9, color='red')
# # # # #
# # # # #     ax.set_xlabel("Index")
# # # # #     ax.set_ylabel("Value")
# # # # #     ax.grid(True)
# # # # #
# # # # #     # Calculate and return the horizontal distance between consecutive peaks
# # # # #     distances = []
# # # # #     for i in range(1, len(peaks)):
# # # # #         distance = x[peaks[i]] - x[peaks[i - 1]]
# # # # #         distances.append(distance)
# # # # #
# # # # #     return distances  # Return the list of distances
# # # # #
# # # # #
# # # # # # Function to create a table of distances for each channel
# # # # # def create_distance_table(distances_dict, n_channels):
# # # # #     # Create a list of column names (subplot titles for each channel)
# # # # #     columns = [f"Channel {i + 1} ({title})" for i, (title, _) in enumerate(distances_dict.items())]
# # # # #
# # # # #     # Create the first row as "Distance from Peak[i] to Peak[i-1]"
# # # # #     table_data = [["Distance from Peak[i] to Peak[i-1]"] + [None] * n_channels]
# # # # #
# # # # #     # Find the maximum number of distances to normalize the table
# # # # #     max_distances = max(len(distances) for distances in distances_dict.values())
# # # # #
# # # # #     # Fill the table with distances for each channel
# # # # #     for i in range(max_distances):
# # # # #         row = [f"Distance {i + 1}"]  # First column is the distance number
# # # # #         for title, distances in distances_dict.items():
# # # # #             # If there is a distance for this channel, add it, otherwise add None
# # # # #             row.append(distances[i] if i < len(distances) else None)
# # # # #         table_data.append(row)
# # # # #
# # # # #     # Create a pandas DataFrame from the table photon_counts_data
# # # # #     df = pd.DataFrame(table_data[1:], columns=columns)
# # # # #     return df
# # # # #
# # # # #
# # # # # # Walk through the directory tree
# # # # # distances_dict = {}  # This will hold the distances for each channel
# # # # # for subdir, _, files in os.walk(root_dir):
# # # # #     match = duration_pattern.search(os.path.basename(subdir))
# # # # #     if match:
# # # # #         duration_key = match.group(0)  # e.g. "20s", "60s"
# # # # #         for file in sorted(files):
# # # # #             file_path = os.path.join(subdir, file)
# # # # #             try:
# # # # #                 if file.startswith("CH0"):
# # # # #                     photon_counts_data = np.loadtxt(file_path, delimiter=',')
# # # # #                     label = os.path.relpath(file_path, root_dir)
# # # # #                     title = extract_voltage_and_title(label)
# # # # #                     distances = find_and_label_peaks(photon_counts_data, None, title, crop_off)
# # # # #                     distances_dict[title] = distances
# # # # #                 elif file.startswith("CH1"):
# # # # #                     photon_counts_data = np.loadtxt(file_path, delimiter=',')
# # # # #                     label = os.path.relpath(file_path, root_dir)
# # # # #                     title = extract_voltage_and_title(label)
# # # # #                     distances = find_and_label_peaks(photon_counts_data, None, title, crop_off)
# # # # #                     distances_dict[title] = distances
# # # # #             except Exception as e:
# # # # #                 print(f"Error loading {file_path}: {e}")
# # # # #
# # # # # # Now create the table of distances
# # # # # df_distances = create_distance_table(distances_dict, n_channels=len(distances_dict))
# # # # #
# # # # # # Print the table
# # # # # print("\nDistance Between Peaks Table:")
# # # # # print(df_distances)
# # # #
# # # # import matplotlib
# # # #
# # # # matplotlib.use('TkAgg')  # For PyCharm interactivity
# # # #
# # # # import os
# # # # import re
# # # # import numpy as np
# # # # import matplotlib.pyplot as plt
# # # # import math
# # # # from collections import defaultdict
# # # # from scipy.signal import find_peaks
# # # #
# # # # # Set the root directory
# # # # # root_dir = 'photon_counts_data/20250402_pulse_height_vary'
# # # # root_dir = 'photon_counts_data/20250403'
# # # # crop_off = 3700
# # # # vertical_lines = False
# # # #
# # # #
# # # # # Dictionaries to hold photon_counts_data grouped by duration (like '20s', '60s') and channel
# # # # ch0_by_duration = defaultdict(list)
# # # # ch1_by_duration = defaultdict(list)
# # # #
# # # # # Regex to extract duration from folder names (e.g., '20s' from '1_2V_20s')
# # # # duration_pattern = re.compile(r'(\d+)s$')
# # # #
# # # #
# # # # # Function to extract voltage and format the title
# # # # def extract_voltage_and_title(file_name):
# # # #     match = re.match(r"(\d+)_?(\d+)_gain", file_name)
# # # #     if match:
# # # #         voltage = float(f"{match.group(1)}.{match.group(2)}")  # Create voltage like 65.5V
# # # #         return f"{voltage}V gain"
# # # #     return file_name  # Default to the filename if not matching the pattern
# # # #
# # # #
# # # # def find_and_label_peaks(photon_counts_data, ax, label, crop_off,vertical_lines=vertical_lines):
# # # #     # Apply cropping
# # # #     data_cropped = photon_counts_data[:-crop_off]
# # # #     x = np.arange(len(data_cropped))
# # # #
# # # #     # Find peaks
# # # #     peaks, properties = find_peaks(data_cropped, height=0.5, distance=15)  # Adjust height and distance as needed
# # # #
# # # #     # Plot the photon_counts_data and peaks
# # # #     ax.plot(x, data_cropped, label=label, alpha=0.7)
# # # #     ax.scatter(x[peaks], data_cropped[peaks], color='red', label='Peaks')
# # # #
# # # #     # Add a dashed vertical line at each peak
# # # #     if vertical_lines == True:
# # # #         for peak in peaks:
# # # #             ax.axvline(x=peak, color='red', linestyle='--', linewidth=1)  # Dashed red vertical line
# # # #
# # # #     # Label each peak
# # # #     for i, idx in enumerate(peaks):
# # # #         ax.text(x[idx], data_cropped[idx] + 100, f'{i + 1}', ha='center', va='bottom', fontsize=9, color='red')
# # # #
# # # #     ax.set_xlabel("Index")
# # # #     ax.set_ylabel("Value")
# # # #     ax.grid(True)
# # # #
# # # #     # Calculate and print the horizontal distance between consecutive peaks
# # # #     for i in range(1, len(peaks)):
# # # #         distance = x[peaks[i]] - x[peaks[i - 1]]
# # # #         print(f"Distance between Peak {i} and Peak {i + 1}: {distance} units")
# # # #
# # # #     return peaks, data_cropped  # Return the peaks and cropped photon_counts_data for optional printing
# # # #
# # # # # Walk through the directory tree
# # # # for subdir, _, files in os.walk(root_dir):
# # # #     match = duration_pattern.search(os.path.basename(subdir))
# # # #     if match:
# # # #         duration_key = match.group(0)  # e.g. "20s", "60s"
# # # #         for file in sorted(files):
# # # #             file_path = os.path.join(subdir, file)
# # # #             try:
# # # #                 if file.startswith("CH0"):
# # # #                     photon_counts_data = np.loadtxt(file_path, delimiter=',')
# # # #                     label = os.path.relpath(file_path, root_dir)
# # # #                     ch0_by_duration[duration_key].append((photon_counts_data, label))
# # # #                 elif file.startswith("CH1"):
# # # #                     photon_counts_data = np.loadtxt(file_path, delimiter=',')
# # # #                     label = os.path.relpath(file_path, root_dir)
# # # #                     ch1_by_duration[duration_key].append((photon_counts_data, label))
# # # #             except Exception as e:
# # # #                 print(f"Error loading {file_path}: {e}")
# # # #
# # # #
# # # # def plot_grouped_subplots(data_dict, title_prefix, n_cols=3):
# # # #     for duration, data_list in sorted(data_dict.items()):
# # # #         n_plots = len(data_list)
# # # #         n_rows = math.ceil(n_plots / n_cols)
# # # #
# # # #         fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 4 * n_rows))
# # # #         axes = axes.flatten()
# # # #
# # # #         for idx, (photon_counts_data, label) in enumerate(data_list):
# # # #             ax = axes[idx]
# # # #             # Extract voltage-based title from the label
# # # #             title = extract_voltage_and_title(label)
# # # #
# # # #             # Find peaks and label them on the plot
# # # #             peaks, cropped_data = find_and_label_peaks(photon_counts_data, ax, title, crop_off)
# # # #
# # # #             # Set the title for the plot
# # # #             ax.set_title(title, fontsize=8)
# # # #
# # # #         # Remove empty subplots if they exist
# # # #         for j in range(idx + 1, len(axes)):
# # # #             fig.delaxes(axes[j])
# # # #
# # # #         fig.suptitle(f"{title_prefix} - Duration: {duration}", fontsize=16)
# # # #         plt.tight_layout(rect=[0, 0, 1, 0.96])
# # # #         plt.show()
# # # #
# # # #
# # # # # Plot CH0 and CH1 grouped by duration
# # # # plot_grouped_subplots(ch0_by_duration, "CH0 Files")
# # # # plot_grouped_subplots(ch1_by_duration, "CH1 Files")
