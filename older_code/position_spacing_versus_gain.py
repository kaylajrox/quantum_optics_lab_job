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

peak_positions = {65.1:16,65.4:25,65.6:28,65.7:33,65.8:34,66.0:44}

voltage_gains = []
idx_positions = []


for voltage_gain,peak_position in peak_positions.items():
    voltage_gains.append(voltage_gain)
    idx_positions.append(peak_position)

# Plot peak index positions vs gain voltage
plt.figure(figsize=(6, 4))
plt.plot(voltage_gains, idx_positions, 'o-', color='tab:blue', label='Peak Index Position')

z = np.polyfit(voltage_gains, idx_positions, 1)
p = np.poly1d(z)
plt.plot(voltage_gains, p(voltage_gains), '--', label=f"Fit: y = {z[0]:.2f}x + {z[1]:.2f}")

plt.xlabel("Gain Voltage (V)")
plt.ylabel("Peak Index Spacing between 1 and 2 ")
plt.title("Peak Position vs Gain Voltage")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()


