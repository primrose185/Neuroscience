# neuron_to_blenderspike.py
from neuron import h
import json
# install BlenderSpike companion module in same env first:
# pip install git+https://github.com/ArtemKirsanov/BlenderSpike.git
# then:
from blenderspike_py import CellRecorder   # typical import

# --------- 1) Build morphology in NEURON (you control this part) ----------
soma = h.Section(name='soma')
dend = h.Section(name='dend')
axon = h.Section(name='axon')

# give simple 3D coordinates so BlenderSpike can position the sections in Blender
soma.pt3dadd(0, 0, 0, 20)          # x,y,z,diam
soma.pt3dadd(10, 0, 0, 20)

dend.pt3dadd(10, 0, 0, 2)
dend.pt3dadd(30, 0, 0, 2)

axon.pt3dadd(0, 0, 0, 1)
axon.pt3dadd(-50, 0, 0, 1)

# connect sections
dend.connect(soma, 1, 0)   # dend(0) to soma(1)
axon.connect(soma, 0, 0)

# basic biophysics
for sec in (soma, dend, axon):
    sec.Ra = 100
    sec.cm = 1
    sec.insert('pas')
    for seg in sec:
        seg.pas.g = 1e-4
        seg.pas.e = -65
# make soma active for spikes (optional)
soma.insert('hh')

# choose the list of sections to give to BlenderSpike
sections = [soma, dend, axon]   # you can also do: sections = list(h.allsec())

# --------- 2) Create CellRecorder BEFORE running the sim ----------
rec = CellRecorder(sections)   # creates internal h.Vector recorders for all segments

# --------- 3) (Optional) also create a local soma recorder for JSON export ----------
tvec = h.Vector()
v_soma = h.Vector()
tvec.record(h._ref_t)
v_soma.record(soma(0.5)._ref_v)

# --------- 4) Stimulate the model (model of the ommatidium -> eccentric cell) ----------
stim = h.IClamp(dend(0.5))
stim.delay = 100   # ms
stim.dur = 8000.0  # ms (8 s)
stim.amp = 0.05    # nA  -- tune this mapping to emulate "light intensities"

# --------- 5) Run ----------
h.load_file("stdrun.hoc")
h.tstop = 8200.0   # ms
h.finitialize(-65)
h.continuerun(h.tstop)   # or h.run()

# --------- 6) Export: save BlenderSpike pickle (frame count controls time-res sampling) ----------
# The README documents calling CellRecorder.save_pickle() after the sim. See README for frame args.
# We'll try a conservative, positional call. If your version uses keyword FRAME_NUM, adapt accordingly.
try:
    rec.save_pickle('limulus_cell.pickle', 400)  # (output filename, number_of_frames)
except TypeError:
    # some versions might expect a keyword or different arg name: try common alternative
    rec.save_pickle('limulus_cell.pickle', FRAME_NUM=400)  # fallback

print("Saved BlenderSpike pickle: limulus_cell.pickle")

# --------- 7) Also write a JSON of the soma trace for analysis/comparison ----------
time_ms = list(tvec)
soma_v = list(v_soma)
json_out = {
    'meta': {'sim_tstop_ms': h.tstop, 'dt_ms': h.dt},
    'time_ms': time_ms,
    'soma_voltage_mV': soma_v
}
with open('soma_trace.json', 'w') as jf:
    json.dump(json_out, jf)

print("Saved JSON trace: soma_trace.json")
