"""
sim_single_ommatidium.py

Simulate a single ommatidium (eccentric cell) with light-driven input
in NEURON (Python interface). This provides a baseline for comparison
with the two-cell lateral inhibition simulation.

Outputs: voltages_single.json with records:
    [{"time": 0.0, "v": -65.0, "norm_v": 0.0}, ...]
"""

import json
import math
import numpy as np
from neuron import h, gui  # gui import optional but helpful in interactive runs

# -----------------------
# Simulation parameters
# -----------------------
tstop = 200.0        # ms, total simulation time
dt = 0.025           # ms, simulation time step
h.dt = dt
h.tstop = tstop

# Biophysical parameters
cm = 1.0             # uF/cm2
Ra = 100.0           # ohm*cm
g_pas = 1e-4         # passive leak conductance (S/cm2), small
e_pas = -65.0        # leak reversal (mV)

# HH (spiking) settings
use_hh = True

# Light stimulus parameters (Gaussian pulses)
# Same as cell1 from the two-cell simulation for direct comparison
light_amp_peak = 0.5  # nA peak of injected current per photostimulus
light_width = 8.0     # ms (sigma of Gaussian)
pulse_times = [50.0, 120.0]  # times when light pulses occur

# Output files
out_filename = "voltages_single.json"
light_filename = "light_stimuli_single.json"

# -----------------------
# Helper functions
# -----------------------
def gaussian_time_series(t_array, peak_time, peak_amp, width):
    """Return an array of current amplitudes for times t_array (ms) representing a Gaussian pulse."""
    return peak_amp * np.exp(-0.5 * ((t_array - peak_time) / width) ** 2)


# -----------------------
# Build single cell (one-compartment soma-like section)
# -----------------------
class EccentricCell:
    def __init__(self, name):
        self.name = name
        self.sec = h.Section(name=name)
        s = self.sec
        s.L = 20.0      # um
        s.diam = 20.0   # um (roughly spherical compartment)
        s.cm = cm
        s.Ra = Ra

        # Insert passive leak; optionally HH
        s.insert('pas')
        for seg in s:
            seg.pas.g = g_pas
            seg.pas.e = e_pas

        if use_hh:
            s.insert('hh')
            # default hh parameters will produce spiking behavior in many cases

        # IClamp for light-driven current (we will drive its amplitude over time)
        self.iclamp = h.IClamp(s(0.5))
        self.iclamp.delay = 0.0
        self.iclamp.dur = 1e9  # we'll control amplitude via Vector.play(), so set huge duration
        # start with 0 amplitude
        self.iclamp.amp = 0.0

        # Recording vectors
        self.v_vec = h.Vector()
        self.v_vec.record(s(0.5)._ref_v)

# instantiate single cell
cell = EccentricCell('ecc_single')

# -----------------------
# Construct time series for IClamp amplitude (light-driven)
# -----------------------
times = np.arange(0.0, tstop + dt, dt)  # ms
I = np.zeros_like(times)

# Add Gaussian pulses at specified times
for pt in pulse_times:
    I += gaussian_time_series(times, pt, light_amp_peak, light_width)

# Convert to NEURON vectors and play into IClamp amplitude
vec_t = h.Vector(times.tolist())
vec_i = h.Vector(I.tolist())

# play amps into the IClamp 'amp' variable over time
vec_i.play(cell.iclamp._ref_amp, vec_t, 1)  # 1 for continuous interpolation

# Record time
time_vec = h.Vector()
time_vec.record(h._ref_t)

# -----------------------
# Run the simulation
# -----------------------
print("Running single ommatidium simulation: tstop={} ms, dt={} ms".format(tstop, dt))
h.finitialize(e_pas)
h.continuerun(tstop)
print("Simulation complete.")

# -----------------------
# Extract recorded data
# -----------------------
t = np.array(time_vec)
v = np.array(cell.v_vec)

# Basic sanity check lengths
n = min(len(t), len(v))
t = t[:n]
v = v[:n]

# -----------------------
# Normalize voltages for visualization (0..1)
# -----------------------
vmin = v.min()
vmax = v.max()
if vmax == vmin:
    norm_v = np.zeros_like(v)
else:
    norm_v = (v - vmin) / (vmax - vmin)

# Clamp 0..1 to be safe
norm_v = np.clip(norm_v, 0.0, 1.0)

# -----------------------
# Export to JSON for Three.js
# -----------------------
records = []
for i_time in range(n):
    records.append({
        "time": float(t[i_time]),
        "v": float(v[i_time]),
        "norm_v": float(norm_v[i_time])
    })

with open(out_filename, "w") as f:
    json.dump(records, f, indent=2)

print(f"Wrote {len(records)} records to {out_filename}")
print("Voltage range: vmin={:.2f} mV, vmax={:.2f} mV".format(vmin, vmax))

# -----------------------
# Export light stimuli to separate JSON
# -----------------------
light_records = []
for i_time in range(n):
    light_records.append({
        "time": float(t[i_time]),
        "i": float(I[i_time])
    })

with open(light_filename, "w") as f:
    json.dump(light_records, f, indent=2)

print(f"Wrote {len(light_records)} light stimulus records to {light_filename}")

# Optional: quick matplotlib plot if matplotlib is available (comment out if not desired)
try:
    import matplotlib.pyplot as plt
    plt.figure(figsize=(8,4))
    plt.plot(t, v, label='v (single ecc)', color='blue')
    plt.xlabel('time (ms)')
    plt.ylabel('membrane potential (mV)')
    plt.legend()
    plt.title('Single eccentric cell voltage (baseline)')
    plt.tight_layout()
    plt.show()
except Exception:
    pass
