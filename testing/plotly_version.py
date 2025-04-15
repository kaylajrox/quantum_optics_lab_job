import numpy as np
import plotly.graph_objects as go

# --- Constants ---
x = np.linspace(-10, 10, 1000)
envelope_amp = 1.0
narrow_sigma = 0.3

# --- Functions ---
def gaussian(x, mu, sigma, A):
    return A * np.exp(- (x - mu) ** 2 / (2 * sigma ** 2))

def gaussian_envelope(x, mu, sigma):
    return envelope_amp * np.exp(- (x - mu) ** 2 / (2 * sigma ** 2))

def generate_data(n, mu_env, sigma_env, center, spacing):
    if n % 2 == 1:
        offsets = np.arange(-(n // 2), n // 2 + 1)
    else:
        offsets = np.linspace(-(n - 1) / 2, (n - 1) / 2, n)

    peak_positions = center + spacing * offsets
    env = gaussian_envelope(x, mu_env, sigma_env)
    signal = np.zeros_like(x)

    annotations = []
    for mu in peak_positions:
        A = gaussian(mu, mu_env, sigma_env, envelope_amp)
        g = gaussian(x, mu, narrow_sigma, A)
        signal += g

        annotations.append(dict(
            x=mu, y=gaussian(mu, mu, narrow_sigma, A),
            xref='x', yref='y',
            showarrow=True, arrowhead=2,
            ax=0, ay=-30,
            text=f"x = {mu:.2f}"
        ))

    return signal, env, annotations, peak_positions

# --- Initial Parameters ---
params = dict(n=5, mu_env=0.0, sigma_env=5.0, center=0.0, spacing=1.0)
signal, env, annotations, peaks = generate_data(**params)

# --- Create Plot ---
fig = go.Figure()

# Combined Signal
fig.add_trace(go.Scatter(
    x=x, y=signal, mode='lines',
    name="Envelope × Peaks", line=dict(color="black")
))

# Envelope
fig.add_trace(go.Scatter(
    x=x, y=env, mode='lines',
    name="Envelope (dotted)", line=dict(dash='dot', color="red")
))

# Peak Markers
fig.add_trace(go.Scatter(
    x=peaks, y=[gaussian(p, p, narrow_sigma, 1) for p in peaks],
    mode='markers', marker=dict(size=6, color='blue'),
    name="Peak Centers", hoverinfo='x+y'
))

fig.update_layout(
    title="Gaussian Envelope × Sum of Gaussians",
    xaxis_title="x", yaxis_title="Amplitude",
    yaxis=dict(range=[0, np.max(signal)*1.2]),
    annotations=annotations,
    margin=dict(l=40, r=40, t=40, b=40)
)

# --- Add Sliders ---
sliders = []

# We'll animate just one slider (n) for simplicity; more can be added
for n in range(1, 10):
    sig, env_, ann, pks = generate_data(n, **{k: params[k] for k in params if k != "n"})
    sliders.append(go.Frame(
        data=[
            go.Scatter(y=sig),
            go.Scatter(y=env_),
            go.Scatter(x=pks, y=[gaussian(p, p, narrow_sigma, 1) for p in pks]),
        ],
        layout=go.Layout(annotations=ann),
        name=str(n)
    ))

fig.frames = sliders

fig.update_layout(
    updatemenus=[dict(
        type='buttons',
        showactive=False,
        y=1.08,
        x=1.15,
        xanchor='right',
        yanchor='top',
        buttons=[dict(label='Play', method='animate', args=[None])]
    )],
    sliders=[{
        "steps": [
            {
                "args": [[str(n)], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate"}],
                "label": str(n),
                "method": "animate"
            }
            for n in range(1, 10)
        ],
        "x": 0.1, "xanchor": "left",
        "y": -0.15, "yanchor": "top"
    }]
)

# --- Save to offline HTML file ---
fig.write_html("gaussian_envelope_tool.html", include_plotlyjs='cdn')
print("✅ Interactive file saved as 'gaussian_envelope_tool.html'")
