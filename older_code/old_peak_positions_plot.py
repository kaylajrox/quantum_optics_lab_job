import matplotlib

matplotlib.use('TkAgg')

import os
import re
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
from scipy.signal import find_peaks
import math

num_gain_voltages = 6

peak_positions = {65.1: 86, 65.4: 80, 65.6: 76, 65.7: 71, 65.8: 70, 66.0: 63}

voltage_gains = []
idx_positions = []

for voltage_gain, peak_position in peak_positions.items():
    voltage_gains.append(voltage_gain)
    idx_positions.append(peak_position)

# Plot peak index positions vs gain voltage
plt.figure(figsize=(6, 4))
plt.plot(voltage_gains, idx_positions, 'o-', color='tab:blue', label='Peak Index Position')

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