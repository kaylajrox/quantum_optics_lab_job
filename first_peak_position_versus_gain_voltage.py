import os
import re
import pandas as pd
import matplotlib.pyplot as plt

# Path to your directory
data_dir = 'generated_peak_data_results'

# Choose specific pulse height (e.g., 1.3V or 1.6V)
target_pulse_height = 1.3

# Regex pattern to extract gain voltage and pulse height from filenames
pattern = re.compile(r'gain_voltage(\d+\.\d+)V_and_pulse_height(\d+\.\d+)V')

# Store data grouped by gain voltage
data_by_gain = {}

# Loop through files in directory
for file in os.listdir(data_dir):
    if file.endswith('.csv'):
        match = pattern.search(file)
        if match:
            gain_voltage = float(match.group(1))
            pulse_height = float(match.group(2))

            if pulse_height == target_pulse_height:
                file_path = os.path.join(data_dir, file)
                df = pd.read_csv(file_path)

                df = pd.read_csv(file_path)
                print(f"Columns in {file}: {df.columns.tolist()}")

                # Assuming columns include 'peak number' and 'peak index'
                peak_index = df['Peak Index']
                peak_counts = df['Peak Counts']

                data_by_gain[gain_voltage] = (peak_index, peak_counts)

print("p1",peak_index)
print("p2",peak_counts)

# Plotting
plt.figure(figsize=(10, 6))
for gain_voltage, (peak_index, peak_counts) in sorted(data_by_gain.items()):
    plt.scatter(peak_index, peak_counts, label=f'Gain {gain_voltage}V')

plt.title(f'Peak Number vs Peak Index (Pulse Height = {target_pulse_height}V)')
plt.xlabel('Peak Index')
plt.ylabel('Peak Number')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
