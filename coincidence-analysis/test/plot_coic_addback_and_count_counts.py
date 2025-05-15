from datetime import datetime
from pathlib import Path
import csv
import numpy as np

# Simulated file group structure
simulated_data_entries = [
    ("peak_1_and2_750ns_filtered.txt", np.random.poisson(lam=20, size=5000)),
    ("peak_1_and3_750ns_filtered.txt", np.random.poisson(lam=25, size=5000)),
    ("peak_1_and4_750ns_unfiltered.txt", np.random.poisson(lam=30, size=5000)),
]

crop_start_amount = 100
crop_end_amount = 3000
timestamp_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Prepare CSV data
csv_rows = [["Timestamp", "File", "Second Peak", "Correlation Time", "Total Counts"]]

for filename, y_values in simulated_data_entries:
    parts = filename.split("_")
    second_peak = parts[2].replace("and", "")
    correlation_time = parts[3].replace("ns", "")

    # Crop and sum
    cropped = y_values[crop_start_amount:-crop_end_amount]
    total_counts = int(np.sum(cropped))

    csv_rows.append([timestamp_now, filename, second_peak, correlation_time, total_counts])

# Save to CSV
output_path = Path.cwd() / "find_counts.csv"
with open(output_path, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(csv_rows)

output_path.name



# from pathlib import Path
# import csv
# import numpy as np
#
# # Simulated file group structure for demonstration:
# # Each entry is a tuple: (filename, y-values list)
# simulated_data_entries = [
#     ("peak_1_and2_750ns_filtered.txt", np.random.poisson(lam=20, size=5000)),
#     ("peak_1_and3_750ns_filtered.txt", np.random.poisson(lam=25, size=5000)),
#     ("peak_1_and4_750ns_unfiltered.txt", np.random.poisson(lam=30, size=5000)),
# ]
#
# crop_start_amount = 100
# crop_end_amount = 3000
#
# # Prepare CSV data
# csv_rows = [["File", "Second Peak", "Correlation Time", "Total Counts"]]
#
# for filename, y_values in simulated_data_entries:
#     # Extract metadata from filename
#     parts = filename.split("_")
#     second_peak = parts[2].replace("and", "")
#     correlation_time = parts[3].replace("ns", "")
#
#     # Crop the data
#     cropped = y_values[crop_start_amount:-crop_end_amount]
#     total_counts = int(np.sum(cropped))
#
#     csv_rows.append([filename, second_peak, correlation_time, total_counts])
#
# # Save to CSV
# output_path = Path.cwd() / "find_counts.csv"
# with open(output_path, "w", newline="") as f:
#     writer = csv.writer(f)
#     writer.writerows(csv_rows)
#
# output_path.name
#
#
#
# # from pathlib import Path
# # import csv
# # import numpy as np
# #
# # # Simulate example y-values (this would come from the real plot's data)
# # # For demo, let's assume a single dataset
# # simulated_y_data = np.random.poisson(lam=20, size=5000)
# # crop_start_amount = 100
# # crop_end_amount = 3000
# #
# # # Crop the data
# # cropped_data = simulated_y_data[crop_start_amount:-crop_end_amount]
# #
# # # Compute total counts
# # total_counts = sum(cropped_data)
# #
# # # Set output path
# # output_csv_path = Path.cwd() / "find_counts.csv"
# #
# # # Write to CSV
# # with open(output_csv_path, 'w', newline='') as f:
# #     writer = csv.writer(f)
# #     writer.writerow(["Index", "Counts"])
# #     for idx, y in enumerate(cropped_data):
# #         writer.writerow([idx, y])
# #     writer.writerow([])
# #     writer.writerow(["Total Counts", total_counts])
# #
# # output_csv_path.name
