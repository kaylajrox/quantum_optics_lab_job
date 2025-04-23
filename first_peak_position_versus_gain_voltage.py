# submodule on getting right first peak isnt working

import os
import re
import pandas as pd

# Path to your CSV folder
data_dir = 'generated_peak_data_results'

# Output CSV filename
output_file = 'combined_peak_data.csv'

# Regex pattern to extract gain voltage and pulse height
pattern = re.compile(r'gain_voltage(\d+\.\d+)V_and_pulse_height(\d+\.\d+)V')

# Container for all data
all_data = []

# Loop through all CSVs
for file in os.listdir(data_dir):
    if file.endswith('.csv'):
        match = pattern.search(file)
        if match:
            gain_voltage = float(match.group(1))
            pulse_height = float(match.group(2))

            file_path = os.path.join(data_dir, file)
            df = pd.read_csv(file_path)

            # Clean up column headers just in case
            df.columns = df.columns.str.strip()

            # Add metadata columns from filename
            df['gain voltage'] = gain_voltage
            df['pulse height'] = pulse_height

            all_data.append(df)

# Combine all data into one DataFrame
combined_df = pd.concat(all_data, ignore_index=True)

# Save to CSV
combined_df = combined_df.sort_values(by='gain voltage').reset_index(drop=True)

# Combine all data into one DataFrame
combined_df = pd.concat(all_data, ignore_index=True)

# Sort by gain voltage (ascending)
combined_df = combined_df.sort_values(by='gain voltage').reset_index(drop=True)

# Save to CSV
combined_df.to_csv(output_file, index=False)
print(f"Combined and sorted data saved to: {output_file}")

# Group by gain voltage and get the first occurrence from each group
summary_df = combined_df.groupby('gain voltage', as_index=False).first()

# Select only the desired columns
simplified_df = summary_df[['Voltage Gain (V)', 'Peak Number', 'Peak Index', 'Peak Counts']]

# Save to CSV
simplified_df.to_csv('first_peaks_summary.csv', index=False)
print("Summary saved to: first_peaks_summary.csv")



# import os
# import re
# import pandas as pd
# import matplotlib.pyplot as plt
#
# # Path to your CSV folder
# data_dir = 'generated_peak_data_results'
#
# # Regex to extract gain voltage and pulse height from filename
# pattern = re.compile(r'gain_voltage(\d+\.\d+)V_and_pulse_height(\d+\.\d+)V')
#
# # List to collect individual DataFrames
# all_data = []
#
# # Loop through all CSVs
# for file in os.listdir(data_dir):
#     if file.endswith('.csv'):
#         match = pattern.search(file)
#         if match:
#             gain_voltage = float(match.group(1))
#             pulse_height = float(match.group(2))
#
#             file_path = os.path.join(data_dir, file)
#             df = pd.read_csv(file_path)
#
#             # Strip whitespace from headers if needed
#             df.columns = df.columns.str.strip()
#
#             # Add metadata columns
#             df['gain voltage'] = gain_voltage
#             df['pulse height'] = pulse_height
#
#             all_data.append(df)
#
# # Combine all DataFrames
# combined_df = pd.concat(all_data, ignore_index=True)
#
# print(combined_df)
#
#
# # import os
# # import re
# # import pandas as pd
# # import matplotlib.pyplot as plt
# #
# # # Path to your directory
# # data_dir = 'generated_peak_data_results'
# #
# # # Regex pattern to extract gain voltage and pulse height from filenames
# # pattern = re.compile(r'gain_voltage(\d+\.\d+)V_and_pulse_height(\d+\.\d+)V')
# #
# # # Store data grouped by gain voltage
# # data_by_gain = {}
# #
# # # Loop through files in directory
# # for file in os.listdir(data_dir):
# #     if file.endswith('.csv'):
# #         match = pattern.search(file)
# #         if match:
# #             gain_voltage = float(match.group(1))
# #             pulse_height = float(match.group(2))
# #             print(match.group(2))
# #             file_path = os.path.join(data_dir, file)
# #             df = pd.read_csv(file_path)
# #
# #             df = pd.read_csv(file_path)
# #             #print(f"Columns in {file}: {df.columns.tolist()}")
# #
# #             # Assuming columns include 'peak number' and 'peak index'
# #             peak_index = df['Peak Index']
# #             peak_counts = df['Peak Counts']
# #
# #             data_by_gain[gain_voltage] = (peak_index, peak_counts)
# #
# #
# # print("peak index",peak_index.shape)
# #
# # # Plotting
# # plt.figure(figsize=(10, 6))
# # for gain_voltage, (peak_index, peak_counts) in sorted(data_by_gain.items()):
# #     plt.scatter(peak_index, peak_counts, label=f'Gain {gain_voltage}V')
# #
# # plt.title(f'Peak Number vs Peak Index (Pulse Height = {pulse_height}V)')
# # plt.xlabel('Peak Index')
# # plt.ylabel('Peak Number')
# # plt.legend()
# # plt.grid(True)
# # plt.tight_layout()
# # plt.show()
