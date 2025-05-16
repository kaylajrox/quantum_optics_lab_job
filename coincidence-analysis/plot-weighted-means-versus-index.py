#TODO check index and data, looks weird now


import matplotlib
matplotlib.use('TkAgg')  # For PyCharm interactivity

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from datetime import datetime

font_size = 24
offset_filtered = 20
font_height_unfiltered = 0.025
text_fontsize = 18
title_filtered = "Filtered: Mean Index versus CH1 Peak Index"
title_unfiltered = "Unfiltered: Mean Index versus CH1 Peak Index"
y_axis_label = "Weighted Mean Index"
x_axis_label = "CH1 Peak Number"

# Load the CSV
df = pd.read_csv("./weighted_means.csv")

# Filter by state
df_filtered = df[df['State'] == 'filtered'].reset_index(drop=True)
df_unfiltered = df[df['State'] == 'unfiltered'].reset_index(drop=True)

print(df_filtered)
# ===================== FILTERED PLOT =====================

import numpy as np

# ===================== FILTERED PLOT =====================
plt.figure(figsize=(10, 6))

x_vals = df_filtered.index.values + 2  # start from peak 2 (no data for 1)
y_vals = df_filtered['Weighted Mean Time'].values

# Plot the data
plt.plot(x_vals, y_vals, 'o-', color='blue', linewidth=3)

# Fit line
slope, intercept = np.polyfit(x_vals, y_vals, 1)
fit_line = slope * x_vals + intercept
plt.plot(x_vals, fit_line, 'r--', linewidth=2, label='Linear Fit')

# Equation display
equation_text = f"y = {slope:.2f}x + {intercept:.2f}"
plt.text(0.05, 0.75, equation_text, transform=plt.gca().transAxes,
         fontsize=text_fontsize, color='red', ha='left', va='top')

# Annotate each point with shifted x-value
for i, y in enumerate(y_vals):
    peak_number = i + 1
    offset = -offset_filtered if i == len(y_vals) - 1 else offset_filtered
    va = 'top' if i == len(y_vals) - 1 else 'bottom'
    plt.text(peak_number+1, y + offset, f"{y:.2f}", ha='center', va=va,
             fontsize=text_fontsize, color='blue')

plt.xlabel(x_axis_label, fontsize=font_size)
plt.ylabel(y_axis_label, fontsize=font_size)
plt.title(title_filtered, fontsize=font_size)
plt.tick_params(axis='x', labelsize=font_size)
plt.tick_params(axis='y', labelsize=font_size)
plt.grid(True)
plt.tight_layout()
plt.legend()
plt.show()

# ===================== UNFILTERED PLOT =====================
plt.figure(figsize=(10, 6))
plt.plot(
    df_unfiltered.index+1,
    df_unfiltered['Weighted Mean Time'],
    's--', color='orange', linewidth=3
)

previous_y = None
for i, y in enumerate(df_unfiltered['Weighted Mean Time']):
    if i == len(df_unfiltered) - 1:
        offset = -font_height_unfiltered
        va = 'top'
    else:
        offset = font_height_unfiltered
        va = 'bottom'
        if previous_y is not None and abs((y + offset) - previous_y) < font_height_unfiltered * 2:
            offset = -font_height_unfiltered
            va = 'top'

    plt.text(i+1, y + offset, f"{y:.2f}", ha='center', va=va, fontsize=text_fontsize, color='orange')
    previous_y = y + offset

plt.xlabel(x_axis_label, fontsize=font_size)
plt.ylabel(y_axis_label, fontsize=font_size)
plt.title(title_unfiltered, fontsize=font_size)
plt.tick_params(axis='x', labelsize=font_size)
plt.tick_params(axis='y', labelsize=font_size)
plt.grid(True)
plt.tight_layout()
plt.show()



# '''
# This script requires the weighted_means.csv file to be created by plot-coic_addback.py.
# '''
#
#
#
# import matplotlib
#
# matplotlib.use('TkAgg')  # For PyCharm interactivity
#
# import pandas as pd
# import matplotlib.pyplot as plt
# import matplotlib.ticker as ticker
#
# font_size = 24
# offset_filtered = 20
# font_height_unfiltered = 0.025  # vertical threshold to check overlap (in y-units)
# text_fontsize = 15
# title_filtered = "Filtered: Weighted Mean of Peak Coicidence Position"
# title_unfiltered = "Unfiltered: Weighted Mean of Peak Coicidence Position"
# y_axis_label = "Weighted Mean"
# x_axis_label = "Index of Weighted Mean"
#
# # Load the weighted means CSV
# df = pd.read_csv("./weighted_means.csv")
#
# # Separate filtered and unfiltered data
# df_filtered = df[df['State'] == 'filtered'].sort_values(by='Weighted Mean Index')
# df_unfiltered = df[df['State'] == 'unfiltered'].sort_values(by='Weighted Mean Index')
#
# # ===================== FILTERED PLOT =====================
# plt.figure(figsize=(10, 6))
# plt.plot(
#     df_filtered['Weighted Mean Index'],
#     df_filtered['Weighted Mean Time'],
#     'o-', color='blue', linewidth=3
# )
#
# # Annotate each point in the filtered dataset
# for i, (x, y) in enumerate(zip(df_filtered['Weighted Mean Index'], df_filtered['Weighted Mean Time'])):
#     offset = -offset_filtered if i == len(df_filtered) - 1 else offset_filtered
#     va = 'top' if i == len(df_filtered) - 1 else 'bottom'
#     plt.text(x, y + offset, f"{y:.2f}", ha='center', va=va, fontsize=text_fontsize, color='blue')
#
# plt.xlabel(x_axis_label, fontsize=font_size)
# plt.ylabel(y_axis_label, fontsize=font_size)
# plt.title(title_filtered, fontsize=font_size)
# plt.tick_params(axis='x', labelsize=font_size)
# plt.tick_params(axis='y', labelsize=font_size)
# plt.grid(True)
# plt.gca().xaxis.set_major_formatter(ticker.FormatStrFormatter('%.1f'))
# plt.tight_layout()
# plt.show()
#
# # ===================== UNFILTERED PLOT =====================
# plt.figure(figsize=(10, 6))
# plt.plot(
#     df_unfiltered['Weighted Mean Index'],
#     df_unfiltered['Weighted Mean Time'],
#     's--', color='orange', linewidth=3
# )
#
# # Annotate each point in the unfiltered dataset with smart offset
# previous_y = None
# for i, (x, y) in enumerate(zip(df_unfiltered['Weighted Mean Index'], df_unfiltered['Weighted Mean Time'])):
#     # Always flip the last point down
#     if i == len(df_unfiltered) - 1:
#         offset = -font_height_unfiltered
#         va = 'top'
#     else:
#         # Default offset
#         offset = font_height_unfiltered
#         va = 'bottom'
#         # Flip if too close to the previous label
#         if previous_y is not None and abs((y + offset) - previous_y) < font_height_unfiltered * 2:
#             offset = -font_height_unfiltered
#             va = 'top'
#
#     plt.text(x, y + offset, f"{y:.2f}", ha='center', va=va, fontsize=text_fontsize, color='orange')
#     previous_y = y + offset
#
# plt.xlabel(x_axis_label, fontsize=font_size)
# plt.ylabel(y_axis_label, fontsize=font_size)
# plt.title(title_unfiltered, fontsize=font_size)
# plt.tick_params(axis='x', labelsize=font_size)
# plt.tick_params(axis='y', labelsize=font_size)
# plt.grid(True)
# plt.gca().xaxis.set_major_formatter(ticker.FormatStrFormatter('%.1f'))
# plt.tight_layout()
# plt.show()
