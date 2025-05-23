# What's This Project For?

This project analyzes SiPM (Silicon Photomultiplier) photon count data from CoMPASS, a physics data acquisition system. We're looking for:

* Peaks in photon count curves, at different gain and pulse voltages.

* How those peaks shift, how far apart they are, and whether you can correlate signals across channels.

# How It's Organized

There are two main analysis types:

1. Single-Channel Analysis (focuses on one detector)

2. Coincidence Analysis (compares two detectors, looking at correlated events)

#️ What to Run — Step-by-Step

1. Setup the parameters in the main script

> `plot-fit-peaks-SiPM-data.py`

* data_dir = 'data-photon-counts-SiPM/20250428_more_light'	→ directory of data files 
* pulse_voltages_to_plot = [1.6]	→ only plots those pulse voltages
* gain_voltages_to_plot = [ 65.7]	→ only plots those gain voltages
* crop_off_start = 100	→ clean noisy start
* crop_off_end = 3000	→ clean noisy end
* vertical_lines = False	→ whether to have vertical lines
* counts_threshold = 100	→ tune peak detection
* peak_spacing_threshold = 16	→ tune peak detection
* sigma = 3.6	→ smoothness of curve
* pulse_color_map = {1.0: 'black', 1.1: 'darkblue', 1.3: 'green',1.6: 'orange', 2.0: 'deeppink', 2.3: 'red',} → 
* manual_peak_indices = {('CH0', 65.7, 1.6): [140, 178, 553, 590], ('CH1', 65.7, 1.6): [130, 177],} → force specific peaks to be counted if auto fails 

* data_by_channel = {"CH0": defaultdict(lambda: defaultdict(list)),                   "CH1": defaultdict(lambda: defaultdict(list))}pulse_by_voltage = defaultdict(lambda: defaultdict(float)) → 

2. Run plot_index_vs_peak_slope_spacing_table.py to generate the index vs peak data. This python file will plot the index vs peak data for each channel and save the plots in the folder "index_vs_peak_data_results". It will also save the data in a csv file in the same folder.

3. Run plot_spacing_between_peaks.py to generate the spacing vs peak data. This python file will plot the spacing vs peak data for each channel and save the plots in the folder "spacing_vs_peak_data_results". It will also save the data in a csv file in the same folder.


* Output:

	* Peak plots (for each channel)

	* CSV files with peak positions (in generated_peak_data_results/)

* What it does:

	* Reads in CoMPASS data

	* Smooths, crops, finds peaks

	* Plots curves and saves peak index data

# Optional: Dark vs Light Comparison

* Use script plot_light_vs_dark_counts_pulse_height_vary_gain_voltage_loop_subdirectory.py

* Needs folders with names like *_dark* and *_pulse_* for comparison

# Data Folder Naming Logic (Important!)

Each folder is named like:

> 65_7_gain_1_1_pulse_300s

The script extracts:

* Gain: 65.7 V

* Pulse Height: 1.1 V

* Duration: 300s

For coincidence measurements:

> peak4_and8_50ns_correlation_window_65_7_gain_1_6_pulse_60s_filtered

Extracts:

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
	
	* `plot_index_vs_peak_slope_spacing_table.py`

		* Reads peak data from `generated_peak_data_results`/

		* Plots peak index (x-axis) vs. peak number (y-axis)

		* Calculates slope of each curve (i.e., peak spacing trend)

	* `plot_spacing_between_peaks.py`

		* Also uses peak data

		* Shows how the spacing between peaks varies with peak number

		* This helps see if spacing is regular, how it changes with light/gain

	* Each creates:

		* Plots in its own folder (index_vs_peak_data_results/, etc.)

		* CSV files with calculated slopes or spacings