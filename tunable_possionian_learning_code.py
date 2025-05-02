'''
Fits peaks of narrow gaussians to a Poisson distribution along with the poisson envelope. Used an interpolation between points
to get the envelope smooth.
'''
import matplotlib
matplotlib.use('TkAgg')  # For PyCharm interactivity

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from scipy.stats import poisson
from scipy.interpolate import interp1d


# --- X domain and default parameters ---
x = np.linspace(0, 15, 1000)

# Narrow Gaussian parameters
narrow_sigma = 0.3
max_gaussians = 15
n_gauss_init = 5

center_init = 7.5
spacing_init = 1.0
lambda_init = 5.0  # Poisson λ (mean)

# --- Gaussian function ---
def gaussian(x, mu, sigma, A):
    return A * np.exp(- (x - mu) ** 2 / (2 * sigma ** 2))

# --- Setup plot ---
fig, ax = plt.subplots(figsize=(10, 6))
plt.subplots_adjust(left=0.1, right=0.65)

signal_line, = ax.plot(x, np.zeros_like(x), label='Poisson × Gaussians', color='k')
peak_dots, = ax.plot([], [], 'ro', label='Gaussian Peaks')
poisson_envelope_line, = ax.plot([], [], 'r--', label='Poisson Envelope')

ax.set_title("Poisson Envelope × Sum of Gaussians")
ax.set_ylim(0, 1.2)
ax.set_xlabel("x")
ax.set_ylabel("Amplitude")
ax.grid()
ax.legend()

# --- Create sliders on the right ---
slider_height = 0.03
slider_spacing = 0.06
slider_left = 0.72
slider_width = 0.22
start_y = 0.85

def add_labeled_slider(label, index, valmin, valmax, valinit):
    ypos = start_y - index * slider_spacing
    fig.text(slider_left, ypos + 0.025, label, fontsize=9)
    ax_slider = plt.axes([slider_left, ypos, slider_width, slider_height])
    return Slider(ax_slider, '', valmin, valmax, valinit=valinit)

# Slider definitions
num_slider = add_labeled_slider('Num Gaussians', 0, 1, max_gaussians, n_gauss_init)
center_slider = add_labeled_slider('Center of Peaks', 1, 0, 15, center_init)
spacing_slider = add_labeled_slider('Spacing Between Peaks', 2, 0.1, 3.0, spacing_init)
lambda_slider = add_labeled_slider('Poisson λ (mean)', 3, 0.1, max_gaussians, lambda_init)

# Set initial integer display
num_slider.valtext.set_text(f"{int(num_slider.val)}")

# --- Update function ---
def update(val):
    n = int(round(num_slider.val))
    num_slider.valtext.set_text(f"{n}")  # Show integer in slider display

    peak_center = center_slider.val
    spacing = spacing_slider.val
    lam = lambda_slider.val

    # Compute peak positions
    if n % 2 == 1:
        offset_range = np.arange(-(n // 2), n // 2 + 1)
    else:
        offset_range = np.linspace(-(n - 1) / 2, (n - 1) / 2, n)

    peak_positions = peak_center + spacing * offset_range
    shifted_indices = np.arange(len(peak_positions))
    poisson_amplitudes = poisson.pmf(shifted_indices, mu=lam)

    # Composite signal of Gaussians
    base = np.zeros_like(x)
    peak_values = []

    for mu, A in zip(peak_positions, poisson_amplitudes):
        g = gaussian(x, mu, narrow_sigma, A)
        base += g
        peak_values.append(A)

    # Update lines
    signal_line.set_ydata(base)
    peak_dots.set_data(peak_positions, peak_values)
    # Interpolate a smooth Poisson envelope
    interp = interp1d(peak_positions, poisson_amplitudes, kind='quadratic', bounds_error=False, fill_value=0)
    envelope_smooth = interp(x)
    poisson_envelope_line.set_data(x, envelope_smooth)

    y_max = max(np.max(base), np.max(poisson_amplitudes))
    ax.set_ylim(0, y_max * 1.1)
    fig.canvas.draw_idle()

# --- Connect sliders ---
for s in [num_slider, center_slider, spacing_slider, lambda_slider]:
    s.on_changed(update)

# --- Initial draw ---
update(None)
plt.show()

