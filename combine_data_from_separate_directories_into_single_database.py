import os
import re
import pandas as pd

# Path to your CSV folder
data_dir = 'generated_peak_data_results'

# Output CSV filenames
combined_output = 'results_combined_peak_data.csv'
summary_output = 'results_first_peaks_summary.csv'

# Regex to extract channel, gain voltage, and pulse height
pattern = re.compile(r'peak_data_(CH\d+)_gain_(\d+\.\d+)V_pulse_(\d+\.\d+)V\.csv')

# Container for all data
all_data = []

# Loop through all CSVs
for file in os.listdir(data_dir):
    if file.endswith('.csv'):
        match = pattern.search(file)
        if match:
            channel = match.group(1)
            gain_voltage = float(match.group(2))
            pulse_height = float(match.group(3))

            file_path = os.path.join(data_dir, file)
            df = pd.read_csv(file_path)

            # Clean up column headers just in case
            df.columns = df.columns.str.strip()

            # Add metadata columns
            df['Channel (from filename)'] = channel
            df['Gain Voltage (from filename)'] = gain_voltage
            df['Pulse Height (from filename)'] = pulse_height

            all_data.append(df)

# Combine all data into one DataFrame
combined_df = pd.concat(all_data, ignore_index=True)

# Sort by channel → gain → pulse height → timestamp
combined_df = combined_df.sort_values(
    by=[
        'Channel (from filename)',
        'Gain Voltage (from filename)',
        'Pulse Height (from filename)',
        'Timestamp'  # Optional: helps ensure time ordering
    ]
).reset_index(drop=True)

# Save combined data
combined_df.to_csv(combined_output, index=False)
print(f"✅ Combined data saved to: {combined_output}")

# Group by channel + gain voltage + pulse height and get the first row in each group
summary_df = combined_df.groupby(
    ['Channel (from filename)', 'Gain Voltage (from filename)', 'Pulse Height (from filename)'],
    as_index=False
).first()

# Select simplified columns (include Timestamp now)
simplified_df = summary_df[
    ['Channel (from filename)', 'Gain Voltage (from filename)', 'Pulse Height (from filename)', 'Timestamp',
     'Peak Number', 'Peak Index', 'Peak Counts']
]

# Sort same as above
simplified_df = simplified_df.sort_values(
    by=[
        'Channel (from filename)',
        'Gain Voltage (from filename)',
        'Pulse Height (from filename)'
    ]
).reset_index(drop=True)

# Save simplified summary
simplified_df.to_csv(summary_output, index=False)
print(f"✅ First peaks summary saved to: {summary_output}")


# import os
# import re
# import pandas as pd
#
#
# # Path to your CSV folder
# data_dir = 'generated_peak_data_results'
#
# # Output CSV filenames
# combined_output = 'results_combined_peak_data_old.csv'
# summary_output = 'results_first_peaks_summary_old.csv'
#
# # Regex to extract channel, gain voltage, and pulse height
# pattern = re.compile(r'peak_data_(CH\d+)_gain_(\d+\.\d+)V_pulse_(\d+\.\d+)V\.csv')
#
# # Container for all data
# all_data = []
#
# # Loop through all CSVs
# for file in os.listdir(data_dir):
#     if file.endswith('.csv'):
#         match = pattern.search(file)
#         if match:
#             channel = match.group(1)
#             gain_voltage = float(match.group(2))
#             pulse_height = float(match.group(3))
#
#             file_path = os.path.join(data_dir, file)
#             df = pd.read_csv(file_path)
#
#             # Clean up column headers just in case
#             df.columns = df.columns.str.strip()
#
#             # Add metadata columns
#             df['Channel (from filename)'] = channel
#             df['Gain Voltage (from filename)'] = gain_voltage
#             df['Pulse Height (from filename)'] = pulse_height
#
#             all_data.append(df)
#
# # Combine all data into one DataFrame
# combined_df = pd.concat(all_data, ignore_index=True)
#
# # Sort by channel → gain → pulse height
# combined_df = combined_df.sort_values(
#     by=[
#         'Channel (from filename)',
#         'Gain Voltage (from filename)',
#         'Pulse Height (from filename)'
#     ]
# ).reset_index(drop=True)
#
# # Save combined data
# combined_df.to_csv(combined_output, index=False)
# print(f"✅ Combined data saved to: {combined_output}")
#
# # Group by channel + gain voltage + pulse height and get the first row in each group
# summary_df = combined_df.groupby(
#     ['Channel (from filename)', 'Gain Voltage (from filename)', 'Pulse Height (from filename)'],
#     as_index=False
# ).first()
#
# # Select simplified columns
# simplified_df = summary_df[
#     ['Channel (from filename)', 'Gain Voltage (from filename)', 'Pulse Height (from filename)', 'Peak Number', 'Peak Index', 'Peak Counts']
# ]
#
# # Sort same as above
# simplified_df = simplified_df.sort_values(
#     by=[
#         'Channel (from filename)',
#         'Gain Voltage (from filename)',
#         'Pulse Height (from filename)'
#     ]
# ).reset_index(drop=True)
#
# # Save simplified summary
# simplified_df.to_csv(summary_output, index=False)
# print(f"✅ First peaks summary saved to: {summary_output}")
