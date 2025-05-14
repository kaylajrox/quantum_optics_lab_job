# rate it moves out seems reasonable constant

# todo make the table

import pandas as pd
import matplotlib.pyplot as plt
import re

# === CONFIG ===
csv_path = "../weighted_means.csv"  # Adjust if needed
font_size = 16

# === LOAD AND PARSE CSV ===
df = pd.read_csv(csv_path)

# Extract second peak number from the Coincidence column
def extract_second_peak(coincidence_str):
    match = re.search(r"Peak \d+ and (\d+)", str(coincidence_str))
    return int(match.group(1)) if match else None

df["Second Peak Number"] = df["Coincidence"].apply(extract_second_peak)
df = df.dropna(subset=["Second Peak Number", "Weighted Mean Index", "State"])

# Separate by state
df_filtered = df[df["State"] == "filtered"].sort_values("Second Peak Number")
df_unfiltered = df[df["State"] == "unfiltered"].sort_values("Second Peak Number")

# === FILTERED PLOT ===
plt.figure(figsize=(10, 6))
plt.plot(df_filtered["Second Peak Number"], df_filtered["Weighted Mean Index"], 'o-', color='blue', label='Filtered', linewidth=2)
plt.xlabel("Peak Number", fontsize=font_size)
plt.ylabel("Weighted Mean Index", fontsize=font_size)
plt.title("Filtered: Weighted Mean Index vs. Second Peak Number", fontsize=font_size)
plt.grid(True)
plt.xticks(fontsize=font_size)
plt.yticks(fontsize=font_size)
plt.tight_layout()
plt.show()

# === UNFILTERED PLOT ===
plt.figure(figsize=(10, 6))
plt.plot(df_unfiltered["Second Peak Number"], df_unfiltered["Weighted Mean Index"], 's--', color='orange', label='Unfiltered', linewidth=2)
plt.xlabel("Peak Number", fontsize=font_size)
plt.ylabel("Weighted Mean Index", fontsize=font_size)
plt.title("Unfiltered: Weighted Mean Index vs. Second Peak Number", fontsize=font_size)
plt.grid(True)
plt.xticks(fontsize=font_size)
plt.yticks(fontsize=font_size)
plt.tight_layout()
plt.show()




# import pandas as pd
# import matplotlib.pyplot as plt
# import re
#
# # === CONFIG ===
# csv_path = "weighted_means2.csv"  # Adjust if needed
# font_size = 16
#
# # === LOAD AND PARSE CSV ===
# df = pd.read_csv(csv_path)
#
# # Extract second peak number
# def extract_second_peak(coincidence_str):
#     match = re.search(r"Peak \d+ and (\d+)", str(coincidence_str))
#     return int(match.group(1)) if match else None
#
# df["Second Peak Number"] = df["Coincidence"].apply(extract_second_peak)
# df = df.dropna(subset=["Second Peak Number", "Weighted Mean Index"])
#
# # === SORT DATA (optional) ===
# df = df.sort_values(by="Second Peak Number")
#
# # === PLOT ===
# plt.figure(figsize=(10, 6))
# plt.plot(df["Second Peak Number"], df["Weighted Mean Index"], 'o-', linewidth=2)
# plt.xlabel("Peak Number", fontsize=font_size)
# plt.ylabel("Weighted Mean Index", fontsize=font_size)
# plt.title("Weighted Mean Index vs. Second Peak Number", fontsize=font_size)
# plt.grid(True)
# plt.xticks(fontsize=font_size)
# plt.yticks(fontsize=font_size)
# plt.tight_layout()
# plt.show()
