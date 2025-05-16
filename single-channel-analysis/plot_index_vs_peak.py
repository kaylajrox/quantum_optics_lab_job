import numpy as np
import matplotlib.pyplot as plt
from lmfit import Model, Parameters
from pathlib import Path
import os

# --- Resolve Repo Root and Results Directory ---
script_dir = Path(__file__).resolve().parent
repo_root = script_dir.parent  # Adjust if deeper
results_dir = repo_root / "results-from-generated-data"
os.makedirs(results_dir, exist_ok=True)

# --- Data File Paths ---
file_path_CH0 = "../data-photon-counts-SiPM/data-photon-counts-SiPM/20250428_pulse_height_vary/65_7_gain_1_0_pulse_300s/CH0@DT5720B_75_EspectrumR_65_7_gain_1_0_pulse_300s_20250428_160229.txt"
file_path_CH1 = "../data-photon-counts-SiPM/data-photon-counts-SiPM/20250428_more_light/65_7_gain_1_0_pulse_300s/CH1@DT5720B_75_EspectrumR_65_7_gain_1_0_pulse_300s_20250428_160229.txt"
print(file_path_CH0)
# --- Load Data ---
energies_CH1 = np.loadtxt(file_path_CH0)
energies_CH1_cropped = energies_CH1[:-3850]
x = np.arange(len(energies_CH1_cropped))  # X-axis (index)

# --- Good peak indices (manual selection for now) ---
good_peak_indices = [33, 65]
mu_guesses = x[good_peak_indices]

# --- Model Definition ---
def envelope_sum(x, mu_env, sigma_env, A_env, sigma_narrow, **kwargs):
    envelope = A_env * np.exp(- (x - mu_env)**2 / (2 * sigma_env**2))
    peak_sum = np.zeros_like(x)
    for key in kwargs:
        if key.startswith('A_'):
            i = key.split('_')[1]
            mu_i = kwargs[f'mu_{i}']
            A_i = kwargs[key]
            peak_sum += A_i * np.exp(- (x - mu_i)**2 / (2 * sigma_narrow**2))
    return envelope * peak_sum

model = Model(envelope_sum, independent_vars=['x'])

# --- Parameters ---
params = Parameters()
params.add('mu_env', value=np.mean(mu_guesses), min=0, max=len(x))
params.add('sigma_env', value=50, min=1, max=200)
params.add('A_env', value=1.0, min=0.1)
params.add('sigma_narrow', value=3.0, min=0.5, max=20)

for i, mu in enumerate(mu_guesses):
    params.add(f'mu_{i}', value=mu, vary=False)
    params.add(f'A_{i}', value=1.0, min=0.0)

# --- Fit Model ---
result = model.fit(energies_CH1_cropped, params, x=x)

# --- Plot Result ---
plt.figure(figsize=(10, 5))
plt.plot(x, energies_CH1_cropped, 'o', markersize=3, label='Data', color='blue')
plt.plot(x, result.best_fit, 'r-.', label='Best Fit', color='red')
plt.xlabel("Index")
plt.ylabel("Counts")
plt.title("LMFit: Envelope × Sum of Gaussians")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# --- Save Fit Report to CSV in results-from-generated-data ---
output_file = results_dir / "fit_results_peak_analysis.csv"
with open(output_file, 'w') as f:
    f.write(result.fit_report())
print(f"Fit report saved to {output_file}")



#
# import matplotlib
# matplotlib.use('TkAgg')  # For PyCharm interactivity
#
# import pandas as pd
# import matplotlib.pyplot as plt
# import numpy as np
# from datetime import datetime
# import csv
# from pathlib import Path
#
#
# # Load data
# df = pd.read_csv('..results-from-generated-data/results_combined_peak_data.csv')
# df.columns = df.columns.str.strip()
# df['Peak Number'] = pd.to_numeric(df['Peak Number'], errors='coerce')
# df['Peak Index'] = pd.to_numeric(df['Peak Index'], errors='coerce')
# df = df.dropna(subset=['Peak Number', 'Peak Index'])
#
# # Setup output file
# csv_filename = '..results-from-generated-data/results_spacing_from_slope.csv'
# with open(csv_filename, mode='w', newline='') as file:
#     writer = csv.writer(file)
#     writer.writerow([
#         'Current time of data made', 'Channel', 'Pulse Height (V)',
#         'Gain Voltage (V)', 'Average Spacing', 'Standard Deviation'
#     ])
#
#     pulse_color_map = {
#         1.0: 'black', 1.1: 'darkblue', 1.3: 'green',
#         1.6: 'orange', 2.0: 'deeppink', 2.3: 'red'
#     }
#
#     for ch in df['Channel (from filename)'].unique():
#         df_ch = df[df['Channel (from filename)'] == ch]
#         gain_voltages = sorted(df_ch['Gain Voltage (from filename)'].unique())
#
#         for gain in gain_voltages:
#             plt.figure(figsize=(8, 6))
#             df_gain = df_ch[df_ch['Gain Voltage (from filename)'] == gain]
#
#             print(f"\n=== CHANNEL: {ch} | GAIN VOLTAGE: {gain} V ===")
#
#             for pulse_height in sorted(df_gain['Pulse Height (from filename)'].unique()):
#                 df_pulse = df_gain[df_gain['Pulse Height (from filename)'] == pulse_height]
#                 df_pulse = df_pulse.sort_values('Peak Number')
#
#                 x = df_pulse['Peak Number'].values
#                 y = df_pulse['Peak Index'].values
#                 color = pulse_color_map.get(pulse_height, 'gray')
#
#                 print(f"\n→ Pulse Height = {pulse_height} V")
#
#                 if len(x) >= 2:
#                     slopes = np.diff(y) / np.diff(x)
#                     avg_slope = np.mean(slopes)
#                     slope_std = np.std(slopes)
#                     timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#
#                     for i, s in enumerate(slopes, start=1):
#                         print(f"   Slope between Peak {i} & {i+1}: {s:.2f}")
#                     print(f"   ↪ Average Slope: {avg_slope:.2f}")
#                     print(f"   ↪ Std Dev of Slopes: {slope_std:.2f}")
#
#                     # Save to CSV
#                     writer.writerow([timestamp, ch, pulse_height, gain, avg_slope, slope_std])
#
#                     # Fit line
#                     coeffs = np.polyfit(x, y, deg=1)
#                     x_fit = np.linspace(min(x), max(x), 300)
#                     y_fit = np.polyval(coeffs, x_fit)
#                     plt.plot(x_fit, y_fit, linestyle='--', color=color, label=f'{pulse_height}V fit')
#
#                     # Annotate
#                     eqn_str = f'y = {coeffs[0]:.2f}x + {coeffs[1]:.1f}'
#                     plt.text(x_fit[-1]+0.3, y_fit[-1], eqn_str, fontsize=12, color=color, va='center')
#                 else:
#                     print("   ⚠ Not enough data points to compute slope or fit.")
#
#                 plt.plot(x, y, marker='o', linestyle='-', color=color, label=f'{pulse_height}V pulse')
#
#             plt.title(f'{ch} — Peak Index vs. Peak Number (Gain = {gain} V)')
#             plt.xlabel('Peak Number')
#             plt.ylabel('Peak Index')
#             plt.grid(True)
#             plt.legend(title='Pulse Height')
#             plt.tight_layout()
#             plt.show()
#
# print(f"\n✅ Slope results written to: {csv_filename}")
#
