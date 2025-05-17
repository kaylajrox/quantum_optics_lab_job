import tkinter as tk
from tkinter import messagebox, filedialog
import subprocess
import os
import json

# Default values for parameters
DEFAULTS = {
    "gain_voltages_to_plot": "65.7",  # string, will parse to list of floats
    "crop_off_start": "0",
    "crop_off_end": "0",
    "counts_threshold": "10",
    "peak_spacing_threshold": "5",
    "sigma": "1.0",
    "manual_peak_indices": "",  # comma separated indices
}

def run_scripts(params):
    # Save params to a JSON config file, or export as env vars
    with open("params_config.json", "w") as f:
        json.dump(params, f)
    
    # Run your main plotting script, passing config path or params as needed
    # Example assuming plot-fit-peaks-SiPM-data.py reads params_config.json
    p1 = subprocess.run(["python", "plot-fit-peaks-SiPM-data.py"])
    
    if p1.returncode != 0:
        messagebox.showerror("Error", "plot-fit-peaks-SiPM-data.py failed.")
        return
    
    # Change directory for next scripts
    os.chdir("single-channel-analysis")
    
    p2 = subprocess.run(["python", "plot_index_vs_peak.py"])
    p3 = subprocess.run(["python", "plot_spacing_between_peaks.py"])
    
    if p2.returncode != 0 or p3.returncode != 0:
        messagebox.showerror("Error", "One of the single-channel-analysis scripts failed.")
        return
    
    messagebox.showinfo("Success", "All scripts ran successfully!")
    # Optionally open folder or files here for viewing
    os.startfile(os.getcwd())  # Opens the folder in File Explorer (Windows)

def on_submit():
    params = {}
    try:
        # parse and validate input values
        params["gain_voltages_to_plot"] = [float(x.strip()) for x in entry_gain.get().split(",") if x.strip()]
        params["crop_off_start"] = int(entry_crop_start.get())
        params["crop_off_end"] = int(entry_crop_end.get())
        params["counts_threshold"] = int(entry_counts_thresh.get())
        params["peak_spacing_threshold"] = int(entry_peak_spacing.get())
        params["sigma"] = float(entry_sigma.get())
        params["manual_peak_indices"] = [int(x.strip()) for x in entry_manual_peaks.get().split(",") if x.strip()]
    except Exception as e:
        messagebox.showerror("Input error", f"Invalid input: {e}")
        return
    
    run_scripts(params)

root = tk.Tk()
root.title("SiPM Data Plotter")

# Build form
tk.Label(root, text="Gain voltages to plot (comma-separated floats):").grid(row=0, column=0)
entry_gain = tk.Entry(root, width=40)
entry_gain.grid(row=0, column=1)
entry_gain.insert(0, DEFAULTS["gain_voltages_to_plot"])

tk.Label(root, text="Crop off start (int):").grid(row=1, column=0)
entry_crop_start = tk.Entry(root)
entry_crop_start.grid(row=1, column=1)
entry_crop_start.insert(0, DEFAULTS["crop_off_start"])

tk.Label(root, text="Crop off end (int):").grid(row=2, column=0)
entry_crop_end = tk.Entry(root)
entry_crop_end.grid(row=2, column=1)
entry_crop_end.insert(0, DEFAULTS["crop_off_end"])

tk.Label(root, text="Counts threshold (int):").grid(row=3, column=0)
entry_counts_thresh = tk.Entry(root)
entry_counts_thresh.grid(row=3, column=1)
entry_counts_thresh.insert(0, DEFAULTS["counts_threshold"])

tk.Label(root, text="Peak spacing threshold (int):").grid(row=4, column=0)
entry_peak_spacing = tk.Entry(root)
entry_peak_spacing.grid(row=4, column=1)
entry_peak_spacing.insert(0, DEFAULTS["peak_spacing_threshold"])

tk.Label(root, text="Sigma (float):").grid(row=5, column=0)
entry_sigma = tk.Entry(root)
entry_sigma.grid(row=5, column=1)
entry_sigma.insert(0, DEFAULTS["sigma"])

tk.Label(root, text="Manual peak indices (comma-separated ints):").grid(row=6, column=0)
entry_manual_peaks = tk.Entry(root)
entry_manual_peaks.grid(row=6, column=1)
entry_manual_peaks.insert(0, DEFAULTS["manual_peak_indices"])

# Submit button
submit_btn = tk.Button(root, text="Run Analysis", command=on_submit)
submit_btn.grid(row=7, column=0, columnspan=2, pady=10)

root.mainloop()
