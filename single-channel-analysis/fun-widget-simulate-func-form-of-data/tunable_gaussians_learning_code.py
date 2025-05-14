import matplotlib
matplotlib.use('TkAgg')  # For PyCharm interactivity

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# --- X domain and default parameters ---
x = np.linspace(-10, 10, 1000)

# Envelope parameters
envelope_mu_init = 0.0
envelope_sigma_init = 5.0
envelope_amp = 1.0

# Narrow Gaussians
narrow_sigma = 0.3
max_gaussians = 9
n_gauss_init = 5

center_init = 0.0
spacing_init = 1.0

# --- Gaussian functions ---
def gaussian(x, mu, sigma, A):
    return A * np.exp(- (x - mu) ** 2 / (2 * sigma ** 2))

def gaussian_envelope(x, mu, sigma):
    return envelope_amp * np.exp(- (x - mu) ** 2 / (2 * sigma ** 2))

# --- Setup plot with space for sliders on the right ---
fig, ax = plt.subplots(figsize=(10, 6))
plt.subplots_adjust(left=0.1, right=0.65)

signal_line, = ax.plot(x, np.zeros_like(x), label='Envelope × Peaks',color='k')
envelope_line, = ax.plot(x, gaussian_envelope(x, envelope_mu_init, envelope_sigma_init), 'r-.', label='Envelope (dotted)')

ax.set_title("Gaussian Envelope × Sum of Gaussians")
ax.set_ylim(0, 1.2)
ax.set_xlabel("x")
ax.set_ylabel("Amplitude")
ax.grid()
ax.legend()

# --- Create sliders on the right with labels above ---
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

num_slider = add_labeled_slider('Num Gaussians', 0, 1, max_gaussians, n_gauss_init)
env_mu_slider = add_labeled_slider('Envelope Center (μ)', 1, -10, 10, envelope_mu_init)
env_sigma_slider = add_labeled_slider('Envelope Width (σ)', 2, 0.5, 10.0, envelope_sigma_init)
center_slider = add_labeled_slider('Center of Peaks', 3, -10, 10, center_init)
spacing_slider = add_labeled_slider('Spacing Between Peaks', 4, 0.1, 5.0, spacing_init)

# --- Update plot ---
def update(val):
    n = int(num_slider.val)
    mu_env = env_mu_slider.val
    sigma_env = env_sigma_slider.val
    peak_center = center_slider.val
    spacing = spacing_slider.val

    if n % 2 == 1:
        offset_range = np.arange(-(n // 2), n // 2 + 1)
    else:
        offset_range = np.linspace(-(n - 1) / 2, (n - 1) / 2, n)

    peak_positions = peak_center + spacing * offset_range

    env = gaussian_envelope(x, mu_env, sigma_env)

    base = np.zeros_like(x)
    for mu in peak_positions:
        A = gaussian(mu, mu_env, sigma_env, envelope_amp)
        base += gaussian(x, mu, narrow_sigma, A)

    total = base
    signal_line.set_ydata(total)
    envelope_line.set_ydata(env)
    ax.set_ylim(0, np.max(total) * 1.1)
    fig.canvas.draw_idle()

# --- Connect sliders ---
for s in [num_slider, env_mu_slider, env_sigma_slider, center_slider, spacing_slider]:
    s.on_changed(update)

# --- Initial draw ---
update(None)
plt.show()
