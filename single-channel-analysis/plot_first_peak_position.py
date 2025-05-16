import matplotlib
matplotlib.use('TkAgg')  # For PyCharm interactivity

from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Crop-off setting
crop_off = 0

# ✅ Custom pulse color map
pulse_color_map = {
    1.0: 'black',
    1.1: 'darkblue',
    1.3: 'green',
    1.6: 'orange',
    2.0: 'deeppink',
    2.3: 'red',
}

# ✅ Dynamically resolve repo root
script_path = Path(__file__).resolve()
repo_root = script_path.parents[1]  # quantum_optics_lab_job/

# ✅ Paths
summary_csv_path = repo_root / 'results-from-generated-data' / 'results_first_peaks_summary.csv'
output_csv_path = summary_csv_path  # Overwrite original
backup_csv_path = repo_root / 'results-from-generated-data' / f'results_first_peaks_summary_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

# ✅ Load CSV with error handling
if not summary_csv_path.exists():
    raise FileNotFoundError(f"CSV file not found at: {summary_csv_path}")

summary_df = pd.read_csv(summary_csv_path)

# ✅ Sort for consistent plotting
summary_df = summary_df.sort_values(
    by=['Channel (from filename)', 'Pulse Height (from filename)', 'Gain Voltage (from filename)']
)

# ✅ Add timestamp column
current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
summary_df['Timestamp'] = current_time

# ✅ Reorder columns to put Timestamp first
cols = ['Timestamp'] + [col for col in summary_df.columns if col != 'Timestamp']
summary_df = summary_df[cols]

# ✅ Save updated CSV (overwrite) and also backup timestamped version
summary_df.to_csv(output_csv_path, index=False)
summary_df.to_csv(backup_csv_path, index=False)
print(f"✅ Updated CSV saved to: {output_csv_path}")
print(f"🗄️ Backup CSV saved to: {backup_csv_path}")

# ✅ Prepare plots directory
plots_dir = repo_root / 'plots' / 'first_peak_vs_gain'
plots_dir.mkdir(parents=True, exist_ok=True)

# ✅ Get all unique pulses for color coding
all_pulses = sorted(summary_df['Pulse Height (from filename)'].unique())

# ✅ Plot for each channel
for channel in summary_df['Channel (from filename)'].unique():
    plt.figure(figsize=(8, 6))

    for pulse in all_pulses:
        filtered = summary_df[
            (summary_df['Channel (from filename)'] == channel) &
            (summary_df['Pulse Height (from filename)'] == pulse)
        ]

        if crop_off > 0:
            filtered = filtered.iloc[:-crop_off]

        if not filtered.empty:
            color = pulse_color_map.get(pulse, 'gray')  # fallback to gray if unknown pulse
            plt.plot(
                filtered['Gain Voltage (from filename)'],
                filtered['Peak Index'],
                marker='o',
                linestyle='-',
                label=f'{pulse}V Pulse',
                color=color
            )

    plt.title(f'First Peak Index vs. Gain Voltage ({channel})')
    plt.xlabel('Gain Voltage (V)')
    plt.ylabel('Peak 1 Index')
    plt.grid(True)
    plt.legend(title='Pulse Height')
    plt.tight_layout()

    # ✅ Save the plot
    plot_file = plots_dir / f'{channel}_first_peak_vs_gain.png'
    plt.savefig(plot_file)
    print(f"📊 Plot saved to: {plot_file}")

    # Optional: Show interactively (comment out if batch running)
    plt.show()


# import matplotlib
# matplotlib.use('TkAgg')  # For PyCharm interactivity
#
# from datetime import datetime
# import pandas as pd
# import matplotlib.pyplot as plt
# from pathlib import Path
#
# # Crop-off setting
# crop_off = 0
#
# # ✅ Your custom pulse color map
# pulse_color_map = {
#     1.0: 'black',
#     1.1: 'darkblue',
#     1.3: 'green',
#     1.6: 'orange',
#     2.0: 'deeppink',
#     2.3: 'red',
# }
#
# # ✅ Dynamically resolve paths relative to repo root
# script_path = Path(__file__).resolve()
# repo_root = script_path.parents[1]  # Go up to repo root level
#
# # ✅ Correct path to your CSV inside 'results-from-generated-data' subdirectory
# summary_csv_path = repo_root / 'results-from-generated-data' / 'results_first_peaks_summary.csv'
# output_csv_path = summary_csv_path  # overwriting same file
#
# # ✅ Load the summary CSV
# if not summary_csv_path.exists():
#     raise FileNotFoundError(f"CSV file not found at: {summary_csv_path}")
#
# summary_df = pd.read_csv(summary_csv_path)
#
#
# # # ✅ Dynamically resolve paths relative to repo root
# # script_path = Path(__file__).resolve()
# # repo_root = script_path.parents[1]  # Go up to repo root level
# #
# # summary_csv_path = repo_root / 'results_first_peaks_summary.csv'
# # output_csv_path = repo_root / 'results_first_peaks_summary.csv'  # Same file (overwrite)
# #
# # # ✅ Load the summary CSV
# # if not summary_csv_path.exists():
# #     raise FileNotFoundError(f"CSV file not found at: {summary_csv_path}")
# #
# # summary_df = pd.read_csv(summary_csv_path)
#
# # Sort for consistent plotting
# summary_df = summary_df.sort_values(
#     by=['Channel (from filename)', 'Pulse Height (from filename)', 'Gain Voltage (from filename)']
# )
#
# # Add timestamp
# current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
# summary_df['Timestamp'] = current_time
#
# # ✅ Reorder columns to place Timestamp first
# cols = ['Timestamp'] + [col for col in summary_df.columns if col != 'Timestamp']
# summary_df = summary_df[cols]
#
# # ✅ Save updated table
# summary_df.to_csv(output_csv_path, index=False)
# print(f"✅ Saved updated summary with timestamp to: {output_csv_path}")
#
# # Detect all pulse heights
# all_pulses = sorted(summary_df['Pulse Height (from filename)'].unique())
#
# # Plot for each channel
# for channel in summary_df['Channel (from filename)'].unique():
#     plt.figure(figsize=(8, 6))
#
#     for pulse in all_pulses:
#         filtered = summary_df[
#             (summary_df['Channel (from filename)'] == channel) &
#             (summary_df['Pulse Height (from filename)'] == pulse)
#         ]
#
#         if crop_off > 0:
#             filtered = filtered.iloc[:-crop_off]
#
#         if not filtered.empty:
#             color = pulse_color_map.get(pulse, 'gray')  # fallback to gray if not in map
#             plt.plot(
#                 filtered['Gain Voltage (from filename)'],
#                 filtered['Peak Index'],
#                 marker='o',
#                 linestyle='-',
#                 label=f'{pulse}V Pulse',
#                 color=color
#             )
#
#     plt.title(f'First Peak Index vs. Gain Voltage ({channel})')
#     plt.xlabel('Gain Voltage (V)')
#     plt.ylabel('Peak 1 Index')
#     plt.grid(True)
#     plt.legend(title='Pulse Height')
#     plt.tight_layout()
#     plt.show()
#
#
#
# # import matplotlib
# # matplotlib.use('TkAgg')  # For PyCharm interactivity
# #
# # from datetime import datetime
# # import pandas as pd
# # import matplotlib.pyplot as plt
# #
# # # Crop-off setting
# # crop_off = 0
# #
# # # ✅ Your custom pulse color map
# # pulse_color_map = {
# #     1.0: 'black',
# #     1.1: 'darkblue',
# #     1.3: 'green',
# #     1.6: 'orange',
# #     2.0: 'deeppink',
# #     2.3: 'red',
# # }
# #
# # # Load the summary CSV
# # summary_df = pd.read_csv('../results_first_peaks_summary.csv')
# #
# # # Sort for consistent plotting
# # summary_df = summary_df.sort_values(
# #     by=['Channel (from filename)', 'Pulse Height (from filename)', 'Gain Voltage (from filename)']
# # )
# #
# # # Add timestamp
# # current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
# # summary_df['Timestamp'] = current_time
# #
# # # ✅ Reorder columns to place Timestamp first
# # cols = ['Timestamp'] + [col for col in summary_df.columns if col != 'Timestamp']
# # summary_df = summary_df[cols]
# #
# # # ✅ Save updated table
# # summary_df.to_csv('results_first_peaks_summary.csv', index=False)
# # print("✅ Saved updated summary with timestamp as first column.")
# #
# # # Detect all pulse heights
# # all_pulses = sorted(summary_df['Pulse Height (from filename)'].unique())
# #
# # # Plot for each channel
# # for channel in summary_df['Channel (from filename)'].unique():
# #     plt.figure(figsize=(8, 6))
# #
# #     for pulse in all_pulses:
# #         filtered = summary_df[
# #             (summary_df['Channel (from filename)'] == channel) &
# #             (summary_df['Pulse Height (from filename)'] == pulse)
# #         ]
# #
# #         if crop_off > 0:
# #             filtered = filtered.iloc[:-crop_off]
# #
# #         if not filtered.empty:
# #             color = pulse_color_map.get(pulse, 'gray')  # fallback to gray if not in map
# #             plt.plot(
# #                 filtered['Gain Voltage (from filename)'],
# #                 filtered['Peak Index'],
# #                 marker='o',
# #                 linestyle='-',
# #                 label=f'{pulse}V Pulse',
# #                 color=color
# #             )
# #
# #     plt.title(f'First Peak Index vs. Gain Voltage ({channel})')
# #     plt.xlabel('Gain Voltage (V)')
# #     plt.ylabel('Peak 1 Index')
# #     plt.grid(True)
# #     plt.legend(title='Pulse Height')
# #     plt.tight_layout()
# #     plt.show()
