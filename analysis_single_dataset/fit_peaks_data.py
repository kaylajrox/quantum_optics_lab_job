# TODO this is a tbh tool at the moment i like the input system! thats so cool

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d

# --- Config ---
file_path = input("Enter the path to your data file: ")  # Prompt user for file path
sigma_smooth = 3.0  # Smoothing factor
peak_height_threshold = 100  # Minimum height of peaks
peak_distance = 10  # Minimum distance between peaks

# --- Load Data ---
try:
    data = np.loadtxt(file_path)
except Exception as e:
    print(f"Error loading file: {e}")
    exit()

# --- Smooth Data ---
data_smoothed = gaussian_filter1d(data, sigma=sigma_smooth)

# --- Find Peaks ---
peaks, _ = find_peaks(data_smoothed, height=peak_height_threshold, distance=peak_distance)

# --- Plot Results ---
plt.figure(figsize=(12, 6))
plt.plot(data, label='Raw Data', color='blue', alpha=0.5)
plt.plot(data_smoothed, label='Smoothed Data', color='green', linestyle='--')
plt.scatter(peaks, data_smoothed[peaks], color='red', marker='x', s=100, label='Detected Peaks')

plt.xlabel("Index")
plt.ylabel("Counts")
plt.title("Peak Detection")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# --- Debug Info ---
print(f"Detected peaks at indices: {peaks}")

# import numpy as np
# import matplotlib.pyplot as plt
# from lmfit import Model, Parameters
# from scipy.signal import find_peaks
# from scipy.ndimage import gaussian_filter1d
#
# # --- Config ---
# file_path = "../data-photon-counts-SiPM/20250428_more_light/65_8_gain_1_6_pulse_300s/CH0@DT5720B_75_EspectrumR_test_fixed2_3V_300s_20250428_153028.txt"
#
# crop_end = 3850
# sigma_smooth = 3.0
# peak_height_threshold = 100
# peak_distance = 10
#
# # --- Load data ---
# data = np.loadtxt(file_path)
# data_cropped = data[:-crop_end]
# x = np.arange(len(data_cropped))
#
# # --- Smooth for better peak finding ---
# data_smoothed = gaussian_filter1d(data_cropped, sigma=sigma_smooth)
#
# # --- Find peaks automatically ---
# peaks, _ = find_peaks(data_smoothed, height=peak_height_threshold, distance=peak_distance)
#
# # --- Debug print ---
# print(f"Found peaks at indices: {peaks}")
#
# # --- Model: Envelope × Sum of Narrow Gaussians ---
# def envelope_sum(x, mu_env, sigma_env, A_env, sigma_narrow, **kwargs):
#     envelope = A_env * np.exp(- (x - mu_env)**2 / (2 * sigma_env**2))
#     peak_sum = np.zeros_like(x)
#     for key in kwargs:
#         if key.startswith('A_'):
#             i = key.split('_')[1]
#             mu_i = kwargs[f'mu_{i}']
#             A_i = kwargs[key]
#             peak_sum += A_i * np.exp(- (x - mu_i)**2 / (2 * sigma_narrow**2))
#     return envelope * peak_sum
#
# # --- lmfit Model ---
# model = Model(envelope_sum, independent_vars=['x'])
#
# # --- Define Parameters ---
# params = Parameters()
# params.add('mu_env', value=np.mean(peaks), min=0, max=len(x))
# params.add('sigma_env', value=50, min=1, max=200)
# params.add('A_env', value=1.0, min=0.1)
# params.add('sigma_narrow', value=3.0, min=0.5, max=20)
#
# for i, mu in enumerate(peaks):
#     params.add(f'mu_{i}', value=mu, vary=False)  # Fix peak positions
#     params.add(f'A_{i}', value=1.0, min=0.0)     # Amplitude of each peak
#
# # --- Fit the model ---
# result = model.fit(data_cropped, params, x=x)
#
# # --- Plot ---
# plt.figure(figsize=(12, 6))
# plt.plot(x, data_cropped, label='Raw Data', color='blue', alpha=0.5)
# plt.plot(x, data_smoothed, label='Smoothed Data', color='green', linestyle='--')
# plt.plot(x, result.best_fit, label='Best Fit', color='red', linewidth=2)
#
# # --- Plot found peaks ---
# plt.scatter(peaks, data_smoothed[peaks], color='orange', marker='x', s=100, label='Detected Peaks')
#
# plt.xlabel("Index")
# plt.ylabel("Counts")
# plt.title("Fit with Envelope × Sum of Gaussians")
# plt.legend()
# plt.grid(True)
# plt.tight_layout()
# plt.show()
#
# # --- Print fit report ---
# print(result.fit_report())
#
#
#
#
#
# # '''
# # Fit data to a given fit function
# #
# # fix error
# # '''
# #
# # import numpy as np
# # import matplotlib.pyplot as plt
# # from lmfit import Model, Parameters
# #
# # file_path_CH0 = "../data-photon-counts-SiPM/test_data/20250402_pulse_height_vary/1_2V_20s/CH0@DT5720B_75_EspectrumR_test_fixed1_2V_20s_20250402_150738.txt"
# # file_path_CH1 = "../data-photon-counts-SiPM/test_data/20250402_pulse_height_vary/1_2V_20s/CH1@DT5720B_75_EspectrumR_test_fixed1_2V_20s_20250402_150738.txt"
# #
# #
# # # --- Load your data-photon-counts-SiPM ---
# # energies_CH1 = np.loadtxt(file_path_CH0)
# #   # One y value per line
# #
# #
# # energies_CH1_cropped = energies_CH1[:-3850]
# # x = np.arange(len(energies_CH1_cropped))            # x is index, assuming evenly spaced
# #
# # # --- Good peak indices (after visual inspection) ---
# # # You can replace this with your actual selected indices
# # good_peak_indices = [33, 65]  # example
# # mu_guesses = x[good_peak_indices]
# #
# # # --- Model: Envelope × Sum of Narrow Gaussians ---
# # def envelope_sum(x, mu_env, sigma_env, A_env, sigma_narrow, **kwargs):
# #     envelope = A_env * np.exp(- (x - mu_env)**2 / (2 * sigma_env**2))
# #     peak_sum = np.zeros_like(x)
# #     for key in kwargs:
# #         if key.startswith('A_'):
# #             i = key.split('_')[1]
# #             mu_i = kwargs[f'mu_{i}']
# #             A_i = kwargs[key]
# #             peak_sum += A_i * np.exp(- (x - mu_i)**2 / (2 * sigma_narrow**2))
# #     return envelope * peak_sum
# #
# # # --- Wrap in an lmfit Model ---
# # model = Model(envelope_sum, independent_vars=['x'])
# #
# # # --- Define Parameters ---
# # params = Parameters()
# # params.add('mu_env', value=np.mean(mu_guesses), min=0, max=len(x))
# # params.add('sigma_env', value=50, min=1, max=200)
# # params.add('A_env', value=1.0, min=0.1)
# #
# # params.add('sigma_narrow', value=3.0, min=0.5, max=20)
# #
# # for i, mu in enumerate(mu_guesses):
# #     params.add(f'mu_{i}', value=mu, vary=False)  # Fix peak positions
# #     params.add(f'A_{i}', value=1.0, min=0.0)     # Amplitude of each peak
# #
# # # --- Fit the model ---
# # result = model.fit(energies_CH1_cropped, params, x=x)
# #
# # # --- Plot results ---
# # plt.figure(figsize=(10, 5))
# # plt.plot(x, energies_CH1_cropped, 'o', markersize=3, label='Data', color='blue')
# # plt.plot(x, result.best_fit, 'r-.', label='Best Fit', color='red')
# # plt.xlabel("Index")
# # plt.ylabel("Value")
# # plt.title("LMFit: Envelope × Sum of Gaussians")
# # plt.legend()
# # plt.grid(True)
# # plt.tight_layout()
# # plt.show()
# #
# # # --- Optional: print fit report ---
# # print(result.fit_report())
