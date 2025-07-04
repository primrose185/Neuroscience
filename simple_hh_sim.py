from neuron import h
import matplotlib.pyplot as plt
import numpy as np

# Load standard run library
h.load_file("stdrun.hoc")

# Create a more complex neuron
class MultiCompartmentNeuron:
    def __init__(self):
        self.create_sections()
        self.build_topology()
        self.define_geometry()
        self.define_biophysics()
        
    def create_sections(self):
        # Create sections
        self.soma = h.Section(name='soma')
        self.axon = h.Section(name='axon')
        self.basal_dends = [h.Section(name=f'basal_dend_{i}') for i in range(3)]
        self.apical_dend = h.Section(name='apical_dend')
        self.apical_tuft = [h.Section(name=f'apical_tuft_{i}') for i in range(2)]
        
    def build_topology(self):
        # Connect sections
        self.axon.connect(self.soma(0))
        self.apical_dend.connect(self.soma(1))
        
        for dend in self.basal_dends:
            dend.connect(self.soma(0))
            
        for tuft in self.apical_tuft:
            tuft.connect(self.apical_dend(1))
            
    def define_geometry(self):
        # Soma
        self.soma.L = self.soma.diam = 18
        self.soma.nseg = 1
        
        # Axon
        self.axon.L = 300
        self.axon.diam = 1
        self.axon.nseg = 7
        
        # Basal dendrites
        for dend in self.basal_dends:
            dend.L = 200
            dend.diam = 2
            dend.nseg = 7
            
        # Apical dendrite
        self.apical_dend.L = 400
        self.apical_dend.diam = 3
        self.apical_dend.nseg = 9
        
        # Apical tuft
        for tuft in self.apical_tuft:
            tuft.L = 150
            tuft.diam = 1.5
            tuft.nseg = 5
            
    def define_biophysics(self):
        # Soma - active
        self.soma.Ra = 100
        self.soma.cm = 1
        self.soma.insert('hh')
        
        # Axon - active
        self.axon.Ra = 100
        self.axon.cm = 1
        self.axon.insert('hh')
        
        # Dendrites - passive
        all_dends = self.basal_dends + [self.apical_dend] + self.apical_tuft
        for dend in all_dends:
            dend.Ra = 100
            dend.cm = 1
            dend.insert('pas')
            dend.g_pas = 0.0001
            dend.e_pas = -70

# Create neuron
neuron = MultiCompartmentNeuron()

# Add stimulation
stim = h.IClamp(neuron.soma(0.5))
stim.delay = 5
stim.dur = 2
stim.amp = 0.3

# Record voltages
recordings = {}
sections = {'soma': neuron.soma, 'axon': neuron.axon, 
           'basal_dend_0': neuron.basal_dends[0],
           'apical_dend': neuron.apical_dend,
           'apical_tuft_0': neuron.apical_tuft[0]}

for name, sec in sections.items():
    recordings[name] = h.Vector().record(sec(0.5)._ref_v)

t = h.Vector().record(h._ref_t)

# Initialize simulation parameters
h.dt = 0.025     # Time step (ms)
h.celsius = 37   # Temperature

# Run simulation
h.finitialize(-70)  # This sets the initial voltage to -70 mV
h.tstop = 25        # Set simulation end time
h.run()             # Run the simulation

# Plotting
fig, axes = plt.subplots(2, 2, figsize=(15, 10))

# Voltage traces
ax1 = axes[0, 0]
for name, v_vec in recordings.items():
    ax1.plot(t, v_vec, label=name, linewidth=2)
ax1.set_xlabel('Time (ms)')
ax1.set_ylabel('Voltage (mV)')
ax1.set_title('Multi-Compartment Neuron Response')
ax1.legend()
ax1.grid(True)

# Manual morphology plot
ax2 = axes[0, 1]

# Draw soma
soma_circle = plt.Circle((0, 0), 9, color='red', alpha=0.8, zorder=3)
ax2.add_patch(soma_circle)

# Draw axon
ax2.plot([0, 0], [-9, -100], 'blue', linewidth=6, label='Axon', zorder=2)

# Draw basal dendrites
angles = [-120, -180, -240]  # degrees
for i, angle in enumerate(angles):
    x = 100 * np.cos(np.radians(angle))
    y = 100 * np.sin(np.radians(angle))
    ax2.plot([0, x], [0, y], 'green', linewidth=4, 
             label='Basal Dendrites' if i == 0 else "", zorder=2)

# Draw apical dendrite
ax2.plot([0, 0], [9, 200], 'purple', linewidth=5, label='Apical Dendrite', zorder=2)

# Draw apical tuft
tuft_angles = [70, 110]
for i, angle in enumerate(tuft_angles):
    x_start, y_start = 0, 200
    x_end = x_start + 75 * np.cos(np.radians(angle))
    y_end = y_start + 75 * np.sin(np.radians(angle))
    ax2.plot([x_start, x_end], [y_start, y_end], 'orange', linewidth=3,
             label='Apical Tuft' if i == 0 else "", zorder=2)

ax2.set_xlim(-120, 120)
ax2.set_ylim(-120, 300)
ax2.set_title('Detailed Neuron Morphology')
ax2.set_xlabel('Distance (µm)')
ax2.set_ylabel('Distance (µm)')
ax2.legend(loc='upper right')
ax2.set_aspect('equal')
ax2.grid(True, alpha=0.3)

# Section properties
ax3 = axes[1, 0]
properties = [
    f"{'Section':<15} {'Length':<8} {'Diameter':<8} {'Type':<10}",
    "-" * 50,
    f"{'Soma':<15} {neuron.soma.L:<8.1f} {neuron.soma.diam:<8.1f} {'Active':<10}",
    f"{'Axon':<15} {neuron.axon.L:<8.1f} {neuron.axon.diam:<8.1f} {'Active':<10}",
    f"{'Basal Dend':<15} {neuron.basal_dends[0].L:<8.1f} {neuron.basal_dends[0].diam:<8.1f} {'Passive':<10}",
    f"{'Apical Dend':<15} {neuron.apical_dend.L:<8.1f} {neuron.apical_dend.diam:<8.1f} {'Passive':<10}",
    f"{'Apical Tuft':<15} {neuron.apical_tuft[0].L:<8.1f} {neuron.apical_tuft[0].diam:<8.1f} {'Passive':<10}",
]

for i, prop in enumerate(properties):
    ax3.text(0.05, 0.9 - i*0.12, prop, fontsize=10, 
             fontfamily='monospace', transform=ax3.transAxes)

ax3.set_title('Section Properties')
ax3.axis('off')

# Topology tree
ax4 = axes[1, 1]
ax4.text(0.05, 0.9, 'Neuron Topology:', fontsize=12, fontweight='bold')
topology_text = [
    "soma",
    "├── axon",
    "├── basal_dend_0",
    "├── basal_dend_1", 
    "├── basal_dend_2",
    "└── apical_dend",
    "    ├── apical_tuft_0",
    "    └── apical_tuft_1"
]

for i, line in enumerate(topology_text):
    ax4.text(0.05, 0.8 - i*0.08, line, fontsize=10, 
             fontfamily='monospace', transform=ax4.transAxes)

ax4.set_title('Connection Tree')
ax4.axis('off')

plt.tight_layout()
plt.show()

# Print detailed topology
print("\nDetailed Neuron Topology:")
h.topology()

print(f"\nTotal sections: {sum(1 for sec in h.allsec())}")
print(f"Total segments: {sum(sec.nseg for sec in h.allsec())}")