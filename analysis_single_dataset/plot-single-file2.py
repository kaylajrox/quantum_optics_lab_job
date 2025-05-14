import matplotlib
matplotlib.use('TkAgg')  # For PyCharm interactivity

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

crop_start_amount = 100
crop_end_amount = 3000

# === USER CONFIGURATION ===
data_folder_name = "20250507_more_peaks_compare_coicdence"
data_folder_name2 = "20250507_baseline_data_for_coic_comparison"

# === PATH SETUP ===
repo_root = Path(__file__).resolve().parents[1]
data_dir1 = repo_root / "data-photon-counts-SiPM" / data_folder_name
data_dir2 = repo_root / "data-photon-counts-SiPM" / data_folder_name2

# === FILE GATHERING ===
filtered_subdirs = [d for d in data_dir1.rglob("*") if d.is_dir() and "filtered" in d.name]
raw_subdirs = [d for d in data_dir2.rglob("*") if d.is_dir()]

plot_groups = {"CH0_filtered": [], "CH1_filtered": [], "CH0_original": [], "CH1_original": []}

for subdir in filtered_subdirs:
    for file in subdir.glob("*.txt"):
        fname = file.name
        if fname.startswith("CH0@"): plot_groups["CH0_filtered"].append(file)
        elif fname.startswith("CH1@"): plot_groups["CH1_filtered"].append(file)

for subdir in raw_subdirs:
    for file in subdir.glob("*.txt"):
        fname = file.name
        if fname.startswith("CH0@"): plot_groups["CH0_original"].append(file)
        elif fname.startswith("CH1@"): plot_groups["CH1_original"].append(file)

# === PLOT CH0 ===
plt.figure(figsize=(10, 6))

for file in plot_groups["CH0_filtered"]:
    print(f"Loading CH0_filtered: {file.name}")
    data = np.loadtxt(file)
    data_cropped = data[crop_start_amount:-crop_end_amount]
    indices = np.arange(len(data_cropped))
    plt.plot(indices, data_cropped, lw=2, label=f"CH0 Filtered: {file.name}")

for file in plot_groups["CH0_original"]:
    print(f"Loading CH0_original: {file.name}")
    data = np.loadtxt(file)
    data_cropped = data[crop_start_amount:-crop_end_amount]
    indices = np.arange(len(data_cropped))
    plt.plot(indices, data_cropped, lw=2, linestyle='dashed', label=f"CH0 Original: {file.name}")

plt.xlabel("Index")
plt.ylabel("Value")
plt.title("CH0: Filtered and Original Data")
plt.grid(True)
plt.legend(fontsize=8)
plt.tight_layout()
plt.show()

# === PLOT CH1 ===
plt.figure(figsize=(10, 6))

for file in plot_groups["CH1_filtered"]:
    print(f"Loading CH1_filtered: {file.name}")
    data = np.loadtxt(file)
    data_cropped = data[crop_start_amount:-crop_end_amount]
    indices = np.arange(len(data_cropped))
    plt.plot(indices, data_cropped, lw=2, label=f"CH1 Filtered: {file.name}")

for file in plot_groups["CH1_original"]:
    print(f"Loading CH1_original: {file.name}")
    data = np.loadtxt(file)
    data_cropped = data[crop_start_amount:-crop_end_amount]
    indices = np.arange(len(data_cropped))
    plt.plot(indices, data_cropped, lw=2, linestyle='dashed', label=f"CH1 Original: {file.name}")

plt.xlabel("Index")
plt.ylabel("Value")
plt.title("CH1: Filtered and Original Data")
plt.grid(True)
plt.legend(fontsize=8)
plt.tight_layout()
plt.show()



# import matplotlib
# matplotlib.use('TkAgg')  # For PyCharm interactivity
#
# from pathlib import Path
# import numpy as np
# import matplotlib.pyplot as plt
#
# crop_start_amount = 100
# crop_end_amount = 3000
#
# # === USER CONFIGURATION ===
# data_folder_name = "20250507_more_peaks_compare_coicdence"
# data_folder_name2 = "20250507_baseline_data_for_coic_comparison"
#
# # === PATH SETUP ===
# repo_root = Path(__file__).resolve().parents[1]
# data_dir1 = repo_root / "data-photon-counts-SiPM" / data_folder_name
# data_dir2 = repo_root / "data-photon-counts-SiPM" / data_folder_name2
#
# # === FILE GATHERING ===
# filtered_subdirs = [d for d in data_dir1.rglob("*") if d.is_dir() and "filtered" in d.name]
# raw_subdirs = [d for d in data_dir2.rglob("*") if d.is_dir()]
#
# plot_groups = {
#     "CH0_filtered": [],
#     "CH1_filtered": [],
#     "CH0_original": [],
#     "CH1_original": []
# }
#
# for subdir in filtered_subdirs:
#     for file in subdir.glob("*.txt"):
#         fname = file.name
#         if fname.startswith("CH0@"): plot_groups["CH0_filtered"].append(file)
#         elif fname.startswith("CH1@"): plot_groups["CH1_filtered"].append(file)
#
# for subdir in raw_subdirs:
#     for file in subdir.glob("*.txt"):
#         fname = file.name
#         if fname.startswith("CH0@"): plot_groups["CH0_original"].append(file)
#         elif fname.startswith("CH1@"): plot_groups["CH1_original"].append(file)
#
# # === PLOT CH0 ===
# plt.figure(figsize=(10, 6))
# for label, files in {k: v for k, v in plot_groups.items() if k.startswith("CH0")}.items():
#     for file in files:
#         print(f"Loading {label}: {file.name}")
#         data = np.loadtxt(file)
#         data_cropped = data[crop_start_amount:-crop_end_amount]
#         indices = np.arange(len(data_cropped))
#         plt.plot(indices, data_cropped, lw=2, label=f"{label}: {file.name}")
# plt.xlabel("Index")
# plt.ylabel("Counts")
# plt.title("CH0 Filtered and Original Data")
# plt.grid(True)
# plt.legend(fontsize=8)
# plt.tight_layout()
# plt.show()
#
# # === PLOT CH1 ===
# plt.figure(figsize=(10, 6))
# for label, files in {k: v for k, v in plot_groups.items() if k.startswith("CH1")}.items():
#     for file in files:
#         print(f"Loading {label}: {file.name}")
#         data = np.loadtxt(file)
#         data_cropped = data[crop_start_amount:-crop_end_amount]
#         indices = np.arange(len(data_cropped))
#         plt.plot(indices, data_cropped, lw=2, label=f"{label}: {file.name}")
# plt.xlabel("Index")
# plt.ylabel("Counts")
# plt.title("CH1 Filtered and Original Data")
# plt.grid(True)
# plt.legend(fontsize=8)
# plt.tight_layout()
# plt.show()
#
# # import matplotlib
# # matplotlib.use('TkAgg')  # For PyCharm interactivity
# #
# # from pathlib import Path
# # import numpy as np
# # import matplotlib.pyplot as plt
# #
# # crop_start_amount = 100
# # crop_end_amount = 3000
# #
# # # === USER CONFIGURATION ===
# # data_folder_name = "20250507_more_peaks_compare_coicdence"
# # data_folder_name2 = "20250507_baseline_data_for_coic_comparison"
# #
# # # === PATH SETUP ===
# # repo_root = Path(__file__).resolve().parents[1]
# # data_dir1 = repo_root / "data-photon-counts-SiPM" / data_folder_name
# # data_dir2 = repo_root / "data-photon-counts-SiPM" / data_folder_name2
# #
# # # === FILE GATHERING ===
# # filtered_subdirs = [d for d in data_dir1.rglob("*") if d.is_dir() and "filtered" in d.name]
# # raw_subdirs = [d for d in data_dir2.rglob("*") if d.is_dir()]
# #
# # plot_groups = {"CH0_filtered": [], "CH1_filtered": [], "AddBack_filtered": [], "CH0_original": [], "CH1_original": []}
# #
# # for subdir in filtered_subdirs:
# #     for file in subdir.glob("*.txt"):
# #         fname = file.name
# #         if fname.startswith("CH0@"): plot_groups["CH0_filtered"].append(file)
# #         elif fname.startswith("CH1@"): plot_groups["CH1_filtered"].append(file)
# #         elif fname.startswith("0@AddBack"): plot_groups["AddBack_filtered"].append(file)
# #
# # for subdir in raw_subdirs:
# #     for file in subdir.glob("*.txt"):
# #         fname = file.name
# #         if fname.startswith("CH0@"): plot_groups["CH0_original"].append(file)
# #         elif fname.startswith("CH1@"): plot_groups["CH1_original"].append(file)
# #
# # # === PLOTTING ===
# # plt.figure(figsize=(10, 6))
# #
# # for label, files in plot_groups.items():
# #     for file in files:
# #         print(f"Loading {label}: {file.name}")
# #         data = np.loadtxt(file)
# #         data_cropped = data[crop_start_amount:-crop_end_amount]
# #         indices = np.arange(len(data_cropped))
# #         plt.plot(indices, data_cropped, lw=2, label=f"{label}: {file.name}")
# #
# # plt.xlabel("Index")
# # plt.ylabel("Value")
# # plt.title("All CH0/CH1/AddBack Filtered and Original Data")
# # plt.grid(True)
# # plt.legend(fontsize=8)
# # plt.tight_layout()
# # plt.show()
# #
# #
# #
# # # # see what single file looks like
# # #
# # # import matplotlib
# # # matplotlib.use('TkAgg')  # For PyCharm interactivity
# # #
# # # from pathlib import Path
# # # import numpy as np
# # # import matplotlib.pyplot as plt
# # #
# # # crop_start_amount = 100
# # # crop_end_amount = 3000
# # #
# # # # === USER CONFIGURATION ===
# # # data_folder_name = "20250507_more_peaks_compare_coicdence"
# # # data_folder_name2 = "20250507_baseline_data_for_coic_comparison"
# # # filename2 = "CH0@DT5720B_75_EspectrumF_peak_4_and4_750_ns_20250507_151921.txt"
# # # filename3 = "0@AddBack_EspectrumF_peak_4_and4_750_ns_20250507_151921.txt"
# # # filename = "CH1@DT5720B_75_EspectrumF_peak_4_and4_750_ns_20250507_151921.txt"
# # #
# # # filename4 = "CH0@DT5720B_75_EspectrumR_65_7_gain_1_6V_pulse_60s_05_20250507_145259.txt"
# # # filename5 = "CH1@DT5720B_75_EspectrumR_65_7_gain_1_6V_pulse_60s_05_20250507_145259.txt"
# # # subfolder_name = "peak4_and4_750ns_correlation_window_65_7_gain_1_6_pulse_60s_filtered"
# # # subfolder_name2 = "65_7_gain_1_6_pulse_60s"
# # # subfolder_name3= "peak4_and6_750ns_correlation_window_65_7_gain_1_6_pulse_60s_filtered"
# # # subfolder_name6= "peak4_and6_750ns_correlation_window_65_7_gain_1_6_pulse_60s_filtered"
# # # filename6 = "CH0@DT5720B_75_EspectrumF_peak_4_and6_750_ns_20250507_151556.txt"
# # #
# # # # === PATH SETUP ===
# # # repo_root = Path(__file__).resolve().parents[1]
# # # base_data_dir = repo_root / "data-photon-counts-SiPM" / data_folder_name
# # # base_data_dir2 = repo_root / "data-photon-counts-SiPM" / data_folder_name2
# # # base_data_dir3 = repo_root / "data-photon-counts-SiPM" / data_folder_name
# # # subfolder_path = base_data_dir / subfolder_name
# # # subfolder_path2 = base_data_dir2 / subfolder_name2
# # # subfolder_path3 = base_data_dir2 / subfolder_name3
# # # subfolder_path6 = base_data_dir / subfolder_path
# # # file_path = subfolder_path / filename
# # # file_path2 = subfolder_path / filename2
# # # file_path3 = subfolder_path / filename3
# # # file_path4 = subfolder_path2 / filename4
# # # file_path5 = subfolder_path2 / filename5
# # # file_path6 = subfolder_path6 / filename6
# # #
# # # # === LOAD DATA ===
# # # print(f"Loading from: {file_path}")
# # # assert file_path.exists(), f"File not found: {file_path}"
# # # data = np.loadtxt(file_path)
# # #
# # # # === LOAD DATA 2 ===
# # # print(f"Loading from: {file_path2}")
# # # assert file_path2.exists(), f"File not found: {file_path2}"
# # # data2 = np.loadtxt(file_path2)
# # #
# # # # === LOAD DATA 3 ===
# # # print(f"Loading from: {file_path3}")
# # # assert file_path2.exists(), f"File not found: {file_path3}"
# # # data3 = np.loadtxt(file_path3)
# # #
# # # # === LOAD DATA 4 ===
# # # print(f"Loading from: {file_path4}")
# # # assert file_path2.exists(), f"File not found: {file_path4}"
# # # data4 = np.loadtxt(file_path4)
# # #
# # # # === LOAD DATA 5 ===
# # # print(f"Loading from: {file_path5}")
# # # assert file_path2.exists(), f"File not found: {file_path5}"
# # # data5 = np.loadtxt(file_path5)
# # #
# # # # === LOAD DATA 6 ===
# # # print(f"Loading from: {file_path6}")
# # # assert file_path2.exists(), f"File not found: {file_path6}"
# # # data6 = np.loadtxt(file_path6)
# # #
# # # # === CROP DATA ===
# # # # Crop data and generate matching index array
# # # data_cropped = data[crop_start_amount:-crop_end_amount]
# # # indices = np.arange(len(data_cropped))
# # # # === CROP DATA ===
# # # # Crop data and generate matching index array
# # # data_cropped2 = data2[crop_start_amount:-crop_end_amount]
# # # indices2 = np.arange(len(data_cropped2))
# # #
# # # # === CROP DATA 3 ===
# # # # Crop data and generate matching index array
# # # data_cropped3 = data3[crop_start_amount:-crop_end_amount]
# # # indices3 = np.arange(len(data_cropped3))
# # #
# # # # === CROP DATA 4 ===
# # # # Crop data and generate matching index array
# # # data_cropped4 = data4[crop_start_amount:-crop_end_amount]
# # # indices4 = np.arange(len(data_cropped4))
# # #
# # # # === CROP DATA 5 ===
# # # # Crop data and generate matching index array
# # # data_cropped5 = data5[crop_start_amount:-crop_end_amount]
# # # indices5 = np.arange(len(data_cropped5))
# # #
# # #
# # # # === CROP DATA 6 ===
# # # # Crop data and generate matching index array
# # # data_cropped6 = data6[crop_start_amount:-crop_end_amount]
# # # indices6 = np.arange(len(data_cropped6))
# # #
# # # # === PLOT ===
# # # plt.figure(figsize=(10, 6))
# # # plt.plot(indices, data_cropped, lw=2,label="CH1 - peak 4 and 4")
# # # plt.plot(indices, data_cropped2, lw=2,label="CH0- peak 4 and 4")
# # # plt.plot(indices6, data_cropped6, lw=2,label="CH0- peak 4 and 6")
# # # plt.plot(indices, data_cropped3, lw=2,label="AddBack - peak 4 and 4")
# # # plt.plot(indices4, data_cropped4, lw=2,label="CH0 original")
# # # plt.plot(indices5, data_cropped5, lw=2,label="CH1 original")
# # # plt.xlabel("Index")
# # # plt.ylabel("Value")
# # # plt.title(f"Cropped Plot of {filename}")
# # # plt.grid(True)
# # # plt.legend()
# # # plt.tight_layout()
# # # plt.show()
# # #
# # #
# # #
