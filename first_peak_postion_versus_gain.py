import os
import re
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
from scipy.signal import find_peaks
import math
import csv

# Get the path to the root directory of the repo
root_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'photon_counts_data', '20250417_1_3_pulse_height')

# Initialize lists for storing data
voltage_gains = []
idx_positions = []
spacing_between_peaks = []

# Dictionary to store peak positions (voltage -> first peak index)
peak_positions = {}


# Function to read the peak data from CSV and print the content
def read_peak_data_from_file(filename):
    with open(filename, mode='r') as file:
        reader = csv.reader(file)
        header = next(reader)  # Skip the header row
        peak_data = []
        print(f"Reading file: {filename}")
        print(f"Header: {header}")
        for row in reader:
            peak_data.append(row)
        # Print the first few rows for debugging
        print(f"First few rows of {filename}: {peak_data[:5]}")
    return peak_data


# Read in peak data and extract relevant information
for file in os.listdir(root_dir):
    if file.startswith("peak_data") and file.endswith(".csv"):
        full_path = os.path.join(root_dir, file)

        # Debugging: Print the full file path being checked
        print(f"Checking file: {full_path}")

        # Check if the file exists
        if os.path.exists(full_path):
            gain_v_match = re.search(r"peak_data_(\d+\.\d+)_1\.3\.csv", file)
            if gain_v_match:
                gain_v = float(gain_v_match.group(1))

                peak_data = read_peak_data_from_file(full_path)

                # Ensure peak data is not empty
                if peak_data:
                    # Extract the first peak index
                    try:
                        first_peak_idx = int(
                            peak_data[0][1])  # First peak index (assuming second column has peak index)
                        peak_positions[gain_v] = first_peak_idx
                        idx_positions.append(first_peak_idx)
                        voltage_gains.append(gain_v)

                        # Calculate the spacing between the first and second peaks
                        if len(peak_data) > 1:
                            second_peak_idx = int(peak_data[1][1])  # Second peak index
                            spacing = second_peak_idx - first_peak_idx
                        else:
                            spacing = 0  # If only one peak, spacing is 0

                        spacing_between_peaks.append(spacing)
                    except IndexError:
                        print(f"Error: Missing peak index data in file {file}")
                else:
                    print(f"Warning: {full_path} is empty or has invalid data.")
            else:
                print(f"Warning: Filename {file} does not match the expected pattern.")
        else:
            print(f"Error: File {full_path} does not exist.")

# Debugging output: Check if the lists are populated
print("Voltage Gains:", voltage_gains)
print("First Peak Indexes:", idx_positions)

# If the lists are empty, exit the program with an informative message
if not voltage_gains or not idx_positions:
    print("Error: No data found. Ensure that the CSV files are read correctly.")
    exit()

# Plot 1: Peak index positions vs gain voltage
plt.figure(figsize=(6, 4))
plt.plot(voltage_gains, idx_positions, 'o-', color='tab:blue', label='First Peak Index Position')

# Fit line to data
z = np.polyfit(voltage_gains, idx_positions, 1)
p = np.poly1d(z)
plt.plot(voltage_gains, p(voltage_gains), '--', label=f"Fit: y = {z[0]:.2f}x + {z[1]:.2f}")

plt.xlabel("Gain Voltage (V)")
plt.ylabel("First Peak Index Position")
plt.title("First Peak Position vs Gain Voltage")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# Plot 2: Spacing between first two peaks vs gain voltage
plt.figure(figsize=(6, 4))
plt.plot(voltage_gains, spacing_between_peaks, 'o-', color='tab:green', label='Peak Spacing')

# Fit line to data
z_spacing = np.polyfit(voltage_gains, spacing_between_peaks, 1)
p_spacing = np.poly1d(z_spacing)
plt.plot(voltage_gains, p_spacing(voltage_gains), '--', label=f"Fit: y = {z_spacing[0]:.2f}x + {z_spacing[1]:.2f}")

plt.xlabel("Gain Voltage (V)")
plt.ylabel("Spacing between First and Second Peak (Index)")
plt.title("Peak Spacing vs Gain Voltage")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# Output the peak_positions dictionary for verification
print("Peak Positions:")
for voltage, peak_index in peak_positions.items():
    print(f"Voltage: {voltage} V -> First Peak Index: {peak_index}")
