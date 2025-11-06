"""
sim_ommatidia.py

Simulate two neighboring ommatidia (eccentric cells) with light-driven input
and synaptic coupling in NEURON (Python interface).

Outputs: voltages.json with records:
    [{"time": 0.0, "v1": -65.0, "v2": -65.0, "norm_v1": 0.0, "norm_v2": 0.0}, ...]
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

# Synapse parameters (chemical, presynaptic spike -> postsynaptic ExpSyn)
syn_tau = 2.0        # ms (ExpSyn tau)
netcon_weight = 0.05 # uS (synaptic weight)
netcon_delay = 1.0   # ms

# Light stimulus parameters (Gaussian pulses)
# Simulate ONE bright light source hitting both ommatidia to demonstrate lateral inhibition
light_amp_peak = 0.5  # nA peak of injected current per photostimulus
light_width = 8.0     # ms (sigma of Gaussian)
pulse_times = [50.0, 120.0]  # times when light pulses occur
# Cell1 is directly illuminated (strong), Cell2 is nearby (moderate intensity)

# Output files
out_filename = "voltages.json"
light_filename = "light_stimuli.json"

# -----------------------
# Helper functions
# -----------------------
def gaussian_time_series(t_array, peak_time, peak_amp, width):
    """Return an array of current amplitudes for times t_array (ms) representing a Gaussian pulse."""
    return peak_amp * np.exp(-0.5 * ((t_array - peak_time) / width) ** 2)


# -----------------------
# Build two cells (one-compartment soma-like sections)
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
        self.t_vec = h.Vector()
        self.v_vec.record(s(0.5)._ref_v)
        # time recorded only by one cell later

        # For spike detection (for NetCon)
        self.spike_detector = h.NetCon(s(0.5)._ref_v, None, sec=s)
        # create NetCon later when connecting to target
        self.spike_detector.threshold = 0.0  # mV spike threshold (adjustable)

    def set_spike_threshold(self, thresh_mV):
        self.spike_detector.threshold = thresh_mV

# instantiate two cells
cell1 = EccentricCell('ecc1')
cell2 = EccentricCell('ecc2')

# -----------------------
# Synaptic coupling: from cell1 -> cell2 and cell2 -> cell1 (bidirectional chemical)
# -----------------------
# Create ExpSyn at each target
syn_12 = h.ExpSyn(cell2.sec(0.5))  # synapse on cell2 from cell1
syn_12.tau = syn_tau
syn_21 = h.ExpSyn(cell1.sec(0.5))  # synapse on cell1 from cell2
syn_21.tau = syn_tau

# Create NetCon objects that watch spikes on presyn cell and drive target synapse
nc_1to2 = h.NetCon(cell1.sec(0.5)._ref_v, syn_12, sec=cell1.sec)
nc_1to2.threshold = 0.0
nc_1to2.delay = netcon_delay
nc_1to2.weight[0] = netcon_weight

nc_2to1 = h.NetCon(cell2.sec(0.5)._ref_v, syn_21, sec=cell2.sec)
nc_2to1.threshold = 0.0
nc_2to1.delay = netcon_delay
nc_2to1.weight[0] = netcon_weight

# optionally set spike thresholds more depolarized if using hh that spikes widely
cell1.set_spike_threshold(0.0)
cell2.set_spike_threshold(0.0)

# -----------------------
# Construct time series for IClamp amplitudes (light-driven)
# -----------------------
times = np.arange(0.0, tstop + dt, dt)  # ms
I1 = np.zeros_like(times)
I2 = np.zeros_like(times)

# Single light source hitting both ommatidia simultaneously
# Cell1 receives strong direct illumination, Cell2 receives moderate nearby illumination
for pt in pulse_times:
    I1 += gaussian_time_series(times, pt, light_amp_peak, light_width)  # strong, direct
    I2 += 0.7 * gaussian_time_series(times, pt, light_amp_peak, light_width)  # moderate, nearby

# This pattern demonstrates lateral inhibition: the strongly activated cell1
# will inhibit cell2 through synaptic coupling, suppressing its response.

# Convert to NEURON vectors and play into IClamp amplitude
vec_t = h.Vector(times.tolist())
vec_i1 = h.Vector(I1.tolist())
vec_i2 = h.Vector(I2.tolist())

# play amps into the IClamp 'amp' variable over time
# Vector.play(target, delta=0.0, continuous=0/1) expects a reference, use the amp attribute
vec_i1.play(cell1.iclamp._ref_amp, vec_t, 1)  # 1 for continuous interpolation
vec_i2.play(cell2.iclamp._ref_amp, vec_t, 1)

# Record time once (we'll use same time vector)
time_vec = h.Vector()
time_vec.record(h._ref_t)

# -----------------------
# Run the simulation
# -----------------------
print("Running simulation: tstop={} ms, dt={} ms".format(tstop, dt))
h.finitialize(e_pas)
h.continuerun(tstop)
print("Simulation complete.")

# -----------------------
# Extract recorded data
# -----------------------
t = np.array(time_vec)
v1 = np.array(cell1.v_vec)
v2 = np.array(cell2.v_vec)

# Basic sanity check lengths
n = min(len(t), len(v1), len(v2))
t = t[:n]
v1 = v1[:n]
v2 = v2[:n]

# -----------------------
# Normalize voltages for visualization (0..1)
# -----------------------
# Use global min/max across both traces to get consistent color mapping
vmin = min(v1.min(), v2.min())
vmax = max(v1.max(), v2.max())
if vmax == vmin:
    norm_v1 = np.zeros_like(v1)
    norm_v2 = np.zeros_like(v2)
else:
    norm_v1 = (v1 - vmin) / (vmax - vmin)
    norm_v2 = (v2 - vmin) / (vmax - vmin)

# Clamp 0..1 to be safe
norm_v1 = np.clip(norm_v1, 0.0, 1.0)
norm_v2 = np.clip(norm_v2, 0.0, 1.0)

# -----------------------
# Export to JSON for Three.js
# -----------------------
records = []
for i_time in range(n):
    records.append({
        "time": float(t[i_time]),
        "v1": float(v1[i_time]),
        "v2": float(v2[i_time]),
        "norm_v1": float(norm_v1[i_time]),
        "norm_v2": float(norm_v2[i_time])
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
        "i1": float(I1[i_time]),
        "i2": float(I2[i_time])
    })

with open(light_filename, "w") as f:
    json.dump(light_records, f, indent=2)

print(f"Wrote {len(light_records)} light stimulus records to {light_filename}")

# Optional: quick matplotlib plot if matplotlib is available (comment out if not desired)
try:
    import matplotlib.pyplot as plt
    plt.figure(figsize=(8,4))
    plt.plot(t, v1, label='v1 (ecc1)')
    plt.plot(t, v2, label='v2 (ecc2)')
    plt.xlabel('time (ms)')
    plt.ylabel('membrane potential (mV)')
    plt.legend()
    plt.title('Eccentric cell voltages')
    plt.tight_layout()
    plt.show()
except Exception:
    pass
