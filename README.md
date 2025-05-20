# What's This Project For?

This project analyzes SiPM (Silicon Photomultiplier) photon count data from CoMPASS, a physics data acquisition system. You're looking for:

* Peaks in photon count curves, at different gain and pulse voltages.

* How those peaks shift, how far apart they are, and whether you can correlate signals across channels.

# How It's Organized

There are two main analysis types:

1. Single-Channel Analysis (focuses on one detector)

2. Coincidence Analysis (compares two detectors, looking at correlated events)

#️ What to Run — Step-by-Step

1. Run the Main Script

> `run_analysis_gui.py`

* Input: 
	
	* `gain_voltages_to_plot` = [65.7] → only plots those gain voltages

	* `crop_off_start`, crop_off_end → clean noisy start/end

	* `counts_threshold`, `peak_spacing_threshold` → tune peak detection

	* `sigma` → smoothness of curve

	* `manual_peak_indices` → force specific peaks to be counted if auto fails

* Output:

	* Peak plots (for each channel)

	* CSV files with peak positions (in generated_peak_data_results/)

* What it does:

	* Reads in CoMPASS data

	* Smooths, crops, finds peaks

	* Plots curves and saves peak index data

* Before running:

	* Make sure `generated_peak_data_results`/ is empty (delete old files first)

	* Set correct data_dir in the script (e.g., '20250428_more_light')

	* You can tweak smoothing, peak threshold, etc.
	


# Optional: Dark vs Light Comparison

* Use script plot_light_vs_dark_counts_pulse_height_vary_gain_voltage_loop_subdirectory.py

* Needs folders with names like *_dark* and *_pulse_* for comparison

# Data Folder Naming Logic (Important!)

Each folder is named like:

> 65_7_gain_1_1_pulse_300s

You can extract:

* Gain: 65.7 V

* Pulse Height: 1.1 V

* Duration: 300s

For coincidence measurements:

> peak4_and8_50ns_correlation_window_65_7_gain_1_6_pulse_60s_filtered

You can extract:

* Peaks: 4 (main) and 8 (comparison)

* Correlation window: 50 ns

* Whether it's filtered or raw

* Same info about gain/pulse



# Common Issues

* Don't forget to delete old files in generated_peak_data_results/ before rerunning.

* Wrong folder path = no data found. Make sure data_dir is correct.

* Make sure each run folder inside data-photon-counts-SiPM/ is well-formed (naming conventions matter).


# Script Descriptions 
	
In single-channel-analysis:
	
	* `plot_index_vs_peak.py`

		* Reads peak data from `generated_peak_data_results`/

		* Plots peak index (x-axis) vs. peak number (y-axis)

		* Calculates slope of each curve (i.e., peak spacing trend)

	* `spacing_between_peaks`.py

		* Also uses peak data

		* Shows how the spacing between peaks varies with peak number

		* This helps see if spacing is regular, how it changes with light/gain

	* Each creates:

		* Plots in its own folder (index_vs_peak_data_results/, etc.)

		* CSV files with calculated slopes or spacings