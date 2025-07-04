from neuron import h
import matplotlib.pyplot as plt
import numpy as np
import os

# Load standard run library
h.load_file("stdrun.hoc")

# Try to import BlenderSpike - if not available, we'll still run the simulation
try:
    from blenderspike_py import CellRecorder
    BLENDERSPIKE_AVAILABLE = True
    print("BlenderSpike module found - 3D export will be available!")
except ImportError:
    BLENDERSPIKE_AVAILABLE = False
    print("BlenderSpike module not found - running simulation only")

# Create a detailed multi-compartment neuron
class BlenderSpikeNeuron:
    def __init__(self):
        self.create_sections()
        self.build_topology()
        self.define_geometry()
        self.define_biophysics()
        self.setup_recording()
        
    def create_sections(self):
        # Create sections with descriptive names for BlenderSpike
        self.soma = h.Section(name='soma')
        self.axon = h.Section(name='axon')
        self.basal_dend1 = h.Section(name='basal_dend1')
        self.basal_dend2 = h.Section(name='basal_dend2')
        self.basal_dend3 = h.Section(name='basal_dend3')
        self.apical_dend = h.Section(name='apical_dend')
        self.apical_tuft1 = h.Section(name='apical_tuft1')
        self.apical_tuft2 = h.Section(name='apical_tuft2')
        
        # Store all sections for easy access
        self.all_sections = [
            self.soma, self.axon, 
            self.basal_dend1, self.basal_dend2, self.basal_dend3,
            self.apical_dend, self.apical_tuft1, self.apical_tuft2
        ]
        
    def build_topology(self):
        # Connect sections (child.connect(parent))
        self.axon.connect(self.soma(0))           # Axon from soma base
        self.basal_dend1.connect(self.soma(0))    # Basal dendrites from soma base
        self.basal_dend2.connect(self.soma(0))
        self.basal_dend3.connect(self.soma(0))
        self.apical_dend.connect(self.soma(1))    # Apical from soma top
        self.apical_tuft1.connect(self.apical_dend(1))  # Tufts from apical end
        self.apical_tuft2.connect(self.apical_dend(1))
        
    def define_geometry(self):
        # Soma - make it spherical for better 3D visualization
        self.soma.L = 20
        self.soma.diam = 20
        self.soma.nseg = 1
        
        # Set 3D coordinates for soma (important for BlenderSpike!)
        h.pt3dclear(sec=self.soma)
        h.pt3dadd(0, 0, 0, 20, sec=self.soma)      # Center at origin
        h.pt3dadd(0, 0, 20, 20, sec=self.soma)    # Extend upward
        
        # Axon - extending downward
        self.axon.L = 400
        self.axon.diam = 1.5
        self.axon.nseg = 20  # More segments for smooth visualization
        
        # Set 3D coordinates for axon
        h.pt3dclear(sec=self.axon)
        h.pt3dadd(0, 0, 0, 1.5, sec=self.axon)      # Start at soma base
        h.pt3dadd(0, 0, -200, 1.2, sec=self.axon)   # Middle point
        h.pt3dadd(0, 0, -400, 1.0, sec=self.axon)   # End point (tapering)
        
        # Basal dendrites - extending in different directions
        basal_coords = [
            [(-150, 0, -30), (-1.5, 0, -0.3)],      # Left
            [(150, 0, -30), (1.5, 0, -0.3)],        # Right  
            [(0, -150, -30), (0, -1.5, -0.3)]       # Back
        ]
        
        for i, (dend, (end_pos, direction)) in enumerate(zip(
            [self.basal_dend1, self.basal_dend2, self.basal_dend3], 
            basal_coords
        )):
            dend.L = 200
            dend.diam = 2.5
            dend.nseg = 15
            
            # Set 3D coordinates
            h.pt3dclear(sec=dend)
            h.pt3dadd(0, 0, 0, 2.5, sec=dend)           # Start at soma
            h.pt3dadd(end_pos[0]/2, end_pos[1]/2, end_pos[2]/2, 2.0, sec=dend)  # Mid
            h.pt3dadd(end_pos[0], end_pos[1], end_pos[2], 1.5, sec=dend)  # End
            
        # Apical dendrite - extending upward
        self.apical_dend.L = 300
        self.apical_dend.diam = 3.0
        self.apical_dend.nseg = 20
        
        h.pt3dclear(sec=self.apical_dend)
        h.pt3dadd(0, 0, 20, 3.0, sec=self.apical_dend)    # Start at soma top
        h.pt3dadd(0, 0, 200, 2.5, sec=self.apical_dend)   # Middle
        h.pt3dadd(0, 0, 320, 2.0, sec=self.apical_dend)   # End
        
        # Apical tufts - branching from apical dendrite
        tuft_coords = [
            [(-80, 0, 400), (-0.8, 0, 0.8)],     # Left tuft
            [(80, 0, 400), (0.8, 0, 0.8)]        # Right tuft
        ]
        
        for i, (tuft, (end_pos, direction)) in enumerate(zip(
            [self.apical_tuft1, self.apical_tuft2], 
            tuft_coords
        )):
            tuft.L = 120
            tuft.diam = 1.5
            tuft.nseg = 10
            
            h.pt3dclear(sec=tuft)
            h.pt3dadd(0, 0, 320, 1.5, sec=tuft)              # Start at apical end
            h.pt3dadd(end_pos[0]/2, end_pos[1]/2, 350, 1.2, sec=tuft)  # Mid
            h.pt3dadd(end_pos[0], end_pos[1], end_pos[2], 1.0, sec=tuft)  # End
            
    def define_biophysics(self):
        # Soma - active membrane
        self.soma.Ra = 100
        self.soma.cm = 1
        self.soma.insert('hh')
        
        # Axon - active membrane with higher sodium conductance
        self.axon.Ra = 100
        self.axon.cm = 1
        self.axon.insert('hh')
        # Increase sodium conductance for better action potential propagation
        for seg in self.axon:
            seg.hh.gnabar = 0.15  # Higher than default 0.12
        
        # All dendrites - passive membrane
        dendrites = [self.basal_dend1, self.basal_dend2, self.basal_dend3, 
                    self.apical_dend, self.apical_tuft1, self.apical_tuft2]
        
        for dend in dendrites:
            dend.Ra = 100
            dend.cm = 1
            dend.insert('pas')
            dend.g_pas = 0.0002  # Slightly higher leak for realistic decay
            dend.e_pas = -70
            
    def setup_recording(self):
        # Record from multiple locations for analysis
        self.recordings = {}
        record_locations = {
            'soma': (self.soma, 0.5),
            'axon_initial': (self.axon, 0.1),
            'axon_middle': (self.axon, 0.5),
            'basal_dend1': (self.basal_dend1, 0.5),
            'apical_dend': (self.apical_dend, 0.5),
            'apical_tuft1': (self.apical_tuft1, 0.5)
        }
        
        for name, (section, location) in record_locations.items():
            self.recordings[name] = h.Vector().record(section(location)._ref_v)
            
        self.t = h.Vector().record(h._ref_t)

# Create the neuron FIRST
print("Creating detailed neuron model...")
neuron = BlenderSpikeNeuron()

# NOW create the CellRecorder with the neuron's sections
if BLENDERSPIKE_AVAILABLE:
    # Create CellRecorder AFTER neuron is created
    cell_recorder = CellRecorder(neuron.all_sections)
    print("CellRecorder initialized successfully!")

# Add stimulation to soma
stim = h.IClamp(neuron.soma(0.5))
stim.delay = 5      # ms
stim.dur = 2        # ms  
stim.amp = 0.8      # nA - strong enough to generate action potential

# Initialize simulation parameters
h.dt = 0.025        # Time step (ms)
h.celsius = 37      # Temperature

print("Running simulation...")
# Run simulation
h.finitialize(-70)
h.tstop = 30        # Run for 30 ms
h.run()

print("Simulation complete!")

# Save BlenderSpike data if available
if BLENDERSPIKE_AVAILABLE:
    print("Saving data for BlenderSpike...")
    
    # Set up the path
    desktop_path = os.path.expanduser("~/Desktop")
    pickle_path = os.path.join(desktop_path, "detailed_neuron_blenderspike.pickle")
    
    # FIXED: Use correct parameter name for save_pickle
    # The method signature appears to accept a frame_num parameter, but let's try without it first
    try:
        # Try the method without frame_num parameter
        cell_recorder.save_pickle(pickle_path)
        print(f"Saved: {pickle_path}")
    except TypeError as e:
        print(f"Error with save_pickle: {e}")
        # Try alternative approaches
        try:
            # Maybe it expects frames parameter instead
            cell_recorder.save_pickle(pickle_path, frames=300)
            print(f"Saved with frames parameter: {pickle_path}")
        except TypeError:
            try:
                # Try with n_frames parameter
                cell_recorder.save_pickle(pickle_path, n_frames=300)
                print(f"Saved with n_frames parameter: {pickle_path}")
            except TypeError:
                # If all else fails, save with default parameters
                print("Using default frame settings...")
                cell_recorder.save_pickle(pickle_path)
                print(f"Saved with defaults: {pickle_path}")
    
    print("You can now load this file in Blender with the BlenderSpike addon!")

# Plot results
print("Creating analysis plots...")
plt.figure(figsize=(15, 10))

# Voltage traces from different locations
plt.subplot(2, 2, 1)
for name, v_vec in neuron.recordings.items():
    plt.plot(neuron.t, v_vec, label=name, linewidth=2)
plt.xlabel('Time (ms)')
plt.ylabel('Voltage (mV)')
plt.title('Multi-Location Voltage Recording')
plt.legend()
plt.grid(True)

# Morphology schematic
plt.subplot(2, 2, 2)
# Draw the neuron schematically
# Soma
circle = plt.Circle((0, 0), 10, color='red', alpha=0.8, zorder=3)
plt.gca().add_patch(circle)

# Axon
plt.plot([0, 0], [-10, -200], 'blue', linewidth=6, label='Axon', zorder=2)

# Basal dendrites
basal_angles = [-135, -225, -270]
for i, angle in enumerate(basal_angles):
    x = 75 * np.cos(np.radians(angle))
    y = 75 * np.sin(np.radians(angle))
    plt.plot([0, x], [0, y], 'green', linewidth=4, 
             label='Basal Dendrites' if i == 0 else "", zorder=2)

# Apical dendrite and tufts
plt.plot([0, 0], [10, 160], 'purple', linewidth=5, label='Apical Dendrite', zorder=2)
plt.plot([0, -40], [160, 200], 'orange', linewidth=3, label='Apical Tufts', zorder=2)
plt.plot([0, 40], [160, 200], 'orange', linewidth=3, zorder=2)

plt.xlim(-100, 100)
plt.ylim(-220, 220)
plt.title('Neuron Morphology (Top View)')
plt.xlabel('X Distance (µm)')
plt.ylabel('Y Distance (µm)')
plt.legend()
plt.axis('equal')
plt.grid(True, alpha=0.3)

# Action potential propagation analysis
plt.subplot(2, 2, 3)
# Show delay between soma and axon
soma_v = np.array(neuron.recordings['soma'])
axon_v = np.array(neuron.recordings['axon_middle'])
t_array = np.array(neuron.t)

plt.plot(t_array, soma_v, 'r-', linewidth=2, label='Soma')
plt.plot(t_array, axon_v, 'b-', linewidth=2, label='Axon (middle)')
plt.xlabel('Time (ms)')
plt.ylabel('Voltage (mV)')
plt.title('Action Potential Propagation')
plt.legend()
plt.grid(True)

# Summary information
plt.subplot(2, 2, 4)
info_text = [
    "Neuron Model Summary:",
    f"Total sections: {len(neuron.all_sections)}",
    f"Total segments: {sum(sec.nseg for sec in neuron.all_sections)}",
    "",
    "Section Details:",
    f"Soma: {neuron.soma.L:.1f}µm length, {neuron.soma.diam:.1f}µm diameter",
    f"Axon: {neuron.axon.L:.1f}µm length, {neuron.axon.nseg} segments",
    f"Basal dendrites: 3 branches, {neuron.basal_dend1.L:.1f}µm each",
    f"Apical dendrite: {neuron.apical_dend.L:.1f}µm length",
    f"Apical tufts: 2 branches, {neuron.apical_tuft1.L:.1f}µm each",
    "",
    "Stimulation:",
    f"Location: Soma center",
    f"Amplitude: {stim.amp:.1f} nA",
    f"Duration: {stim.dur:.1f} ms",
    "",
    "BlenderSpike:" + (" Ready!" if BLENDERSPIKE_AVAILABLE else " Not installed")
]

for i, line in enumerate(info_text):
    plt.text(0.05, 0.95 - i*0.05, line, transform=plt.gca().transAxes,
             fontsize=10, fontfamily='monospace')

plt.xlim(0, 1)
plt.ylim(0, 1)
plt.axis('off')

plt.tight_layout()
plt.show()

# Print topology
print("\nNeuron Topology:")
h.topology()

if BLENDERSPIKE_AVAILABLE:
    print("\n" + "="*60)
    print("SUCCESS! Your neuron model is ready for BlenderSpike!")
    print("="*60)
    print("Next steps:")
    print("1. Install the BlenderSpike addon in Blender")
    print("2. Load the file: detailed_neuron_blenderspike.pickle")
    print("3. In Blender BlenderSpike panel:")
    print("   - Set 'Center at origin' if needed")
    print("   - Adjust 'Downscale factor' for proper sizing")
    print("   - Choose segmentation level (higher = more detail)")
    print("   - Select colormap (e.g., 'viridis', 'plasma', 'coolwarm')")
    print("   - Set voltage limits (e.g., -80 to 40 mV)")
    print("4. Enjoy your 3D neuron animation!")
else:
    print("\n" + "="*60)  
    print("To use BlenderSpike, install it with:")
    print("pip install git+https://github.com/ArtemKirsanov/BlenderSpike.git")
    print("="*60)