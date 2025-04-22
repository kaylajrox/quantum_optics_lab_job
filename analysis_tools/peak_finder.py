'''
Finds peaks for a single data txt file from compass
'''


import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

#======================================================================================
#        User set parameters here only, path to data txt file
#======================================================================================

file_path_CH = "../data_photon_counts/20250402_pulse_height_vary/1_2V_20s/CH0@DT5720B_75_EspectrumR_test_fixed1_2V_20s_20250402_150738.txt"
#file_path_CH = "data_photon_counts/20250402_pulse_height_vary/1_2V_20s/CH1@DT5720B_75_EspectrumR_test_fixed1_2V_20s_20250402_150738.txt"

#===================================================
#===================================================
#===================================================

# Example data_photon_counts (use your real data_photon_counts here)
energies_CH = np.loadtxt(file_path_CH)  # assuming one value per line

energies_CH_cropped = energies_CH[:-3850]

x = np.arange(len(energies_CH_cropped))
# Find peaks
peaks, properties = find_peaks(energies_CH_cropped, height=15, distance=15)  # tune height & distance

# --- Label each peak with its index ---
for i, idx in enumerate(peaks):
    plt.text(x[idx], energies_CH_cropped[idx] + 100, f'{i+1}', ha='center', va='bottom', fontsize=9, color='red')

# Plot
plt.scatter(x, energies_CH_cropped, s=10, label='Data')
plt.scatter(x[peaks], energies_CH_cropped[peaks], color='red', label='Peaks')
plt.xlabel("Index")
plt.ylabel("Value")
plt.title("Peak Finding")
plt.legend()
plt.grid(True)
plt.show()

# Optional: print peak info
for i, idx in enumerate(peaks):
    print(f"Peak {i+1}: x = {x[idx]}, energies_CH_cropped = {energies_CH_cropped[idx]}")
